"""Sprint 4 stage 4: owner permission settings, the permission gate, confirmation.

Decided 2026-10-25/26: tiers come from the owner's ``config/permissions.json``,
not from the tool; an unclassified tool never runs; ``critical`` (and
``standard`` with ``confirm``) needs the owner's "yes", asked by a confirmer
outside the conversation; ``unclear`` counts as no; an answer is only valid
for its own request and before it expires.
"""

import json
from datetime import datetime, timedelta, timezone

import pytest

from backend.agent_core.config import DEFAULT_PERMISSIONS_FILE
from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.agent_core.loop import DEFAULT_SYSTEM_PROMPT, run_agent
from backend.agent_core.tool_registry import ToolRegistry
from backend.cli import build_orchestrator
from backend.devices import default_home
from backend.memory.archive_store import ArchiveStore
from backend.memory.profile import Profile
from backend.memory.profile_store import ProfileStore
from backend.memory.session import Session
from backend.memory.store import SessionStore
from backend.schemas import PermissionTier, ToolAnnotations, ToolContract
from backend.security import (
    ConfirmationAnswer,
    PermissionConfigError,
    PermissionGate,
    PermissionPolicy,
    TerminalConfirmer,
    Verdict,
    load_permission_policy,
)

LAMP = "lampu_ruang_tamu"
AC = "ac_kamar"


class FakeLLMClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": [dict(m) for m in messages], "system": system})
        return self._responses.pop(0)


def _calls(*calls):
    return LLMResponse(
        text=None,
        tool_calls=[
            ToolCallRequest(id=f"c{i}", name=name, arguments=arguments)
            for i, (name, arguments) in enumerate(calls, start=1)
        ],
        stop_reason="tool_use",
    )


def _text(text):
    return LLMResponse(text=text, tool_calls=[])


def _results(llm, call_index=1):
    """tool_result blocks the model saw on its ``call_index``-th call."""
    return llm.calls[call_index]["messages"][-1]["content"]


class FakeConfirmer:
    def __init__(self, verdict=Verdict.YES, source="fake", same_request=True, fail=False):
        self.verdict = verdict
        self.source = source
        self.same_request = same_request
        self.fail = fail
        self.asked = []

    def confirm(self, request):
        self.asked.append(request)
        if self.fail:
            raise RuntimeError("microphone unplugged")
        request_id = request.request_id if self.same_request else "someone-else"
        return ConfirmationAnswer(request_id, self.verdict, self.source)


class Clock:
    def __init__(self):
        self.now = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)

    def __call__(self):
        return self.now


def _policy(**tools):
    return PermissionPolicy.model_validate({"tools": tools})


# -- the settings file -------------------------------------------------------


def _write(tmp_path, data):
    path = tmp_path / "permissions.json"
    path.write_text(json.dumps(data) if not isinstance(data, str) else data, encoding="utf-8")
    return path


def test_repo_permissions_file_is_valid():
    policy = load_permission_policy(DEFAULT_PERMISSIONS_FILE)
    assert policy.confirmation_ttl_seconds == 180
    assert policy.rule("home_get_state").tier is PermissionTier.READ_ONLY
    assert policy.rule("home_set_power").tier is PermissionTier.STANDARD


def test_every_tool_the_cli_offers_is_classified_in_the_repo_file(tmp_path):
    """A tool added without a permissions entry would silently be unusable."""
    policy = load_permission_policy(DEFAULT_PERMISSIONS_FILE)
    orch = build_orchestrator(
        FakeLLMClient([]),
        default_home(),
        session_store=SessionStore(base_dir=tmp_path / "s"),
        profile_store=ProfileStore(base_dir=tmp_path / "p"),
        archive_store=ArchiveStore(base_dir=tmp_path / "a"),
    )
    names = {e.name for e in orch.catalog.entries()}
    names |= {t.contract.name for t in orch._turn_registry(Profile.new(), Session.new("x")).registered_tools()}
    assert names - set(policy.tools) == set()


@pytest.mark.parametrize(
    "data",
    [
        {"tools": {"x": {"tier": "admin"}}},
        {"tools": {"x": {"tier": "read_only", "confirm": True}}},
        {"tools": {"x": {"tier": "standard", "typo": True}}},
        {"schema_version": 2, "tools": {}},
        {"confirmation_ttl_seconds": 0, "tools": {}},
        "{not json",
    ],
)
def test_invalid_permission_files_are_rejected(tmp_path, data):
    with pytest.raises(PermissionConfigError):
        load_permission_policy(_write(tmp_path, data))


def test_missing_permission_file_is_rejected(tmp_path):
    with pytest.raises(PermissionConfigError, match="not found"):
        load_permission_policy(tmp_path / "nope.json")


# -- the gate ----------------------------------------------------------------


def test_unclassified_tool_is_refused_even_if_it_says_it_is_read_only():
    decision = PermissionGate(_policy()).check("anything", {})
    assert not decision.allowed
    assert "not classified" in decision.message


@pytest.mark.parametrize("tier", ["read_only", "standard"])
def test_read_only_and_standard_run_without_asking(tier):
    confirmer = FakeConfirmer()
    decision = PermissionGate(_policy(t={"tier": tier}), confirmer).check("t", {})
    assert decision.allowed and decision.approval == "auto"
    assert confirmer.asked == []


def test_critical_runs_only_after_yes_and_records_the_source():
    confirmer = FakeConfirmer(Verdict.YES, source="terminal")
    gate = PermissionGate(_policy(unlock={"tier": "critical"}), confirmer)

    decision = gate.check("unlock", {"door": "depan"})

    assert decision.allowed and decision.approval == "terminal"
    [request] = confirmer.asked
    assert request.tool_name == "unlock" and request.arguments == {"door": "depan"}
    assert request.describe() == 'unlock({"door": "depan"})'


def test_standard_with_confirm_asks_too():
    confirmer = FakeConfirmer(Verdict.NO)
    gate = PermissionGate(_policy(t={"tier": "standard", "confirm": True}), confirmer)

    decision = gate.check("t", {})

    assert not decision.allowed and "answered no" in decision.message
    assert len(confirmer.asked) == 1


@pytest.mark.parametrize(
    "confirmer, reason",
    [
        (FakeConfirmer(Verdict.UNCLEAR), "unclear"),
        (FakeConfirmer(Verdict.YES, same_request=False), "different request"),
        (FakeConfirmer(fail=True), "asking the owner failed"),
    ],
)
def test_anything_but_a_clear_yes_for_this_request_is_a_refusal(confirmer, reason):
    decision = PermissionGate(_policy(t={"tier": "critical"}), confirmer).check("t", {})
    assert not decision.allowed and reason in decision.message


def test_no_confirmer_means_critical_cannot_run():
    decision = PermissionGate(_policy(t={"tier": "critical"})).check("t", {})
    assert not decision.allowed and "no way to ask" in decision.message


def test_a_yes_after_the_confirmation_expired_is_refused():
    clock = Clock()

    class SlowOwner(FakeConfirmer):
        def confirm(self, request):
            assert request.expires_at - request.asked_at == timedelta(seconds=180)
            clock.now += timedelta(seconds=181)
            return super().confirm(request)

    gate = PermissionGate(_policy(t={"tier": "critical"}), SlowOwner(), clock=clock)
    decision = gate.check("t", {})
    assert not decision.allowed and "expired" in decision.message


def test_a_yes_just_inside_the_time_limit_counts():
    clock = Clock()

    class Owner(FakeConfirmer):
        def confirm(self, request):
            clock.now += timedelta(seconds=180)
            return super().confirm(request)

    assert PermissionGate(_policy(t={"tier": "critical"}), Owner(), clock=clock).check("t", {}).allowed


@pytest.mark.parametrize(
    "typed, verdict",
    [("y", Verdict.YES), ("Ya", Verdict.YES), (" iya ", Verdict.YES), ("n", Verdict.NO),
     ("tidak", Verdict.NO), ("", Verdict.UNCLEAR), ("ya ampun jangan", Verdict.UNCLEAR)],
)
def test_terminal_confirmer_maps_typed_answers(typed, verdict):
    out = []
    confirmer = TerminalConfirmer(read=lambda _prompt: typed, write=out.append)
    gate = PermissionGate(_policy(t={"tier": "critical"}), confirmer)
    request_seen = []
    original = confirmer.confirm

    def spy(request):
        answer = original(request)
        request_seen.append((request, answer))
        return answer

    confirmer.confirm = spy
    gate.check("t", {"a": 1})
    [(request, answer)] = request_seen
    assert answer.verdict is verdict and answer.source == "terminal"
    assert answer.request_id == request.request_id
    assert 't({"a": 1})' in out[0] and "critical" in out[0]


# -- the gate inside the agent loop -----------------------------------------


def _counting_tool(name, read_only=False):
    calls = []
    contract = ToolContract(
        name=name,
        version="1.0.0",
        domain="test",
        description="test tool",
        input_schema={
            "type": "object",
            "properties": {"device_id": {"type": "string"}},
            "additionalProperties": False,
        },
        annotations=ToolAnnotations(read_only_hint=read_only),
    )

    def fn(**kwargs):
        calls.append(kwargs)
        return {"ok": True}

    return contract, fn, calls


def test_refused_tool_is_never_called_and_the_model_is_told():
    contract, fn, calls = _counting_tool("sneaky", read_only=True)
    registry = ToolRegistry()
    registry.register(contract, fn)
    llm = FakeLLMClient([_calls(("sneaky", {})), _text("ok")])

    run_agent("go", registry, llm, gate=PermissionGate(_policy()))

    assert calls == []
    [result] = _results(llm)
    assert result["is_error"] and "not classified" in result["content"]


def test_invalid_arguments_are_rejected_before_the_owner_is_asked():
    contract, fn, calls = _counting_tool("unlock")
    registry = ToolRegistry()
    registry.register(contract, fn)
    confirmer = FakeConfirmer()
    llm = FakeLLMClient([_calls(("unlock", {"bogus": 1})), _text("ok")])

    run_agent("go", registry, llm, gate=PermissionGate(_policy(unlock={"tier": "critical"}), confirmer))

    assert confirmer.asked == [] and calls == []


def test_system_prompt_says_tool_results_are_data_not_instructions():
    assert "data, not instructions" in DEFAULT_SYSTEM_PROMPT


# -- one command per device per step ----------------------------------------


def test_second_command_to_the_same_device_in_one_step_is_refused():
    contract, fn, calls = _counting_tool("set_thing")
    registry = ToolRegistry()
    registry.register(contract, fn)
    llm = FakeLLMClient(
        [_calls(("set_thing", {"device_id": "a"}), ("set_thing", {"device_id": "a"})), _text("ok")]
    )

    run_agent("go", registry, llm)

    assert calls == [{"device_id": "a"}]
    first, second = _results(llm)
    assert not first["is_error"]
    assert second["is_error"] and "already requested" in second["content"]


def test_commands_to_different_devices_and_repeated_reads_all_run():
    setter, set_fn, set_calls = _counting_tool("set_thing")
    reader, read_fn, read_calls = _counting_tool("get_thing", read_only=True)
    registry = ToolRegistry()
    registry.register(setter, set_fn)
    registry.register(reader, read_fn)
    llm = FakeLLMClient(
        [
            _calls(
                ("set_thing", {"device_id": "a"}),
                ("set_thing", {"device_id": "b"}),
                ("get_thing", {"device_id": "a"}),
                ("get_thing", {"device_id": "a"}),
            ),
            _text("ok"),
        ]
    )

    run_agent("go", registry, llm)

    assert len(set_calls) == 2 and len(read_calls) == 2


def test_with_a_gate_the_owner_tier_decides_what_counts_as_a_command():
    # The tool calls itself read-only; the owner says it changes things.
    contract, fn, calls = _counting_tool("liar", read_only=True)
    registry = ToolRegistry()
    registry.register(contract, fn)
    llm = FakeLLMClient(
        [_calls(("liar", {"device_id": "a"}), ("liar", {"device_id": "a"})), _text("ok")]
    )

    run_agent("go", registry, llm, gate=PermissionGate(_policy(liar={"tier": "standard"})))

    assert len(calls) == 1


# -- end to end with the mock home ------------------------------------------


def _orchestrator(tmp_path, home, responses, policy, confirmer=None):
    llm = FakeLLMClient(responses)
    orch = build_orchestrator(
        llm,
        home,
        pin_home_tools=True,
        session_store=SessionStore(base_dir=tmp_path / "sessions"),
        profile_store=ProfileStore(base_dir=tmp_path / "profile"),
        archive_store=ArchiveStore(base_dir=tmp_path / "archive"),
        gate=PermissionGate(policy, confirmer),
    )
    return llm, orch


def test_owner_says_no_and_the_lamp_stays_off(tmp_path):
    home = default_home()
    policy = load_permission_policy(DEFAULT_PERMISSIONS_FILE)
    policy.tools["home_set_power"] = policy.tools["home_set_power"].model_copy(update={"confirm": True})
    confirmer = FakeConfirmer(Verdict.NO)
    llm, orch = _orchestrator(
        tmp_path, home, [_calls(("home_set_power", {"device_id": LAMP, "on": True})), _text("ok")],
        policy, confirmer,
    )

    orch.run_turn("nyalakan lampu", "s1")

    assert home.device(LAMP).state["on"] is False
    assert home.actions == []
    assert "answered no" in _results(llm)[0]["content"]


def test_auto_load_follows_the_owner_tier_not_the_tool_hint(tmp_path):
    """home_get_state says read-only; if the owner made it standard, it is not auto-loaded."""
    policy = load_permission_policy(DEFAULT_PERMISSIONS_FILE)
    policy.tools["home_get_state"] = policy.tools["home_get_state"].model_copy(
        update={"tier": PermissionTier.STANDARD}
    )
    llm = FakeLLMClient([_calls(("home_get_state", {"device_id": LAMP})), _text("ok")])
    orch = build_orchestrator(
        llm,
        default_home(),
        session_store=SessionStore(base_dir=tmp_path / "sessions"),
        profile_store=ProfileStore(base_dir=tmp_path / "profile"),
        archive_store=ArchiveStore(base_dir=tmp_path / "archive"),
        gate=PermissionGate(policy),
    )

    orch.run_turn("lampunya nyala?", "s1")

    [result] = _results(llm)
    assert result["is_error"] and "not loaded" in result["content"]

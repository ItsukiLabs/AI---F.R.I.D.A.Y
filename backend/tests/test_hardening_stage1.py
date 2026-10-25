"""Stage 1 of the plan after the external AI reviews (2026-10-25).

Each test pins one fix: compaction never drops context on an empty summary,
a tool result that can't be serialized becomes a tool error, oversized
results are cut but stay valid JSON, tool error text is clipped, the step
limit is 10, Ctrl+C keeps the partial turn, local time instead of UTC, and
the profile block tells the model it is the primary source.
"""

import json
from datetime import datetime, timezone

import pytest

from backend.agent_core import loop
from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.agent_core.loop import DEFAULT_MAX_ITERATIONS, TOOL_ERROR_MAX_CHARS, run_agent
from backend.agent_core.tool_registry import ToolRegistry
from backend.agent_core.tools.time_tool import TIME_TOOL_CONTRACT, get_current_time
from backend.cli import Cli, build_orchestrator
from backend.devices import default_home
from backend.memory import CompactionError
from backend.memory.archive_store import ArchiveStore
from backend.memory.compaction import compact
from backend.memory.profile import Profile
from backend.memory.profile_store import ProfileStore
from backend.memory.session import Session
from backend.memory.store import SessionStore
from backend.orchestrator import Orchestrator
from backend.schemas import ToolContract

LAMP = "lampu_ruang_tamu"


class FakeLLMClient:
    """Scripted responses; an exception instance in the script is raised instead."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": list(messages), "tools": tools, "system": system})
        response = self._responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


def _call(name, arguments, call_id="c1"):
    return LLMResponse(
        text=None,
        tool_calls=[ToolCallRequest(id=call_id, name=name, arguments=arguments)],
        stop_reason="tool_use",
    )


def _text(text):
    return LLMResponse(text=text, tool_calls=[])


def _contract(name):
    return ToolContract(
        name=name,
        version="1.0.0",
        description=f"Test tool {name}.",
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
    )


def _registry(name, fn):
    registry = ToolRegistry()
    registry.register(_contract(name), fn)
    return registry


def _tool_result(llm_call):
    """The tool_result block the model received in a recorded call."""
    return llm_call["messages"][-1]["content"][0]


def _session_with_turns(n_pairs):
    session = Session.new("s1")
    for i in range(n_pairs):
        session.messages.append({"role": "user", "content": f"user turn {i}"})
        session.messages.append({"role": "assistant", "content": f"assistant turn {i}"})
    return session


# --- 1.1 compaction never drops context on an empty summary ---------------


@pytest.mark.parametrize("empty", [None, "", "   \n"])
def test_empty_summary_raises_and_leaves_the_session_untouched(empty):
    session = _session_with_turns(5)
    session.summary = "old summary"
    before = [dict(m) for m in session.messages]
    llm = FakeLLMClient([LLMResponse(text=empty)])

    with pytest.raises(CompactionError):
        compact(session, llm, keep_recent_messages=4)

    assert session.messages == before
    assert session.summary == "old summary"
    assert session.archived_turns == []
    assert session.compaction_count == 0


def test_summary_is_stored_stripped():
    session = _session_with_turns(5)
    compact(session, FakeLLMClient([LLMResponse(text="  ringkasan  \n")]), keep_recent_messages=4)
    assert session.summary == "ringkasan"


def test_turn_goes_on_with_full_context_and_a_warning_when_compaction_is_empty(monkeypatch):
    monkeypatch.setenv("MEMORY_COMPACTION_THRESHOLD_TOKENS", "100")
    session = _session_with_turns(5)
    session.last_input_tokens = 10_000
    llm = FakeLLMClient([LLMResponse(text=""), _text("Halo!")])

    result = run_agent("hai", ToolRegistry(), llm, session=session)

    assert result.text == "Halo!"
    assert any("compaction skipped" in w for w in result.warnings)
    assert session.compaction_count == 0
    # all ten old messages + the new user turn + the reply are still in context
    assert len(session.messages) == 12
    assert len(llm.calls[1]["messages"]) == 11


def test_orchestrator_passes_the_compaction_warning_on(tmp_path, monkeypatch):
    monkeypatch.setenv("MEMORY_COMPACTION_THRESHOLD_TOKENS", "100")
    store = SessionStore(base_dir=tmp_path / "sessions")
    session = _session_with_turns(5)
    session.last_input_tokens = 10_000
    store.save(session)
    orch = Orchestrator(
        FakeLLMClient([LLMResponse(text=None), _text("Halo!")]),
        session_store=store,
        profile_store=ProfileStore(base_dir=tmp_path / "profile"),
        archive_store=ArchiveStore(base_dir=tmp_path / "archive"),
    )

    result = orch.run_turn("hai", "s1")

    assert any("compaction skipped" in w for w in result.warnings)
    assert len(store.load("s1").messages) == 12


# --- 1.2 a result that can't be serialized is a tool error, not a crash ---


def test_non_serializable_result_becomes_a_tool_error():
    llm = FakeLLMClient([_call("weird", {}), _text("Maaf, alatnya error.")])

    result = run_agent("coba", _registry("weird", lambda: {"when": object()}), llm)

    assert result.text == "Maaf, alatnya error."
    block = _tool_result(llm.calls[1])
    assert block["is_error"] is True
    assert "could not be serialized" in block["content"]


def test_non_ascii_results_stay_readable():
    llm = FakeLLMClient([_call("nama", {}), _text("ok")])
    run_agent("coba", _registry("nama", lambda: {"ruangan": "kamar tidur — atas"}), llm)
    assert "kamar tidur — atas" in _tool_result(llm.calls[1])["content"]


# --- 1.3 oversized results are cut but stay valid JSON --------------------


def test_oversized_result_is_cut_into_valid_json(monkeypatch):
    monkeypatch.setenv("TOOL_RESULT_MAX_CHARS", "100")
    big = {"items": ["x" * 50 for _ in range(20)]}
    llm = FakeLLMClient([_call("big", {}), _text("ok")])

    run_agent("coba", _registry("big", lambda: big), llm)

    block = _tool_result(llm.calls[1])
    assert block["is_error"] is False
    payload = json.loads(block["content"])
    assert payload["truncated"] is True
    assert payload["original_chars"] == len(json.dumps(big))
    assert len(payload["preview"]) == 100


def test_oversized_string_result_is_cut_too(monkeypatch):
    monkeypatch.setenv("TOOL_RESULT_MAX_CHARS", "10")
    llm = FakeLLMClient([_call("long", {}), _text("ok")])
    run_agent("coba", _registry("long", lambda: "a" * 50), llm)
    assert json.loads(_tool_result(llm.calls[1])["content"])["preview"] == "a" * 10


def test_results_under_the_limit_are_unchanged():
    llm = FakeLLMClient([_call("small", {}), _text("ok")])
    run_agent("coba", _registry("small", lambda: {"on": True}), llm)
    assert _tool_result(llm.calls[1])["content"] == '{"on": true}'


# --- 1.4 tool error text is clipped and names the exception type ----------


def test_tool_error_names_the_type_and_is_clipped():
    def boom():
        raise RuntimeError("detail " * 500)

    llm = FakeLLMClient([_call("boom", {}), _text("ok")])
    run_agent("coba", _registry("boom", boom), llm)

    content = _tool_result(llm.calls[1])["content"]
    assert content.startswith("Tool 'boom' failed (RuntimeError): detail")
    assert len(content) < TOOL_ERROR_MAX_CHARS + 100


def test_short_device_errors_reach_the_model_whole():
    def offline():
        raise RuntimeError("Lampu Ruang Tamu is offline. Actual state read back: {'on': False}")

    llm = FakeLLMClient([_call("offline", {}), _text("ok")])
    run_agent("coba", _registry("offline", offline), llm)
    assert "Actual state read back: {'on': False}" in _tool_result(llm.calls[1])["content"]


# --- 1.6 step limit ---------------------------------------------------------


def test_default_step_limit_is_ten():
    assert DEFAULT_MAX_ITERATIONS == 10
    assert Orchestrator(FakeLLMClient([])).max_iterations == 10
    llm = FakeLLMClient([_call("t", {}, f"c{i}") for i in range(10)])
    result = run_agent("loop", _registry("t", lambda: "ok"), llm)
    assert result.exceeded_max_iterations is True
    assert result.iterations == 10


# --- 1.5 Ctrl+C keeps the partial turn --------------------------------------


def _home_orchestrator(tmp_path, responses):
    home = default_home()
    llm = FakeLLMClient(responses)
    orch = build_orchestrator(
        llm,
        home,
        session_store=SessionStore(base_dir=tmp_path / "sessions"),
        profile_store=ProfileStore(base_dir=tmp_path / "profile"),
        archive_store=ArchiveStore(base_dir=tmp_path / "archive"),
        pin_home_tools=True,
    )
    return home, orch


def test_ctrl_c_after_a_device_action_keeps_the_turn(tmp_path):
    home, orch = _home_orchestrator(
        tmp_path,
        [_call("home_set_power", {"device_id": LAMP, "on": True}), KeyboardInterrupt()],
    )

    with pytest.raises(KeyboardInterrupt):
        orch.run_turn("nyalakan lampu", "s1")

    assert home.snapshot()[LAMP]["on"] is True
    saved = SessionStore(base_dir=tmp_path / "sessions").load("s1").messages
    assert saved[-1]["role"] == "assistant"
    assert "Turn interrupted" in saved[-1]["content"][0]["text"]
    assert "KeyboardInterrupt" in saved[-1]["content"][0]["text"]


def test_cli_survives_ctrl_c_during_a_turn(tmp_path):
    home, orch = _home_orchestrator(
        tmp_path,
        [_call("home_set_power", {"device_id": LAMP, "on": True}), KeyboardInterrupt(), _text("Halo")],
    )
    out = []
    cli = Cli(orch, home, write=out.append)

    assert cli.handle("nyalakan lampu") is True
    assert any(line.startswith("[interrupted]") for line in out)
    assert cli.handle("halo") is True
    assert out[-1] == "F.R.I.D.A.Y: Halo"


# --- 1.7 local time instead of UTC ------------------------------------------


def test_configured_zone_is_used(monkeypatch):
    monkeypatch.setenv("FRIDAY_TIMEZONE", "Asia/Jakarta")
    result = get_current_time(datetime(2026, 10, 25, 17, 0, tzinfo=timezone.utc))
    assert result == {
        "iso_datetime": "2026-10-26T00:00:00+07:00",
        "timezone": "Asia/Jakarta",
        "utc_offset": "+07:00",
    }


def test_zone_with_half_hour_offset(monkeypatch):
    monkeypatch.setenv("FRIDAY_TIMEZONE", "Asia/Kolkata")
    result = get_current_time(datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert result["utc_offset"] == "+05:30"


def test_without_setting_the_os_zone_is_used(monkeypatch):
    monkeypatch.delenv("FRIDAY_TIMEZONE", raising=False)
    result = get_current_time()
    expected = datetime.now().astimezone().utcoffset()
    assert datetime.fromisoformat(result["iso_datetime"]).utcoffset() == expected
    assert result["timezone"]


def test_unknown_zone_name_fails_loudly(monkeypatch):
    monkeypatch.setenv("FRIDAY_TIMEZONE", "Mars/Olympus")
    with pytest.raises(Exception):
        get_current_time()


def test_time_contract_promises_local_time():
    assert "UTC" not in TIME_TOOL_CONTRACT.description.split("(")[0]
    assert TIME_TOOL_CONTRACT.version == "1.1.0"


# --- 1.8 the profile block is the primary source ----------------------------


def test_profile_block_says_it_is_the_primary_source():
    profile = Profile.new()
    profile.remember_fact("Suka lampu redup saat membaca", category="preference")
    block = profile.to_context_block()
    assert "primary source" in block
    assert "recall_memory only for" in block
    assert "Suka lampu redup saat membaca" in block


def test_loop_module_exposes_the_new_settings():
    # Guard against a silent rename: the CLI and docs refer to these names.
    assert hasattr(loop, "DEFAULT_MAX_ITERATIONS")
    assert hasattr(loop, "TOOL_ERROR_MAX_CHARS")

"""Sprint 3 stage 3 (2026-10-25): slow devices (pending), "which lamp?", CLI controls."""

import pytest

from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.agent_core.loop import DEFAULT_SYSTEM_PROMPT
from backend.cli import HOMES, Cli, build_orchestrator
from backend.devices import (
    CommandAccepted,
    DeviceService,
    MockHomeAdapter,
    default_home,
    two_lamp_home,
)
from backend.devices.tools import ASK_WHICH_DEVICE, PENDING_NOTE
from backend.memory.archive_store import ArchiveStore
from backend.memory.profile_store import ProfileStore
from backend.memory.store import SessionStore
from backend.schemas.device_contract import CommandStatus

LAMP = "lampu_ruang_tamu"
READING_LAMP = "lampu_baca_ruang_tamu"
AC = "ac_kamar"


class FakeLLMClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": list(messages), "tools": tools, "system": system})
        return self._responses.pop(0)


def _call(name, arguments, call_id="c1"):
    return LLMResponse(
        text=None,
        tool_calls=[ToolCallRequest(id=call_id, name=name, arguments=arguments)],
        stop_reason="tool_use",
    )


def _text(text):
    return LLMResponse(text=text, tool_calls=[])


def _tools(home):
    return {c.name: (c, fn) for c, fn in MockHomeAdapter(home).tools()}


# -- 3.1 slow devices: the mock -------------------------------------------------


def test_slow_device_applies_after_the_given_number_of_reads():
    home = default_home()
    home.make_slow(AC, 2)

    with pytest.raises(CommandAccepted):
        home.apply(AC, on=True)

    assert home.snapshot()[AC]["on"] is False
    assert home.queued() == {AC: [{"changes": {"on": True}, "reads_left": 2}]}
    home.read_state(AC)
    assert home.snapshot()[AC]["on"] is False
    home.read_state(AC)
    assert home.snapshot()[AC]["on"] is True
    assert home.queued() == {}
    assert home.actions == [{"device_id": AC, "changes": {"on": True}}]


def test_make_slow_zero_makes_the_device_normal_again():
    home = default_home()
    home.make_slow(AC, 3)
    home.make_slow(AC, 0)
    assert home.apply(AC, on=True)["on"] is True


def test_make_slow_rejects_negative_reads():
    with pytest.raises(ValueError):
        default_home().make_slow(AC, -1)


# -- 3.1 slow devices: the service ------------------------------------------------


def test_slow_command_is_pending_then_succeeds_on_a_later_read():
    home = default_home()
    service = DeviceService(home)
    service.read_state(AC)  # last known state exists
    home.make_slow(AC, 2)

    outcome = service.apply(AC, {"on": True, "target_temperature": 22})

    assert outcome.status is CommandStatus.PENDING
    assert "do not tell the user it is done" in outcome.message
    assert outcome.reported["on"] is False  # last known, not a fresh read

    first = service.read_state(AC)
    assert first.pending_operations == [outcome.operation_id]
    assert first.in_sync is False
    assert "not confirmed yet" in first.message

    second = service.read_state(AC)
    assert second.pending_operations == []
    assert second.in_sync is True and second.message is None
    settled = service.get_operation(outcome.operation_id)
    assert settled.status is CommandStatus.SUCCEEDED
    assert settled.reported["target_temperature"] == 22


def test_pending_without_any_earlier_read_has_no_reported_state():
    home = default_home()
    home.make_slow(LAMP, 1)
    outcome = DeviceService(home).apply(LAMP, {"on": True})
    assert outcome.status is CommandStatus.PENDING and outcome.reported is None


def test_unknown_operation_id():
    assert DeviceService(default_home()).get_operation("nope") is None


# -- 3.1 slow devices: the tool -----------------------------------------------------


def test_pending_command_is_not_a_tool_error_but_says_it_is_not_done():
    home = default_home()
    home.make_slow(LAMP, 1)
    _, set_power = _tools(home)["home_set_power"]

    result = set_power(device_id=LAMP, on=True)

    assert result["status"] == "pending"
    assert result["note"] == PENDING_NOTE
    assert "do not say it is done" in result["note"]


def test_pending_command_through_the_orchestrator(tmp_path):
    home = default_home()
    home.make_slow(LAMP, 1)
    llm = FakeLLMClient(
        [
            _call("home_set_power", {"device_id": LAMP, "on": True}, "c1"),
            _text("Perintah sudah dikirim, lampunya masih memproses."),
        ]
    )
    orch = build_orchestrator(
        llm,
        home,
        pin_home_tools=True,
        session_store=SessionStore(base_dir=tmp_path / "s"),
        profile_store=ProfileStore(base_dir=tmp_path / "p"),
        archive_store=ArchiveStore(base_dir=tmp_path / "a"),
    )

    orch.run_turn("nyalakan lampu ruang tamu", "s1")

    observation = llm.calls[1]["messages"][-1]["content"][0]
    assert observation["is_error"] is False
    assert '"status": "pending"' in observation["content"]
    assert home.snapshot()[LAMP]["on"] is False  # not applied yet


# -- 3.2 which lamp? ----------------------------------------------------------------


def test_two_lamp_home_has_two_lamps_in_the_living_room():
    lamps = [d for d in two_lamp_home().devices() if d.kind == "lamp"]
    assert {(d.device_id, d.room) for d in lamps} == {
        (LAMP, "ruang tamu"),
        (READING_LAMP, "ruang tamu"),
    }
    assert {d.name for d in lamps} == {"Lampu utama ruang tamu", "Lampu baca ruang tamu"}


def test_default_home_is_unchanged():
    assert [d.device_id for d in default_home().devices()] == [LAMP, AC]
    assert default_home().device(LAMP).name == "Lampu ruang tamu"


def test_every_actuator_tool_tells_the_model_to_ask_which_device():
    tools = _tools(two_lamp_home())
    actuators = [c for c, _ in tools.values() if not c.annotations.read_only_hint]
    assert {c.name for c in actuators} == {
        "home_set_power",
        "home_set_brightness",
        "home_set_target_temperature",
    }
    assert all(c.description.endswith(ASK_WHICH_DEVICE) for c in actuators)
    reads = [c for c, _ in tools.values() if c.annotations.read_only_hint]
    assert not any(ASK_WHICH_DEVICE in c.description for c in reads)


def test_both_lamps_are_named_in_the_device_choice():
    contract, _ = _tools(two_lamp_home())["home_set_power"]
    device = contract.input_schema["properties"]["device_id"]
    assert READING_LAMP in device["enum"] and LAMP in device["enum"]
    assert "Lampu baca ruang tamu" in device["description"]
    assert "Lampu utama ruang tamu" in device["description"]


def test_system_prompt_says_ask_instead_of_guess():
    assert "ask which one instead of guessing" in DEFAULT_SYSTEM_PROMPT


# -- 3.3 CLI ------------------------------------------------------------------------


def _cli(tmp_path, home, responses=()):
    out = []
    orch = build_orchestrator(
        FakeLLMClient(list(responses)),
        home,
        session_store=SessionStore(base_dir=tmp_path / "s"),
        profile_store=ProfileStore(base_dir=tmp_path / "p"),
        archive_store=ArchiveStore(base_dir=tmp_path / "a"),
    )
    return Cli(orch, home, write=out.append), out


def test_cli_slow_command_and_state_show_the_queue(tmp_path):
    home = default_home()
    cli, out = _cli(tmp_path, home)

    cli.handle(f"/slow {AC} 2")
    home.make_slow(AC, 2)  # idempotent; the CLI already did this
    with pytest.raises(CommandAccepted):
        home.apply(AC, on=True)
    cli.handle("/state")

    assert f"{AC} is slow: commands apply after 2 later read(s)" in out
    assert any(line.startswith(f"  pending {AC}:") and "2 more read(s)" in line for line in out)


@pytest.mark.parametrize(
    "line, expected",
    [
        ("/slow", "usage: /slow"),
        (f"/slow {AC} banyak", "usage: /slow"),
        ("/slow kulkas 2", "/state lists the device ids"),
        (f"/slow {AC} 0", f"{AC} is normal again"),
    ],
)
def test_cli_slow_command_errors_and_reset(tmp_path, line, expected):
    cli, out = _cli(tmp_path, default_home())
    cli.handle(line)
    assert any(expected in o for o in out)


def test_cli_home_choices():
    assert set(HOMES) == {"default", "dua-lampu"}
    assert len(HOMES["dua-lampu"]().devices()) == 3

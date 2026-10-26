"""The terminal CLI (``backend/cli.py``), driven with a scripted LLM and no real API."""

import pytest

from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.cli import Cli, build_orchestrator, format_trace, main
from backend.devices import default_home
from backend.memory.archive_store import ArchiveStore
from backend.memory.profile_store import ProfileStore
from backend.memory.store import SessionStore
from backend.registry import FIND_TOOLS_NAME

LAMP = "lampu_ruang_tamu"


class ApiDown(RuntimeError):
    pass


class FakeLLMClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def send(self, messages, tools, system):
        self.calls.append({"tools": [t["name"] for t in tools]})
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


class Harness:
    def __init__(self, tmp_path, responses, **kwargs):
        self.home = default_home()
        self.llm = FakeLLMClient(responses)
        self.out = []
        orch = build_orchestrator(
            self.llm,
            self.home,
            session_store=SessionStore(base_dir=tmp_path / "sessions"),
            profile_store=ProfileStore(base_dir=tmp_path / "profile"),
            archive_store=ArchiveStore(base_dir=tmp_path / "archive"),
            **kwargs,
        )
        self.cli = Cli(orch, self.home, write=self.out.append)

    def run(self, *lines):
        for line in lines:
            if not self.cli.handle(line):
                return False
        return True

    @property
    def text(self):
        return "\n".join(self.out)


def test_a_turn_prints_the_reply_and_the_tool_trace(tmp_path):
    h = Harness(
        tmp_path,
        [
            _call(FIND_TOOLS_NAME, {"query": "set power lamp"}, "c1"),
            _call("home_set_power", {"device_id": LAMP, "on": True}, "c2"),
            _text("Lampu ruang tamu sudah nyala."),
        ],
    )

    h.run("nyalakan lampu ruang tamu")

    assert "-> find_tools" in h.text
    assert f'-> home_set_power({{"device_id": "{LAMP}", "on": true}})' in h.text
    assert "<- [ok]" in h.text
    assert h.out[-1] == "F.R.I.D.A.Y: Lampu ruang tamu sudah nyala."
    assert h.home.snapshot()[LAMP]["on"] is True


def test_home_tools_are_discoverable_by_default_and_time_is_always_installed(tmp_path):
    h = Harness(tmp_path, [_text("Halo.")])

    h.run("halo")

    tools = h.llm.calls[0]["tools"]
    assert "get_current_time" in tools and FIND_TOOLS_NAME in tools
    assert "home_set_power" not in tools


def test_pin_home_tools_installs_them_every_turn(tmp_path):
    h = Harness(tmp_path, [_text("Halo.")], pin_home_tools=True)

    h.run("halo")

    assert "home_set_power" in h.llm.calls[0]["tools"]


def test_trace_off_hides_tool_calls(tmp_path):
    h = Harness(tmp_path, [_call("home_get_state", {"device_id": LAMP}), _text("Mati.")])

    h.run("/trace off", "lampunya nyala?")

    assert "->" not in h.text
    assert h.out[-1] == "F.R.I.D.A.Y: Mati."


def test_state_and_fail_commands_drive_the_mock_home(tmp_path):
    h = Harness(
        tmp_path,
        [_call("home_get_state", {"device_id": LAMP}), _text("Lampunya tidak merespons.")],
    )

    h.run("/state", f"/fail {LAMP} offline", "lampunya nyala?")

    assert f"{LAMP} (Lampu ruang tamu, ruang tamu)" in h.text
    assert f"next command to {LAMP} will fail: offline" in h.text
    # Since stage 2 (2026-10-25) an offline read is a stale snapshot, not a tool error.
    assert '<- [ok] {"device_id": "lampu_ruang_tamu", "connection": "offline"' in h.text


@pytest.mark.parametrize(
    "line, expected",
    [
        ("/fail", "usage: /fail"),
        (f"/fail {LAMP} melted", "unknown mode"),
        ("/fail kulkas offline", "/state lists the device ids"),
        ("/teleport", "unknown command"),
    ],
)
def test_bad_commands_are_explained_not_raised(tmp_path, line, expected):
    h = Harness(tmp_path, [])

    h.run(line)

    assert expected in h.text
    assert h.llm.calls == []


def test_an_llm_failure_is_reported_and_the_cli_keeps_running(tmp_path):
    h = Harness(
        tmp_path,
        [
            _call("home_get_state", {"device_id": LAMP}),
            ApiDown("503"),
            _text("Halo lagi."),
        ],
    )

    still_running = h.run("lampunya nyala?", "halo")

    assert still_running
    assert "[error] ApiDown: 503" in h.text
    assert "-> home_get_state" in h.text  # the partial turn was saved and traced
    assert h.out[-1] == "F.R.I.D.A.Y: Halo lagi."


def test_new_session_starts_fresh_history(tmp_path):
    h = Harness(tmp_path, [_text("Satu."), _text("Dua.")])

    h.run("satu", "/new", "dua")

    assert "new session: cli-" in h.text
    first = h.cli.orch.session_store.load("cli")
    second = h.cli.orch.session_store.load(h.cli.session_id)
    assert [m["content"] for m in first.messages if m["role"] == "user"] == ["satu"]
    assert [m["content"] for m in second.messages if m["role"] == "user"] == ["dua"]


def test_quit_stops_and_blank_lines_are_ignored(tmp_path):
    h = Harness(tmp_path, [])

    assert h.run("", "   ") is True
    assert h.run("/quit", "never sent") is False
    assert h.llm.calls == []


def test_format_trace_truncates_long_results():
    turn = [{"role": "user", "content": [{"type": "tool_result", "content": "x" * 500, "is_error": False}]}]

    [line] = format_trace(turn)

    assert line.endswith("...") and len(line) < 200


def test_main_exits_on_eof(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr("backend.cli.get_llm_client", lambda: FakeLLMClient([]))
    monkeypatch.setenv("FRIDAY_ACTION_JOURNAL_FILE", str(tmp_path / "actions.db"))

    def eof(_prompt):
        raise EOFError

    monkeypatch.setattr("builtins.input", eof)

    main(["--session", "t"])

    assert "session 't'" in capsys.readouterr().out

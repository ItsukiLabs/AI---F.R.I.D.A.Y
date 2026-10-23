"""M4: catalog tools used successfully in recent turns stay loaded (decided 2026-10-23).

``tool_retention_turns``: 3 by default, ``None`` = whole stored
conversation, ``0`` = never (the pre-2026-10-23 behavior).
"""

from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.devices import MockHomeAdapter, default_home
from backend.memory.archive_store import ArchiveStore
from backend.memory.profile_store import ProfileStore
from backend.memory.store import SessionStore
from backend.orchestrator import Orchestrator
from backend.registry import FIND_TOOLS_NAME, ToolCatalog, recently_used_tool_names

LAMP = "lampu_ruang_tamu"


class FakeLLMClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": [dict(m) for m in messages], "tools": tools})
        return self._responses.pop(0)


def _call(name, arguments, call_id="c1"):
    return LLMResponse(
        text=None,
        tool_calls=[ToolCallRequest(id=call_id, name=name, arguments=arguments)],
        stop_reason="tool_use",
    )


def _text(text):
    return LLMResponse(text=text, tool_calls=[])


def _names(call):
    return {tool["name"] for tool in call["tools"]}


def _turn_on_lamp_script():
    return [
        _call(FIND_TOOLS_NAME, {"query": "set power lamp"}, "c1"),
        _call("home_set_power", {"device_id": LAMP, "on": True}, "c2"),
        _text("Lampu nyala."),
    ]


class World:
    def __init__(self, tmp_path, llm, **kwargs):
        self.home = default_home()
        self.catalog = ToolCatalog()
        self.adapter = MockHomeAdapter(self.home)
        self.adapter.sync_into(self.catalog)  # discoverable, not pinned
        self.orch = Orchestrator(
            llm,
            catalog=self.catalog,
            session_store=SessionStore(base_dir=tmp_path / "sessions"),
            profile_store=ProfileStore(base_dir=tmp_path / "profile"),
            archive_store=ArchiveStore(base_dir=tmp_path / "archive"),
            **kwargs,
        )


# --- orchestrator -----------------------------------------------------------


def test_actuator_used_last_turn_is_callable_without_find_tools(tmp_path):
    llm = FakeLLMClient(
        _turn_on_lamp_script()
        + [_call("home_set_power", {"device_id": LAMP, "on": False}, "c3"), _text("Mati.")]
    )
    w = World(tmp_path, llm)

    w.orch.run_turn("nyalakan lampu", "s1")
    w.orch.run_turn("matikan lagi", "s1")

    assert "home_set_power" in _names(llm.calls[3])
    assert llm.calls[4]["messages"][-1]["content"][0]["is_error"] is False
    assert w.home.snapshot()[LAMP]["on"] is False


def test_retention_window_expires_after_n_turns(tmp_path):
    llm = FakeLLMClient(_turn_on_lamp_script() + [_text("a"), _text("b"), _text("c"), _text("d")])
    w = World(tmp_path, llm, tool_retention_turns=3)

    w.orch.run_turn("nyalakan lampu", "s1")  # turn 1: used
    for text in ("halo", "apa kabar", "oke"):  # turns 2-4
        w.orch.run_turn(text, "s1")
    w.orch.run_turn("lagi", "s1")  # turn 5

    tools_per_turn = [_names(c) for c in llm.calls[3:]]  # first call of turns 2..5
    assert ["home_set_power" in t for t in tools_per_turn] == [True, True, True, False]


def test_failed_not_loaded_call_does_not_earn_retention(tmp_path):
    """Otherwise an actuator could skip find_tools by being called blindly once."""
    llm = FakeLLMClient(
        [
            _call("home_set_power", {"device_id": LAMP, "on": True}),
            _text("Sebentar."),
            _text("Halo."),
        ]
    )
    w = World(tmp_path, llm)

    w.orch.run_turn("nyalakan lampu", "s1")
    w.orch.run_turn("halo", "s1")

    assert llm.calls[1]["messages"][-1]["content"][0]["is_error"] is True
    assert "home_set_power" not in _names(llm.calls[2])
    assert w.home.actions == []


def test_retention_zero_keeps_the_old_behavior(tmp_path):
    llm = FakeLLMClient(_turn_on_lamp_script() + [_text("Halo.")])
    w = World(tmp_path, llm, tool_retention_turns=0)

    w.orch.run_turn("nyalakan lampu", "s1")
    w.orch.run_turn("halo", "s1")

    assert "home_set_power" not in _names(llm.calls[3])


def test_retention_none_keeps_tools_for_the_whole_session(tmp_path):
    llm = FakeLLMClient(_turn_on_lamp_script() + [_text(str(i)) for i in range(6)])
    w = World(tmp_path, llm, tool_retention_turns=None)

    w.orch.run_turn("nyalakan lampu", "s1")
    for i in range(6):
        w.orch.run_turn(f"pesan {i}", "s1")

    assert "home_set_power" in _names(llm.calls[-1])


def test_retention_is_per_session(tmp_path):
    llm = FakeLLMClient(_turn_on_lamp_script() + [_text("Halo.")])
    w = World(tmp_path, llm)

    w.orch.run_turn("nyalakan lampu", "s1")
    w.orch.run_turn("halo", "s2")

    assert "home_set_power" not in _names(llm.calls[3])


def test_tool_removed_from_catalog_is_not_retained(tmp_path):
    llm = FakeLLMClient(_turn_on_lamp_script() + [_text("Halo.")])
    w = World(tmp_path, llm)

    w.orch.run_turn("nyalakan lampu", "s1")
    w.catalog.sync("mock_home", [])  # adapter now offers nothing
    w.orch.run_turn("halo", "s1")

    assert "home_set_power" not in _names(llm.calls[3])


# --- helper -----------------------------------------------------------------


def _use(call_id, name):
    return {"role": "assistant", "content": [{"type": "tool_use", "id": call_id, "name": name, "input": {}}]}


def _result(call_id, is_error=False):
    return {
        "role": "user",
        "content": [{"type": "tool_result", "tool_use_id": call_id, "content": "x", "is_error": is_error}],
    }


def _reply():
    return {"role": "assistant", "content": [{"type": "text", "text": "ok"}]}


def test_helper_counts_turns_from_plain_user_messages_most_recent_first():
    messages = [
        {"role": "user", "content": "t1"}, _use("a", "tool_a"), _result("a"), _reply(),
        {"role": "user", "content": "t2"}, _use("b", "tool_b"), _result("b"), _reply(),
        {"role": "user", "content": "t3"}, _use("c", "tool_c"), _result("c", is_error=True), _reply(),
    ]

    assert recently_used_tool_names(messages, 1) == []  # t3's only call failed
    assert recently_used_tool_names(messages, 2) == ["tool_b"]
    assert recently_used_tool_names(messages, 3) == ["tool_b", "tool_a"]
    assert recently_used_tool_names(messages, None) == ["tool_b", "tool_a"]
    assert recently_used_tool_names(messages, 0) == []

"""M4 wiring: Orchestrator with a ToolCatalog — pinned tools, find_tools, per-turn isolation."""

import pytest

from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.agent_core.tool_registry import ToolRegistry
from backend.memory.archive_store import ArchiveStore
from backend.memory.profile_store import ProfileStore
from backend.memory.store import SessionStore
from backend.orchestrator import Orchestrator
from backend.registry import FIND_TOOLS_NAME, ToolCatalog
from backend.schemas import PermissionTier, ToolContract, ToolExample

MEMORY_TOOLS = {"remember_user_fact", "forget_user_fact", "recall_memory"}

TIME_CONTRACT = ToolContract(
    name="get_current_time",
    version="1.0.0",
    description="Get the current time.",
    domain="time",
    input_schema={"type": "object", "properties": {}, "additionalProperties": False},
)

LAMP_CONTRACT = ToolContract(
    name="lamp_set_power",
    version="1.0.0",
    description="Turn the living room lamp on or off.",
    domain="device_lamp",
    input_schema={
        "type": "object",
        "properties": {"on": {"type": "boolean"}},
        "required": ["on"],
        "additionalProperties": False,
    },
    examples=[ToolExample(scenario="User: 'nyalakan lampu'", arguments={"on": True})],
    permission_tier=PermissionTier.CRITICAL,
)


class FakeLLMClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": list(messages), "tools": tools, "system": system})
        return self._responses.pop(0)


def _call(name, arguments, call_id="call_1"):
    return LLMResponse(
        text=None,
        tool_calls=[ToolCallRequest(id=call_id, name=name, arguments=arguments)],
        stop_reason="tool_use",
    )


def _text(text):
    return LLMResponse(text=text, tool_calls=[])


def _names(call):
    return {tool["name"] for tool in call["tools"]}


def _stores(tmp_path):
    return {
        "session_store": SessionStore(base_dir=tmp_path / "sessions"),
        "profile_store": ProfileStore(base_dir=tmp_path / "profile"),
        "archive_store": ArchiveStore(base_dir=tmp_path / "archive"),
    }


def _catalog(lamp_calls):
    catalog = ToolCatalog()
    catalog.register(TIME_CONTRACT, lambda: {"iso_datetime": "2026-09-11T10:00:00+00:00"})
    catalog.sync("lamp_adapter", [(LAMP_CONTRACT, lambda on: lamp_calls.append(on) or {"on": on})])
    catalog.describe_domain("device_lamp", "Lampu gantung di ruang tamu")
    return catalog


def test_discoverable_tool_is_hidden_until_find_tools_loads_it(tmp_path):
    lamp_calls = []
    llm = FakeLLMClient(
        [
            _call(FIND_TOOLS_NAME, {"query": "turn on lamp"}, "call_1"),
            _call("lamp_set_power", {"on": True}, "call_2"),
            _text("Lampu ruang tamu sudah nyala."),
        ]
    )
    orch = Orchestrator(llm, catalog=_catalog(lamp_calls), **_stores(tmp_path))

    result = orch.run_turn("nyalakan lampu ruang tamu", session_id="s1")

    assert result.text == "Lampu ruang tamu sudah nyala."
    assert _names(llm.calls[0]) == {"get_current_time", FIND_TOOLS_NAME} | MEMORY_TOOLS
    assert "lamp_set_power" in _names(llm.calls[1])
    assert lamp_calls == [True]
    lamp_result = llm.calls[2]["messages"][-1]["content"][0]
    assert lamp_result["is_error"] is False


def test_calling_a_discoverable_tool_without_find_tools_is_an_observation_not_a_crash(tmp_path):
    lamp_calls = []
    llm = FakeLLMClient([_call("lamp_set_power", {"on": True}), _text("Maaf, belum bisa.")])
    orch = Orchestrator(llm, catalog=_catalog(lamp_calls), **_stores(tmp_path))

    result = orch.run_turn("nyalakan lampu", session_id="s1")

    assert result.text == "Maaf, belum bisa."
    assert lamp_calls == []
    observation = llm.calls[1]["messages"][-1]["content"][0]
    assert observation["is_error"] is True
    assert "not registered" in observation["content"]


def test_tools_loaded_in_one_turn_are_gone_at_the_start_of_the_next(tmp_path):
    lamp_calls = []
    catalog = _catalog(lamp_calls)
    stores = _stores(tmp_path)
    llm = FakeLLMClient(
        [
            _call(FIND_TOOLS_NAME, {"query": "lamp"}),
            _text("Siap."),
            _text("Halo lagi."),
        ]
    )
    orch = Orchestrator(llm, catalog=catalog, **stores)

    orch.run_turn("cari tool lampu", session_id="s1")
    orch.run_turn("halo", session_id="s1")

    assert "lamp_set_power" in _names(llm.calls[1])
    assert "lamp_set_power" not in _names(llm.calls[2])
    assert catalog.has("lamp_set_power")  # the catalog itself is never mutated by a turn


def test_catalog_with_only_pinned_tools_does_not_install_find_tools(tmp_path):
    catalog = ToolCatalog()
    catalog.register(TIME_CONTRACT, lambda: {"iso_datetime": "x"})
    llm = FakeLLMClient([_text("ok")])

    Orchestrator(llm, catalog=catalog, **_stores(tmp_path)).run_turn("hi", session_id="s1")

    assert _names(llm.calls[0]) == {"get_current_time"} | MEMORY_TOOLS


def test_without_catalog_there_is_no_find_tools(tmp_path):
    registry = ToolRegistry()
    registry.register(TIME_CONTRACT, lambda: {"iso_datetime": "x"})
    llm = FakeLLMClient([_text("ok")])

    Orchestrator(llm, registry, **_stores(tmp_path)).run_turn("hi", session_id="s1")

    assert _names(llm.calls[0]) == {"get_current_time"} | MEMORY_TOOLS


def test_registry_is_optional(tmp_path):
    llm = FakeLLMClient([_text("ok")])

    result = Orchestrator(llm, **_stores(tmp_path)).run_turn("hi", session_id="s1")

    assert result.text == "ok"
    assert _names(llm.calls[0]) == MEMORY_TOOLS


def test_same_tool_name_in_registry_and_catalog_fails_loud(tmp_path):
    registry = ToolRegistry()
    registry.register(TIME_CONTRACT, lambda: {"iso_datetime": "x"})
    catalog = ToolCatalog()
    catalog.register(TIME_CONTRACT, lambda: {"iso_datetime": "y"})
    orch = Orchestrator(FakeLLMClient([_text("ok")]), registry, catalog=catalog, **_stores(tmp_path))

    with pytest.raises(ValueError, match="already registered"):
        orch.run_turn("hi", session_id="s1")

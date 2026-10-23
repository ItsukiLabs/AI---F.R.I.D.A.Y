"""M4: calling a catalog tool that was never loaded in this turn.

Policy (``AutoLoadPolicy``, decided 2026-10-23): by default a read-only
tool is loaded on the spot, a tool that changes something needs
``find_tools`` first, and the observation says so. ``ALL`` and ``NEVER``
keep both behaviors available.
"""

import pytest

from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.agent_core.tool_registry import ToolNotLoadedError, ToolRegistry
from backend.devices import MockHomeAdapter, default_home
from backend.memory.archive_store import ArchiveStore
from backend.memory.profile_store import ProfileStore
from backend.memory.store import SessionStore
from backend.orchestrator import Orchestrator
from backend.registry import AutoLoadPolicy, FIND_TOOLS_NAME, ToolCatalog, make_catalog_resolver

LAMP = "lampu_ruang_tamu"


class FakeLLMClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": [dict(m) for m in messages], "tools": tools})
        return self._responses.pop(0)


def _call(name, arguments):
    return LLMResponse(
        text=None,
        tool_calls=[ToolCallRequest(id="c1", name=name, arguments=arguments)],
        stop_reason="tool_use",
    )


def _text(text):
    return LLMResponse(text=text, tool_calls=[])


def _setup(tmp_path, llm, **kwargs):
    home = default_home()
    catalog = ToolCatalog()
    MockHomeAdapter(home).sync_into(catalog)  # discoverable, not pinned
    orch = Orchestrator(
        llm,
        catalog=catalog,
        session_store=SessionStore(base_dir=tmp_path / "sessions"),
        profile_store=ProfileStore(base_dir=tmp_path / "profile"),
        archive_store=ArchiveStore(base_dir=tmp_path / "archive"),
        **kwargs,
    )
    return home, orch


def _observation(llm):
    return llm.calls[1]["messages"][-1]["content"][0]


def _tool_names(call):
    return {tool["name"] for tool in call["tools"]}


# --- default policy: READ_ONLY ----------------------------------------------


def test_read_only_tool_is_loaded_and_run_without_find_tools(tmp_path):
    llm = FakeLLMClient([_call("home_get_state", {"device_id": LAMP}), _text("Lampu mati.")])
    _, orch = _setup(tmp_path, llm)

    orch.run_turn("lampunya nyala?", "s1")

    observation = _observation(llm)
    assert observation["is_error"] is False
    assert '"on": false' in observation["content"]
    assert "home_get_state" not in _tool_names(llm.calls[0])
    assert "home_get_state" in _tool_names(llm.calls[1])  # stays loaded for the rest of the turn


def test_actuator_needs_find_tools_and_nothing_happens(tmp_path):
    llm = FakeLLMClient([_call("home_set_power", {"device_id": LAMP, "on": True}), _text("Sebentar.")])
    home, orch = _setup(tmp_path, llm)

    orch.run_turn("nyalakan lampu", "s1")

    observation = _observation(llm)
    assert observation["is_error"] is True
    assert "exists in the catalog but is not loaded" in observation["content"]
    assert "not read-only" in observation["content"]
    assert FIND_TOOLS_NAME in observation["content"]
    assert home.actions == []
    assert "home_set_power" not in _tool_names(llm.calls[1])


def test_actuator_works_after_find_tools(tmp_path):
    llm = FakeLLMClient(
        [
            _call(FIND_TOOLS_NAME, {"query": "set power lamp"}),
            _call("home_set_power", {"device_id": LAMP, "on": True}),
            _text("Lampu nyala."),
        ]
    )
    home, orch = _setup(tmp_path, llm)

    orch.run_turn("nyalakan lampu", "s1")

    assert home.actions == [{"device_id": LAMP, "changes": {"on": True}}]


def test_unknown_tool_is_still_reported_as_not_registered(tmp_path):
    llm = FakeLLMClient([_call("teleport_user", {}), _text("Tidak bisa.")])
    _, orch = _setup(tmp_path, llm)

    orch.run_turn("teleport aku", "s1")

    observation = _observation(llm)
    assert observation["is_error"] is True
    assert "not registered" in observation["content"]


def test_auto_loaded_arguments_are_still_validated(tmp_path):
    llm = FakeLLMClient([_call("home_get_state", {"device_id": "kulkas"}), _text("Tidak ada.")])
    _, orch = _setup(tmp_path, llm)

    orch.run_turn("kulkasnya nyala?", "s1")

    observation = _observation(llm)
    assert observation["is_error"] is True
    assert "Invalid arguments" in observation["content"]


# --- other policies ---------------------------------------------------------


def test_policy_all_loads_actuators_too(tmp_path):
    llm = FakeLLMClient([_call("home_set_power", {"device_id": LAMP, "on": True}), _text("Nyala.")])
    home, orch = _setup(tmp_path, llm, catalog_auto_load="all")

    orch.run_turn("nyalakan lampu", "s1")

    assert _observation(llm)["is_error"] is False
    assert home.actions == [{"device_id": LAMP, "changes": {"on": True}}]


def test_policy_never_requires_find_tools_even_for_reads(tmp_path):
    llm = FakeLLMClient([_call("home_get_state", {"device_id": LAMP}), _text("Sebentar.")])
    _, orch = _setup(tmp_path, llm, catalog_auto_load=AutoLoadPolicy.NEVER)

    orch.run_turn("lampunya nyala?", "s1")

    observation = _observation(llm)
    assert observation["is_error"] is True
    assert "is not loaded" in observation["content"]
    assert "not read-only" not in observation["content"]


def test_unknown_policy_is_rejected():
    with pytest.raises(ValueError):
        Orchestrator(FakeLLMClient([]), catalog=ToolCatalog(), catalog_auto_load="sometimes")


# --- registry level ---------------------------------------------------------


def test_registry_without_resolver_behaves_like_get():
    registry = ToolRegistry()
    with pytest.raises(KeyError) as info:
        registry.resolve("nothing")
    assert not isinstance(info.value, ToolNotLoadedError)


def test_resolver_returns_none_for_names_outside_the_catalog():
    registry = ToolRegistry()
    resolver = make_catalog_resolver(ToolCatalog(), registry)
    assert resolver("nothing") is None


def test_not_loaded_error_message_is_unquoted():
    assert str(ToolNotLoadedError("Load it first")) == "Load it first"

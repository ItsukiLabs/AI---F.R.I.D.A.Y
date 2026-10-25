"""M5 mock home: device state, failure injection, catalog sync, SAGE-style end-to-end task."""

import pytest

from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.agent_core.tool_registry import ToolRegistry
from backend.devices import (
    MOCK_HOME_DOMAIN,
    MOCK_HOME_PROVIDER,
    DeviceError,
    FailureMode,
    MockDevice,
    MockHome,
    MockHomeAdapter,
    default_home,
)
from backend.memory.archive_store import ArchiveStore
from backend.memory.profile_store import ProfileStore
from backend.memory.store import SessionStore
from backend.orchestrator import Orchestrator
from backend.registry import FIND_TOOLS_NAME, ToolCatalog


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


def _stores(tmp_path):
    return {
        "session_store": SessionStore(base_dir=tmp_path / "sessions"),
        "profile_store": ProfileStore(base_dir=tmp_path / "profile"),
        "archive_store": ArchiveStore(base_dir=tmp_path / "archive"),
    }


def _tool_fns(home):
    return {contract.name: fn for contract, fn in MockHomeAdapter(home).tools()}


# -- MockHome ---------------------------------------------------------------


def test_apply_changes_state_and_records_the_action():
    home = default_home()

    state = home.apply("lampu_ruang_tamu", on=True)

    assert state == {"on": True, "brightness": 100}
    assert home.snapshot()["lampu_ruang_tamu"]["on"] is True
    assert home.actions == [{"device_id": "lampu_ruang_tamu", "changes": {"on": True}}]


def test_returned_state_is_a_copy():
    home = default_home()
    home.read_state("ac_kamar")["on"] = True
    assert home.snapshot()["ac_kamar"]["on"] is False


def test_offline_applies_nothing_and_fails_once():
    home = default_home()
    home.fail_next("lampu_ruang_tamu", FailureMode.OFFLINE)

    with pytest.raises(DeviceError, match="offline"):
        home.apply("lampu_ruang_tamu", on=True)
    assert home.snapshot()["lampu_ruang_tamu"]["on"] is False
    assert home.actions == []

    home.apply("lampu_ruang_tamu", on=True)  # the failure was one-shot
    assert home.snapshot()["lampu_ruang_tamu"]["on"] is True


def test_lost_ack_applies_the_change_and_still_raises():
    home = default_home()
    home.fail_next("lampu_ruang_tamu", FailureMode.LOST_ACK)

    with pytest.raises(DeviceError, match="did not confirm"):
        home.apply("lampu_ruang_tamu", on=True)

    assert home.snapshot()["lampu_ruang_tamu"]["on"] is True
    assert len(home.actions) == 1


def test_unknown_device_is_a_device_error():
    with pytest.raises(DeviceError, match="no device"):
        default_home().apply("kulkas", on=True)


def test_diff_reports_only_mismatching_named_keys():
    home = default_home()
    home.apply("ac_kamar", on=True, target_temperature=26)

    assert home.diff({"ac_kamar": {"on": True, "target_temperature": 26}}) == {}
    assert home.diff({"ac_kamar": {"target_temperature": 22}, "lampu_ruang_tamu": {"on": False}}) == {
        "ac_kamar": {"target_temperature": (22, 26)}
    }


def test_duplicate_device_id_is_rejected():
    home = default_home()
    with pytest.raises(ValueError, match="duplicate"):
        home.add_device(MockDevice("ac_kamar", "AC lain", "dapur", "air_conditioner"))


# -- adapter tools ----------------------------------------------------------


def test_adapter_publishes_read_and_actuator_tools_in_one_domain():
    contracts = {c.name: c for c, _ in MockHomeAdapter(default_home()).tools()}

    assert set(contracts) == {
        "home_list_devices",
        "home_get_state",
        "home_set_power",
        "home_set_brightness",
        "home_set_target_temperature",
    }
    assert {c.domain for c in contracts.values()} == {MOCK_HOME_DOMAIN}
    assert contracts["home_get_state"].annotations.read_only_hint is True
    assert contracts["home_set_power"].annotations.read_only_hint is False
    assert all(c.examples for c in contracts.values())
    assert contracts["home_set_brightness"].input_schema["properties"]["device_id"]["enum"] == [
        "lampu_ruang_tamu"
    ]


def test_tools_drive_the_home():
    home = default_home()
    fns = _tool_fns(home)

    fns["home_set_brightness"](device_id="lampu_ruang_tamu", brightness=40)
    fns["home_set_target_temperature"](device_id="ac_kamar", target_temperature=26)

    assert home.diff(
        {
            "lampu_ruang_tamu": {"on": True, "brightness": 40},
            "ac_kamar": {"on": True, "target_temperature": 26},
        }
    ) == {}
    assert fns["home_get_state"](device_id="ac_kamar")["reported"]["target_temperature"] == 26
    assert len(fns["home_list_devices"]()["devices"]) == 2


def test_tools_register_cleanly_in_a_turn_registry():
    registry = ToolRegistry()
    for contract, fn in MockHomeAdapter(default_home()).tools():
        registry.register(contract, fn)
    assert len(registry.to_llm_tools()) == 5


# -- catalog sync (ScaleMCP) ------------------------------------------------


def test_sync_is_idempotent_and_picks_up_a_new_device_without_restart():
    home = default_home()
    adapter = MockHomeAdapter(home)
    catalog = ToolCatalog()

    first = adapter.sync_into(catalog)
    again = adapter.sync_into(catalog)
    home.add_device(MockDevice("lampu_dapur", "Lampu dapur", "dapur", "lamp", {"on": False}))
    after_new_device = adapter.sync_into(catalog)

    assert len(first.added) == 5
    assert not again.changed
    # The device_id enum changed, so every tool naming devices has a new content_hash.
    assert set(after_new_device.updated) == {"home_get_state", "home_set_power", "home_set_brightness"}
    assert after_new_device.unchanged == ("home_list_devices", "home_set_target_temperature")
    assert catalog.get("home_set_power").provider == MOCK_HOME_PROVIDER


def test_sync_removes_tools_whose_device_kind_is_gone():
    catalog = ToolCatalog()
    home = default_home()
    MockHomeAdapter(home).sync_into(catalog)

    lamp_only = MockHome([d for d in default_home().devices() if d.kind == "lamp"])
    report = MockHomeAdapter(lamp_only).sync_into(catalog)

    assert report.removed == ("home_set_target_temperature",)
    assert not catalog.has("home_set_target_temperature")


@pytest.mark.parametrize(
    "query, expected",
    [
        ("nyalakan lampu", "home_set_power"),
        ("lampunya udah nyala belum", "home_get_state"),
        ("atur suhu AC", "home_set_target_temperature"),
        ("agak gelap", "home_set_brightness"),
    ],
)
def test_catalog_search_finds_device_tools_from_everyday_phrases(query, expected):
    catalog = ToolCatalog()
    MockHomeAdapter(default_home()).sync_into(catalog)

    names = [hit.contract.name for hit in catalog.search(query)]

    assert expected in names


def test_catalog_search_for_a_missing_device_finds_nothing():
    catalog = ToolCatalog()
    MockHomeAdapter(default_home()).sync_into(catalog)
    assert catalog.search("kulkas") == []


# -- SAGE-style task: initial state, command, final-state check -------------


def test_end_to_end_turn_on_lamp_through_find_tools(tmp_path):
    home = default_home()
    catalog = ToolCatalog()
    MockHomeAdapter(home).sync_into(catalog)
    llm = FakeLLMClient(
        [
            _call(FIND_TOOLS_NAME, {"query": "nyalakan lampu"}, "c1"),
            _call("home_set_power", {"device_id": "lampu_ruang_tamu", "on": True}, "c2"),
            _text("Lampu ruang tamu sudah menyala."),
        ]
    )
    orch = Orchestrator(llm, catalog=catalog, **_stores(tmp_path))

    result = orch.run_turn("nyalakan lampu ruang tamu", session_id="s1")

    assert result.text == "Lampu ruang tamu sudah menyala."
    assert home.diff({"lampu_ruang_tamu": {"on": True}, "ac_kamar": {"on": False}}) == {}
    domain_listing = llm.calls[0]["tools"]
    find_tools = next(t for t in domain_listing if t["name"] == FIND_TOOLS_NAME)
    assert "home: Perangkat rumah" in find_tools["description"]


def test_invalid_argument_type_is_rejected_before_touching_the_device(tmp_path):
    """Smoke-test finding from M4: the model sent a boolean as a string."""
    home = default_home()
    catalog = ToolCatalog()
    MockHomeAdapter(home).sync_into(catalog, pinned=True)
    llm = FakeLLMClient(
        [
            _call("home_set_power", {"device_id": "lampu_ruang_tamu", "on": "true"}, "c1"),
            _call("home_set_power", {"device_id": "lampu_ruang_tamu", "on": True}, "c2"),
            _text("Sudah."),
        ]
    )

    Orchestrator(llm, catalog=catalog, **_stores(tmp_path)).run_turn("nyalakan lampu", "s1")

    first_observation = llm.calls[1]["messages"][-1]["content"][0]
    assert first_observation["is_error"] is True
    assert "Invalid arguments" in first_observation["content"]
    assert home.actions == [{"device_id": "lampu_ruang_tamu", "changes": {"on": True}}]

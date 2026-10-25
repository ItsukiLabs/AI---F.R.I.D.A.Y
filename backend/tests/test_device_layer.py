"""Stage 2 (2026-10-25): Device contract, DeviceService shadow and generated tools."""

import pytest

from backend.devices import (
    DeviceError,
    DeviceService,
    FailureMode,
    MockHome,
    MockHomeAdapter,
    build_device_tools,
    default_home,
)
from backend.schemas.device_contract import (
    BRIGHTNESS,
    CURRENT_TEMPERATURE,
    DEVICE_CONTRACT_VERSION,
    POWER,
    TARGET_TEMPERATURE,
    Capability,
    CommandStatus,
    DeviceDescriptor,
)

LAMP = "lampu_ruang_tamu"
AC = "ac_kamar"


class Clock:
    def __init__(self):
        self.ticks = 0

    def __call__(self):
        self.ticks += 1
        return f"t{self.ticks}"


def _service(home=None):
    home = home or default_home()
    return home, DeviceService(home, clock=Clock())


class RoundingHome(MockHome):
    """A device that steps the target temperature to the nearest 0.5 °C, or ignores it."""

    def __init__(self, reported_target):
        super().__init__(default_home().devices())
        self.reported_target = reported_target

    def apply(self, device_id, **changes):
        state = super().apply(device_id, **changes)
        if "target_temperature" in changes:
            self.device(device_id).state["target_temperature"] = self.reported_target
            state["target_temperature"] = self.reported_target
        return state


class DeadHome(MockHome):
    """Every command and every read to the lamp fails: nothing can be confirmed."""

    def __init__(self):
        super().__init__(default_home().devices())

    def apply(self, device_id, **changes):
        raise DeviceError("no route to device")

    def read_state(self, device_id):
        raise DeviceError("no route to device")


# -- contract -----------------------------------------------------------------


def test_contract_version_and_standard_capabilities():
    assert DEVICE_CONTRACT_VERSION == "1.1.0"  # stage 3 added pending_operations
    assert TARGET_TEMPERATURE.name == "target_temperature"
    assert CURRENT_TEMPERATURE.writable is False


@pytest.mark.parametrize(
    "capability, value, error",
    [
        (POWER, "true", "must be boolean"),
        (BRIGHTNESS, True, "must be integer"),
        (BRIGHTNESS, 0, "at least 1"),
        (BRIGHTNESS, 101, "at most 100"),
        (TARGET_TEMPERATURE, 26.5, "must be integer"),
        (CURRENT_TEMPERATURE, 25.0, "read-only"),
    ],
)
def test_capability_rejects_bad_values(capability, value, error):
    with pytest.raises(ValueError, match=error):
        capability.check(value)


def test_capability_tolerance_for_analog_values():
    assert TARGET_TEMPERATURE.matches(24, 24.5)
    assert not TARGET_TEMPERATURE.matches(24, 25)
    assert not TARGET_TEMPERATURE.matches(24, None)
    assert BRIGHTNESS.matches(40, 40) and not BRIGHTNESS.matches(40, 41)
    assert not POWER.matches(True, 1)  # booleans compare exactly


def test_descriptor_rejects_a_bad_device_id():
    with pytest.raises(ValueError):
        DeviceDescriptor(device_id="Lampu Tamu", name="x", room="y", kind="lamp")


def test_mock_home_describes_capabilities_per_kind():
    kinds = {d.device_id: [c.name for c in d.capabilities] for d in default_home().descriptors()}
    assert kinds == {
        LAMP: ["on", "brightness"],
        AC: ["on", "target_temperature", "current_temperature"],
    }


# -- service: commands ----------------------------------------------------------


def test_successful_command_has_an_operation_id_and_updates_the_shadow():
    home, service = _service()

    first = service.apply(LAMP, {"on": True})
    second = service.apply(LAMP, {"brightness": 40})

    assert first.status is CommandStatus.SUCCEEDED and first.message is None
    assert len(first.operation_id) == 32 and first.operation_id != second.operation_id
    assert first.requested == {"on": True}
    assert first.reported == {"on": True, "brightness": 100}
    snapshot = service.read_state(LAMP)
    assert snapshot.desired == {"on": True, "brightness": 40}
    assert snapshot.reported == {"on": True, "brightness": 40}
    assert snapshot.in_sync is True and snapshot.connection == "online" and snapshot.message is None


@pytest.mark.parametrize(
    "device_id, changes, error",
    [
        (LAMP, {"target_temperature": 24}, "has no 'target_temperature'"),
        (AC, {"current_temperature": 20.0}, "read-only"),
        (AC, {"target_temperature": 40}, "at most 30"),
        (LAMP, {"on": "yes"}, "must be boolean"),
        (LAMP, {}, "at least one change"),
        ("kulkas", {"on": True}, "no device"),
    ],
)
def test_invalid_commands_never_reach_the_device(device_id, changes, error):
    home, service = _service()
    with pytest.raises((ValueError, DeviceError), match=error):
        service.apply(device_id, changes)
    assert home.actions == []
    assert service.read_state(LAMP).desired == {}


def test_lost_ack_is_confirmed_by_read_back():
    home, service = _service()
    home.fail_next(LAMP, FailureMode.LOST_ACK)

    outcome = service.apply(LAMP, {"on": True})

    assert outcome.status is CommandStatus.SUCCEEDED
    assert "took effect" in outcome.message
    assert outcome.reported["on"] is True


def test_offline_command_fails_with_the_actual_state_and_keeps_desired():
    home, service = _service()
    home.fail_next(AC, FailureMode.OFFLINE)

    outcome = service.apply(AC, {"on": True, "target_temperature": 22})

    assert outcome.status is CommandStatus.FAILED
    assert outcome.reported == {"on": False, "target_temperature": 24, "current_temperature": 29.0}
    snapshot = service.read_state(AC)
    assert snapshot.desired == {"on": True, "target_temperature": 22}
    assert snapshot.in_sync is False


def test_no_confirmation_and_no_read_back_is_unknown():
    _, service = _service(DeadHome())

    outcome = service.apply(LAMP, {"on": True})

    assert outcome.status is CommandStatus.UNKNOWN
    assert outcome.reported is None
    assert "actual state unknown" in outcome.message


def test_rounded_analog_value_within_tolerance_succeeds():
    _, service = _service(RoundingHome(reported_target=24.5))
    assert service.apply(AC, {"target_temperature": 24}).status is CommandStatus.SUCCEEDED


def test_device_that_reports_another_value_fails():
    _, service = _service(RoundingHome(reported_target=26))
    outcome = service.apply(AC, {"target_temperature": 22})
    assert outcome.status is CommandStatus.FAILED
    assert "reports a different state" in outcome.message


# -- service: reading state -----------------------------------------------------


def test_offline_read_returns_last_known_state_marked_stale():
    home, service = _service()
    service.read_state(LAMP)  # seen once, at t1
    home.fail_next(LAMP, FailureMode.OFFLINE)

    snapshot = service.read_state(LAMP)

    assert snapshot.connection == "offline"
    assert snapshot.stale is True
    assert snapshot.reported == {"on": False, "brightness": 100}
    assert snapshot.reported_at == "t1"
    assert "did not answer" in snapshot.message and "from t1" in snapshot.message


def test_offline_read_of_a_device_never_seen():
    home, service = _service()
    home.fail_next(LAMP, FailureMode.OFFLINE)
    snapshot = service.read_state(LAMP)
    assert snapshot.reported == {} and snapshot.reported_at is None
    assert "none known yet" in snapshot.message


# -- generated tools --------------------------------------------------------------


def _tools(home=None):
    adapter = MockHomeAdapter(home or default_home())
    return {c.name: (c, fn) for c, fn in adapter.tools()}


def test_tools_are_generated_from_capabilities():
    tools = _tools()
    assert set(tools) == {
        "home_list_devices",
        "home_get_state",
        "home_set_power",
        "home_set_brightness",
        "home_set_target_temperature",
    }
    contract, _ = tools["home_set_target_temperature"]
    schema = contract.input_schema["properties"]
    assert schema["device_id"]["enum"] == [AC]
    assert schema["target_temperature"]["minimum"] == 16 and schema["target_temperature"]["maximum"] == 30
    assert tools["home_get_state"][0].version == "2.0.0"
    assert "current_temperature" in tools["home_get_state"][0].description


def test_a_new_capability_gets_its_own_tool_without_new_code():
    fan_speed = Capability(name="fan_speed", value_type="integer", description="fan speed level", minimum=1, maximum=3)

    class FanHome(MockHome):
        def descriptors(self):
            return [DeviceDescriptor(device_id="kipas", name="Kipas", room="dapur", kind="fan", capabilities=[POWER, fan_speed])]

    contracts = [c.name for c, _ in build_device_tools(DeviceService(FanHome([])), "home")]
    assert contracts == ["home_list_devices", "home_get_state", "home_set_power", "home_set_fan_speed"]


def test_set_tool_turns_the_device_on_and_returns_the_command_result():
    home = default_home()
    _, fn = _tools(home)["home_set_target_temperature"]

    result = fn(device_id=AC, target_temperature=26)

    assert result["status"] == "succeeded"
    assert result["requested"] == {"on": True, "target_temperature": 26}
    assert home.snapshot()[AC]["on"] is True


def test_unconfirmed_command_is_a_tool_error_with_status_and_operation_id():
    home = default_home()
    home.fail_next(LAMP, FailureMode.OFFLINE)
    _, fn = _tools(home)["home_set_power"]

    with pytest.raises(DeviceError) as info:
        fn(device_id=LAMP, on=True)

    message = str(info.value)
    assert "status=failed" in message and "operation_id=" in message
    assert "Actual state read back" in message


def test_get_state_tool_returns_the_snapshot():
    _, fn = _tools()["home_get_state"]
    state = fn(device_id=AC)
    assert state["reported"]["current_temperature"] == 29.0
    assert state["connection"] == "online"

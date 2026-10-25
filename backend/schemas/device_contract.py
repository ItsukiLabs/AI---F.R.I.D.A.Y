"""M0 Device contract: how every device adapter describes devices, state and commands.

Shape follows the device-shadow pattern recommended by all four external
reviews (2026-10-25; AWS IoT Shadow style):

- ``desired`` is what F.R.I.D.A.Y last asked a device to be (kept even if
  the command failed, so "asked for 24°C, still 28°C" is visible);
- ``reported`` is what the device last said it is, with the time it said
  it — after a failed read it is the last known value, marked ``stale``;
- ``connection`` is whether the latest read reached the device.

Every command gets an ``operation_id`` and ends in one ``CommandStatus``.
``PENDING`` is defined now for slow devices (e.g. LoRa class A) but only
produced once the mock simulates them (Sprint 3, stage 3). The id is what
the M11 action journal will key on.

Capabilities are named after the state key they control or report, so one
generic toolset (``backend/devices/tools.py``) can publish tools for any
adapter: a capability is a typed, range-checked value with a tolerance for
read-back comparison of analog values.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from backend.schemas.tool_contract import validate_identifier

DEVICE_CONTRACT_VERSION = "1.0.0"


class Capability(BaseModel):
    """One state key a device has: a power switch, a brightness, a sensor reading."""

    name: str
    value_type: Literal["boolean", "integer", "number"]
    description: str
    writable: bool = True
    minimum: float | None = None
    maximum: float | None = None
    unit: str | None = None
    # Read-back values within this distance of the requested value count as
    # matching: real devices round or step analog values.
    tolerance: float = 0.0

    @field_validator("name")
    @classmethod
    def _name_is_identifier(cls, value: str) -> str:
        return validate_identifier(value, "capability name")

    def json_schema(self) -> dict[str, Any]:
        schema: dict[str, Any] = {"type": self.value_type, "description": self.description}
        if self.minimum is not None:
            schema["minimum"] = self.minimum
        if self.maximum is not None:
            schema["maximum"] = self.maximum
        return schema

    def check(self, value: Any) -> None:
        """Raise ValueError if ``value`` can't be written to this capability."""
        if not self.writable:
            raise ValueError(f"{self.name} is read-only")
        if self.value_type == "boolean":
            ok = isinstance(value, bool)
        elif self.value_type == "integer":
            ok = isinstance(value, int) and not isinstance(value, bool)
        else:
            ok = isinstance(value, (int, float)) and not isinstance(value, bool)
        if not ok:
            raise ValueError(f"{self.name} must be {self.value_type}, got {value!r}")
        if self.minimum is not None and value < self.minimum:
            raise ValueError(f"{self.name} must be at least {self.minimum:g}, got {value!r}")
        if self.maximum is not None and value > self.maximum:
            raise ValueError(f"{self.name} must be at most {self.maximum:g}, got {value!r}")

    def matches(self, requested: Any, reported: Any) -> bool:
        if self.value_type == "boolean":
            # True == 1 in Python; a device reporting 1 must be normalized by
            # its driver, not silently accepted as "on".
            return isinstance(reported, bool) and requested == reported
        if self.tolerance == 0:
            return requested == reported
        if not isinstance(reported, (int, float)) or isinstance(reported, bool):
            return False
        return abs(requested - reported) <= self.tolerance


# Standard capabilities shared by adapters, so tools and comparisons agree.
POWER = Capability(name="on", value_type="boolean", description="power, true = on")
BRIGHTNESS = Capability(
    name="brightness",
    value_type="integer",
    description="brightness",
    minimum=1,
    maximum=100,
    unit="%",
)
TARGET_TEMPERATURE = Capability(
    name="target_temperature",
    value_type="integer",
    description="target temperature the AC cools to",
    minimum=16,
    maximum=30,
    unit="°C",
    tolerance=0.5,
)
CURRENT_TEMPERATURE = Capability(
    name="current_temperature",
    value_type="number",
    description="room temperature measured by the device",
    writable=False,
    unit="°C",
)


class DeviceDescriptor(BaseModel):
    device_id: str
    name: str
    room: str
    kind: str
    capabilities: list[Capability] = Field(default_factory=list)

    @field_validator("device_id")
    @classmethod
    def _id_is_identifier(cls, value: str) -> str:
        return validate_identifier(value, "device_id")

    def capability(self, name: str) -> Capability | None:
        return next((c for c in self.capabilities if c.name == name), None)


class DeviceSnapshot(BaseModel):
    device_id: str
    connection: Literal["online", "offline"]
    reported: dict[str, Any] = Field(default_factory=dict)
    reported_at: str | None = None
    # True when ``reported`` is the last known value, not a fresh read.
    stale: bool = False
    desired: dict[str, Any] = Field(default_factory=dict)
    desired_at: str | None = None
    # Every desired value matches the reported one (within tolerance).
    in_sync: bool = True
    # Set when the device did not answer, so stale values can't pass for fresh ones.
    message: str | None = None


class CommandStatus(str, Enum):
    SUCCEEDED = "succeeded"  # the device (or a read-back) confirms the change
    FAILED = "failed"  # the device is known NOT to be in the requested state
    PENDING = "pending"  # accepted, not confirmed yet (slow devices)
    UNKNOWN = "unknown"  # no confirmation and no read-back: state unknown


class DeviceCommandResult(BaseModel):
    operation_id: str
    device_id: str
    status: CommandStatus
    requested: dict[str, Any]
    reported: dict[str, Any] | None = None
    message: str | None = None

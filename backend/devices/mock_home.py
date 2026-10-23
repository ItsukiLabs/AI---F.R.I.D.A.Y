"""A smart home without hardware, in the shape of SAGE's benchmark.

SAGE (Rivkin et al. 2023, PAPER_NOTES.md #5) evaluates a smart-home agent
with no devices attached: a saved initial state, a user command, then a
check of the final state. ``MockHome`` is that state; ``MockHome.diff()`` is
that check. ``MockHomeAdapter`` is the first M5 provider: it turns the home
into ``ToolContract``s and ``sync()``s them into the M4 catalog. Adding a
device changes the tool contracts (the ``device_id`` enum), and the catalog
picks that up through ``content_hash`` without a restart (ScaleMCP).

Two things are deliberately realistic because A2 needs them:

- A device error is raised from the tool, so ``loop._execute_tool_call``
  turns it into an observation the model sees (SAGE: exception text goes
  back to the agent).
- ``FailureMode.LOST_ACK`` *applies* the change and *then* raises, like a
  real device whose confirmation times out. The adapter's actuator tools
  therefore read the state back after any failed command (A2, decided
  2026-10-23) and report what the device actually is, not just "failed".

``MockHome.actions`` records every applied change in order. It is test
instrumentation for the mock, not the durable action log that A2 option (b)
would add.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from backend.registry import SyncReport, ToolCatalog
from backend.schemas import PermissionTier, ToolAnnotations, ToolContract, ToolExample
from backend.schemas.tool_contract import validate_identifier

MOCK_HOME_PROVIDER = "mock_home"
MOCK_HOME_DOMAIN = "home"

LAMP = "lamp"
AIR_CONDITIONER = "air_conditioner"
_KINDS = {LAMP, AIR_CONDITIONER}

AC_MIN_TEMPERATURE = 16
AC_MAX_TEMPERATURE = 30


class DeviceError(RuntimeError):
    """A device refused or did not confirm a command."""


class FailureMode(str, Enum):
    OFFLINE = "offline"  # nothing is applied; the command raises
    LOST_ACK = "lost_ack"  # the change IS applied, then the command raises


@dataclass
class MockDevice:
    device_id: str
    name: str
    room: str
    kind: str
    state: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_identifier(self.device_id, "device_id")
        if self.kind not in _KINDS:
            raise ValueError(f"unknown device kind {self.kind!r}")


def default_home() -> "MockHome":
    """The home used by tests and the A2 trace: one lamp, one AC, both off."""
    return MockHome(
        [
            MockDevice(
                "lampu_ruang_tamu",
                "Lampu ruang tamu",
                "ruang tamu",
                LAMP,
                {"on": False, "brightness": 100},
            ),
            MockDevice(
                "ac_kamar",
                "AC kamar",
                "kamar tidur",
                AIR_CONDITIONER,
                {"on": False, "temperature": 24},
            ),
        ]
    )


class MockHome:
    def __init__(self, devices: list[MockDevice]) -> None:
        self._devices: dict[str, MockDevice] = {}
        for device in devices:
            if device.device_id in self._devices:
                raise ValueError(f"duplicate device_id {device.device_id!r}")
            self._devices[device.device_id] = device
        self._failures: dict[str, FailureMode] = {}
        self.actions: list[dict[str, Any]] = []

    # -- inspection -------------------------------------------------------

    def devices(self) -> list[MockDevice]:
        return list(self._devices.values())

    def add_device(self, device: MockDevice) -> None:
        if device.device_id in self._devices:
            raise ValueError(f"duplicate device_id {device.device_id!r}")
        self._devices[device.device_id] = device

    def device_ids(self, kind: str | None = None) -> list[str]:
        return sorted(
            d.device_id for d in self._devices.values() if kind is None or d.kind == kind
        )

    def device(self, device_id: str) -> MockDevice:
        try:
            return self._devices[device_id]
        except KeyError:
            raise DeviceError(f"no device with id {device_id!r}") from None

    def snapshot(self) -> dict[str, dict[str, Any]]:
        return {d.device_id: copy.deepcopy(d.state) for d in self._devices.values()}

    def diff(self, expected: dict[str, dict[str, Any]]) -> dict[str, dict[str, tuple[Any, Any]]]:
        """SAGE-style final-state check: ``{device: {key: (expected, actual)}}``, empty if equal.

        Only keys named in ``expected`` are compared.
        """
        mismatches: dict[str, dict[str, tuple[Any, Any]]] = {}
        for device_id, wanted in expected.items():
            actual = self.device(device_id).state
            wrong = {k: (v, actual.get(k)) for k, v in wanted.items() if actual.get(k) != v}
            if wrong:
                mismatches[device_id] = wrong
        return mismatches

    # -- failure injection ------------------------------------------------

    def fail_next(self, device_id: str, mode: FailureMode) -> None:
        """Make the next command to ``device_id`` fail in ``mode`` (once)."""
        self.device(device_id)
        self._failures[device_id] = FailureMode(mode)

    # -- commands ---------------------------------------------------------

    def read_state(self, device_id: str) -> dict[str, Any]:
        device = self.device(device_id)
        if self._failures.get(device_id) is FailureMode.OFFLINE:
            del self._failures[device_id]
            raise DeviceError(f"{device.name} is offline and did not respond")
        return copy.deepcopy(device.state)

    def apply(self, device_id: str, **changes: Any) -> dict[str, Any]:
        device = self.device(device_id)
        failure = self._failures.pop(device_id, None)
        if failure is FailureMode.OFFLINE:
            raise DeviceError(f"{device.name} is offline and did not respond")
        device.state.update(changes)
        self.actions.append({"device_id": device_id, "changes": dict(changes)})
        if failure is FailureMode.LOST_ACK:
            raise DeviceError(f"{device.name} did not confirm the command (timeout)")
        return copy.deepcopy(device.state)


_READ_ONLY = ToolAnnotations(
    read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=True
)
# Physical side effect, but reversible and safe to repeat with the same arguments.
_ACTUATOR = ToolAnnotations(
    read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=True
)


def _object(properties: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": sorted(properties),
        "additionalProperties": False,
    }


class MockHomeAdapter:
    """Publishes a ``MockHome`` as catalog tools under one provider and one domain."""

    def __init__(self, home: MockHome, provider: str = MOCK_HOME_PROVIDER) -> None:
        self.home = home
        self.provider = validate_identifier(provider, "provider")

    def sync_into(self, catalog: ToolCatalog, *, pinned: bool = False) -> SyncReport:
        """Publish the current device set; call again after the home changes."""
        report = catalog.sync(self.provider, self.tools(), pinned=pinned)
        catalog.describe_domain(MOCK_HOME_DOMAIN, self._domain_summary())
        return report

    def _command(self, device_id: str, **changes: Any) -> dict[str, Any]:
        """Apply ``changes``; on a device error, read the state back before answering.

        A command that errors may still have taken effect (``LOST_ACK``). If
        the read-back shows every requested change, the command succeeded
        and is reported as such; otherwise the error is re-raised with the
        actual state, or with "state unknown" if the read-back fails too.
        """
        try:
            return {"device_id": device_id, "state": self.home.apply(device_id, **changes)}
        except DeviceError as exc:
            try:
                actual = self.home.read_state(device_id)
            except DeviceError:
                raise DeviceError(f"{exc}. Read-back failed too; actual state unknown.") from exc
            if all(actual.get(k) == v for k, v in changes.items()):
                return {
                    "device_id": device_id,
                    "state": actual,
                    "note": f"{exc}, but reading the state back shows the change took effect.",
                }
            raise DeviceError(f"{exc}. Actual state read back: {actual}") from exc

    def _domain_summary(self) -> str:
        listing = ", ".join(f"{d.name} ({d.room})" for d in self.home.devices())
        return f"Perangkat rumah, lihat dan ubah status lampu dan AC: {listing}"

    def _device_property(self, kind: str | None) -> dict[str, Any]:
        ids = self.home.device_ids(kind)
        names = "; ".join(
            f"{d.device_id} = {d.name} ({d.room})"
            for d in self.home.devices()
            if d.device_id in ids
        )
        return {"type": "string", "enum": ids, "description": f"Which device. {names}"}

    def tools(self) -> list[tuple[ToolContract, Callable[..., Any]]]:
        home = self.home
        all_ids = home.device_ids()
        lamp_ids = home.device_ids(LAMP)
        ac_ids = home.device_ids(AIR_CONDITIONER)

        def home_list_devices() -> dict[str, Any]:
            return {
                "devices": [
                    {"device_id": d.device_id, "name": d.name, "room": d.room, "kind": d.kind}
                    for d in home.devices()
                ]
            }

        tools: list[tuple[ToolContract, Callable[..., Any]]] = [
            (
                ToolContract(
                    name="home_list_devices",
                    version="1.0.0",
                    domain=MOCK_HOME_DOMAIN,
                    description="List every device in the home with its id, name, room and kind.",
                    input_schema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                    annotations=_READ_ONLY,
                    permission_tier=PermissionTier.READ_ONLY,
                    examples=[
                        ToolExample(scenario="User: 'perangkat apa saja yang ada di rumah?'")
                    ],
                ),
                home_list_devices,
            )
        ]
        if not all_ids:
            return tools

        sample_id = lamp_ids[0] if lamp_ids else all_ids[0]

        def home_get_state(device_id: str) -> dict[str, Any]:
            return {"device_id": device_id, "state": home.read_state(device_id)}

        def home_set_power(device_id: str, on: bool) -> dict[str, Any]:
            return self._command(device_id, on=on)

        tools.append(
            (
                ToolContract(
                    name="home_get_state",
                    version="1.0.0",
                    domain=MOCK_HOME_DOMAIN,
                    description=(
                        "Read a device's current state (on/off, brightness, temperature). "
                        "Use it to check whether an earlier command really took effect."
                    ),
                    input_schema=_object({"device_id": self._device_property(None)}),
                    annotations=_READ_ONLY,
                    permission_tier=PermissionTier.READ_ONLY,
                    examples=[
                        ToolExample(
                            scenario="User: 'lampunya udah nyala belum?'",
                            arguments={"device_id": sample_id},
                        )
                    ],
                ),
                home_get_state,
            )
        )
        tools.append(
            (
                ToolContract(
                    name="home_set_power",
                    version="1.0.0",
                    domain=MOCK_HOME_DOMAIN,
                    description="Turn a device (lamp or AC) on or off. Returns the new state.",
                    input_schema=_object(
                        {
                            "device_id": self._device_property(None),
                            "on": {"type": "boolean", "description": "true = on, false = off"},
                        }
                    ),
                    annotations=_ACTUATOR,
                    permission_tier=PermissionTier.STANDARD,
                    examples=[
                        ToolExample(
                            scenario="User: 'nyalakan lampu ruang tamu'",
                            arguments={"device_id": sample_id, "on": True},
                        )
                    ],
                ),
                home_set_power,
            )
        )

        if lamp_ids:

            def lamp_set_brightness(device_id: str, brightness: int) -> dict[str, Any]:
                return self._command(device_id, on=True, brightness=brightness)

            tools.append(
                (
                    ToolContract(
                        name="lamp_set_brightness",
                        version="1.0.0",
                        domain=MOCK_HOME_DOMAIN,
                        description="Set a lamp's brightness in percent (1-100); turns the lamp on.",
                        input_schema=_object(
                            {
                                "device_id": self._device_property(LAMP),
                                "brightness": {"type": "integer", "minimum": 1, "maximum": 100},
                            }
                        ),
                        annotations=_ACTUATOR,
                        permission_tier=PermissionTier.STANDARD,
                        examples=[
                            ToolExample(
                                scenario="User: 'agak gelap nih di ruang tamu'",
                                arguments={"device_id": lamp_ids[0], "brightness": 80},
                            )
                        ],
                    ),
                    lamp_set_brightness,
                )
            )

        if ac_ids:

            def ac_set_temperature(device_id: str, temperature: int) -> dict[str, Any]:
                return self._command(device_id, on=True, temperature=temperature)

            tools.append(
                (
                    ToolContract(
                        name="ac_set_temperature",
                        version="1.0.0",
                        domain=MOCK_HOME_DOMAIN,
                        description=(
                            "Set an air conditioner's target temperature in degrees Celsius "
                            f"({AC_MIN_TEMPERATURE}-{AC_MAX_TEMPERATURE}); turns the AC on."
                        ),
                        input_schema=_object(
                            {
                                "device_id": self._device_property(AIR_CONDITIONER),
                                "temperature": {
                                    "type": "integer",
                                    "minimum": AC_MIN_TEMPERATURE,
                                    "maximum": AC_MAX_TEMPERATURE,
                                },
                            }
                        ),
                        annotations=_ACTUATOR,
                        permission_tier=PermissionTier.STANDARD,
                        examples=[
                            ToolExample(
                                scenario="User: 'AC kamar dingin banget, naikin suhunya'",
                                arguments={"device_id": ac_ids[0], "temperature": 26},
                            )
                        ],
                    ),
                    ac_set_temperature,
                )
            )

        return tools

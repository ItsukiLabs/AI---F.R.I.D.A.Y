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

Since stage 2 (2026-10-25) ``MockHome`` is just a ``DeviceDriver``: the
read-back, shadow (desired/reported), operation ids and tolerance live in
``DeviceService`` (``service.py``) and the tools are generated from device
capabilities (``tools.py``), so a real adapter gets the same behavior by
implementing ``descriptors``/``read_state``/``apply``. The AC's state keys
are ``target_temperature`` (what it cools to) and ``current_temperature``
(the measured room temperature), replacing the ambiguous ``temperature``.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from backend.devices.service import CommandAccepted, DeviceError, DeviceService
from backend.devices.tools import build_device_tools
from backend.journal import ActionJournal
from backend.registry import SyncReport, ToolCatalog
from backend.schemas import ToolContract
from backend.schemas.device_contract import (
    BRIGHTNESS,
    CURRENT_TEMPERATURE,
    POWER,
    TARGET_TEMPERATURE,
    Capability,
    DeviceDescriptor,
)
from backend.schemas.tool_contract import validate_identifier

MOCK_HOME_PROVIDER = "mock_home"
MOCK_HOME_DOMAIN = "home"

LAMP = "lamp"
AIR_CONDITIONER = "air_conditioner"
# What each kind of mock device can do; the tools are generated from this.
_CAPABILITIES: dict[str, list[Capability]] = {
    LAMP: [POWER, BRIGHTNESS],
    AIR_CONDITIONER: [POWER, TARGET_TEMPERATURE, CURRENT_TEMPERATURE],
}
_KINDS = set(_CAPABILITIES)


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


def two_lamp_home() -> "MockHome":
    """``default_home`` plus a reading lamp in the same living room (disambiguation)."""
    home = default_home()
    home.add_device(
        MockDevice(
            "lampu_baca_ruang_tamu",
            "Lampu baca ruang tamu",
            "ruang tamu",
            LAMP,
            {"on": False, "brightness": 100},
        )
    )
    home.device("lampu_ruang_tamu").name = "Lampu utama ruang tamu"
    return home


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
                {"on": False, "target_temperature": 24, "current_temperature": 29.0},
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
        # Slow devices (stage 3): device_id -> reads a command waits before applying.
        self._slow: dict[str, int] = {}
        self._queued: dict[str, list[list[Any]]] = {}
        self.actions: list[dict[str, Any]] = []

    # -- inspection -------------------------------------------------------

    def devices(self) -> list[MockDevice]:
        return list(self._devices.values())

    def add_device(self, device: MockDevice) -> None:
        if device.device_id in self._devices:
            raise ValueError(f"duplicate device_id {device.device_id!r}")
        self._devices[device.device_id] = device

    def descriptors(self) -> list[DeviceDescriptor]:
        return [
            DeviceDescriptor(
                device_id=d.device_id,
                name=d.name,
                room=d.room,
                kind=d.kind,
                capabilities=_CAPABILITIES[d.kind],
            )
            for d in self._devices.values()
        ]

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

    def make_slow(self, device_id: str, reads: int) -> None:
        """Commands to ``device_id`` take effect only after ``reads`` later state reads.

        Simulates a device that confirms late (e.g. LoRa class A, which only
        receives downlinks after its next uplink). ``reads=0`` makes it normal
        again; commands already queued still wait for their reads.
        """
        self.device(device_id)
        if reads < 0:
            raise ValueError("reads must be 0 or more")
        if reads:
            self._slow[device_id] = reads
        else:
            self._slow.pop(device_id, None)

    def queued(self) -> dict[str, list[dict[str, Any]]]:
        """Commands accepted by slow devices and not applied yet (for /state and tests)."""
        return {
            device_id: [{"changes": dict(changes), "reads_left": left} for left, changes in items]
            for device_id, items in self._queued.items()
            if items
        }

    # -- commands ---------------------------------------------------------

    def read_state(self, device_id: str) -> dict[str, Any]:
        device = self.device(device_id)
        if self._failures.get(device_id) is FailureMode.OFFLINE:
            del self._failures[device_id]
            raise DeviceError(f"{device.name} is offline and did not respond")
        self._advance_queue(device)
        return copy.deepcopy(device.state)

    def _advance_queue(self, device: MockDevice) -> None:
        """One read passes for a slow device; commands whose wait is over are applied."""
        items = self._queued.get(device.device_id, [])
        for item in items:
            item[0] -= 1
        for left, changes in [i for i in items if i[0] <= 0]:
            device.state.update(changes)
            self.actions.append({"device_id": device.device_id, "changes": dict(changes)})
        self._queued[device.device_id] = [i for i in items if i[0] > 0]

    def apply(self, device_id: str, **changes: Any) -> dict[str, Any]:
        device = self.device(device_id)
        failure = self._failures.pop(device_id, None)
        if failure is FailureMode.OFFLINE:
            raise DeviceError(f"{device.name} is offline and did not respond")
        if device_id in self._slow:
            self._queued.setdefault(device_id, []).append([self._slow[device_id], dict(changes)])
            raise CommandAccepted(f"{device.name} accepted the command; it takes effect later")
        device.state.update(changes)
        self.actions.append({"device_id": device_id, "changes": dict(changes)})
        if failure is FailureMode.LOST_ACK:
            raise DeviceError(f"{device.name} did not confirm the command (timeout)")
        return copy.deepcopy(device.state)


class MockHomeAdapter:
    """Publishes a ``MockHome`` as catalog tools under one provider and one domain."""

    def __init__(
        self,
        home: MockHome,
        provider: str = MOCK_HOME_PROVIDER,
        *,
        journal: ActionJournal | None = None,
        pending_timeout_seconds: float | None = None,
    ) -> None:
        self.home = home
        self.provider = validate_identifier(provider, "provider")
        self.service = DeviceService(
            home, journal=journal, pending_timeout_seconds=pending_timeout_seconds
        )

    def sync_into(self, catalog: ToolCatalog, *, pinned: bool = False) -> SyncReport:
        """Publish the current device set; call again after the home changes."""
        report = catalog.sync(self.provider, self.tools(), pinned=pinned)
        catalog.describe_domain(MOCK_HOME_DOMAIN, self._domain_summary())
        return report

    def _domain_summary(self) -> str:
        listing = ", ".join(f"{d.name} ({d.room})" for d in self.home.devices())
        return f"Perangkat rumah, lihat dan ubah status lampu dan AC: {listing}"

    def tools(self) -> list[tuple[ToolContract, Callable[..., Any]]]:
        return build_device_tools(self.service, MOCK_HOME_DOMAIN)

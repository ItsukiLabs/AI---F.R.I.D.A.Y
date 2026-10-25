"""The one path every device command goes through, whatever the adapter.

A ``DeviceDriver`` is the thin, protocol-specific part (the mock home now;
Home Assistant / MQTT later): describe devices, read one device's state,
apply changes. ``DeviceService`` adds what must behave the same for every
driver:

- the shadow: ``desired`` (last requested, kept on failure) and the last
  known ``reported`` state with its time, so an offline read still says
  what was last seen instead of nothing;
- validation of every change against the device's capabilities before the
  driver is touched (defense in depth behind the tool's JSON schema);
- an ``operation_id`` and a final ``CommandStatus`` per command;
- the A2 rule (decided 2026-10-23): when a command errors, read the state
  back and report what the device actually is. Values are compared with
  each capability's tolerance, not exact equality;
- pending commands (stage 3): a slow device that accepts a command but
  confirms it later raises ``CommandAccepted``; the operation stays
  ``PENDING`` until a later read shows the change, then becomes
  ``SUCCEEDED`` (``get_operation``).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Protocol

from backend.schemas.device_contract import (
    CommandStatus,
    DeviceCommandResult,
    DeviceDescriptor,
    DeviceSnapshot,
)


class DeviceError(RuntimeError):
    """A device refused, did not answer, or did not confirm a command."""


class CommandAccepted(Exception):
    """Raised by a driver when a slow device accepted a command it will apply later.

    Not a failure, so not a ``DeviceError``: the service must not read the
    state back and call it "failed" just because the change hasn't happened yet.
    """


class DeviceDriver(Protocol):
    def descriptors(self) -> list[DeviceDescriptor]: ...

    def read_state(self, device_id: str) -> dict[str, Any]: ...

    def apply(self, device_id: str, **changes: Any) -> dict[str, Any]: ...


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DeviceService:
    def __init__(self, driver: DeviceDriver, clock: Callable[[], str] = _now) -> None:
        self.driver = driver
        self._clock = clock
        self._reported: dict[str, tuple[dict[str, Any], str]] = {}
        self._desired: dict[str, tuple[dict[str, Any], str]] = {}
        self._operations: dict[str, DeviceCommandResult] = {}
        self._pending: dict[str, list[str]] = {}

    def get_operation(self, operation_id: str) -> DeviceCommandResult | None:
        """The latest known result of a command (a pending one may have settled since)."""
        return self._operations.get(operation_id)

    # -- devices ----------------------------------------------------------

    def list_devices(self) -> list[DeviceDescriptor]:
        return self.driver.descriptors()

    def descriptor(self, device_id: str) -> DeviceDescriptor:
        for descriptor in self.driver.descriptors():
            if descriptor.device_id == device_id:
                return descriptor
        raise DeviceError(f"no device with id {device_id!r}")

    # -- state ------------------------------------------------------------

    def read_state(self, device_id: str) -> DeviceSnapshot:
        """Fresh state when the device answers; last known state, ``stale``, when it doesn't."""
        descriptor = self.descriptor(device_id)
        try:
            self._read(device_id)
            connection = "online"
        except DeviceError:
            connection = "offline"
        return self._snapshot(descriptor, connection)

    def _read(self, device_id: str) -> dict[str, Any]:
        reported = self.driver.read_state(device_id)
        self._reported[device_id] = (dict(reported), self._clock())
        self._settle_pending(device_id, reported)
        return reported

    def _settle_pending(self, device_id: str, reported: dict[str, Any]) -> None:
        """A pending command whose changes now show up in ``reported`` has succeeded."""
        waiting = self._pending.get(device_id)
        if not waiting:
            return
        descriptor = self.descriptor(device_id)
        for operation_id in list(waiting):
            operation = self._operations[operation_id]
            if self._matches(descriptor, operation.requested, reported):
                self._operations[operation_id] = operation.model_copy(
                    update={
                        "status": CommandStatus.SUCCEEDED,
                        "reported": dict(reported),
                        "message": "confirmed by a later read of the device state",
                    }
                )
                waiting.remove(operation_id)

    def _snapshot(self, descriptor: DeviceDescriptor, connection: str) -> DeviceSnapshot:
        reported, reported_at = self._reported.get(descriptor.device_id, ({}, None))
        desired, desired_at = self._desired.get(descriptor.device_id, ({}, None))
        pending = self._pending.get(descriptor.device_id, [])
        notes = []
        if connection != "online":
            notes.append(
                f"{descriptor.name} did not answer. 'reported' is the last known state"
                + (f" (from {reported_at})" if reported_at else " (none known yet)")
                + "; do not present it as the current state."
            )
        if pending:
            notes.append(
                f"{len(pending)} command(s) accepted but not confirmed yet; 'desired' shows "
                "what was asked. Do not say it is done until 'reported' shows it."
            )
        return DeviceSnapshot(
            device_id=descriptor.device_id,
            connection=connection,
            reported=dict(reported),
            reported_at=reported_at,
            stale=connection != "online",
            desired=dict(desired),
            desired_at=desired_at,
            in_sync=self._matches(descriptor, desired, reported),
            pending_operations=list(pending),
            message=" ".join(notes) or None,
        )

    @staticmethod
    def _matches(descriptor: DeviceDescriptor, requested: dict[str, Any], reported: dict[str, Any]) -> bool:
        for key, value in requested.items():
            capability = descriptor.capability(key)
            if key not in reported:
                return False
            if capability is None:
                if reported[key] != value:
                    return False
            elif not capability.matches(value, reported[key]):
                return False
        return True

    # -- commands ---------------------------------------------------------

    def apply(self, device_id: str, changes: dict[str, Any]) -> DeviceCommandResult:
        """Validate, apply, and settle one command. Raises only for an invalid command.

        Invalid commands (unknown device, unknown or read-only key, wrong
        type, out of range) raise ``ValueError``/``DeviceError`` before the
        driver is touched. Everything else ends in a ``DeviceCommandResult``.
        """
        descriptor = self.descriptor(device_id)
        if not changes:
            raise ValueError("a command needs at least one change")
        for key, value in changes.items():
            capability = descriptor.capability(key)
            if capability is None:
                raise ValueError(f"{descriptor.name} has no {key!r}")
            capability.check(value)

        operation_id = uuid.uuid4().hex
        desired = dict(self._desired.get(device_id, ({}, None))[0])
        desired.update(changes)
        self._desired[device_id] = (desired, self._clock())

        def result(status: CommandStatus, reported: dict[str, Any] | None, message: str | None):
            outcome = DeviceCommandResult(
                operation_id=operation_id,
                device_id=device_id,
                status=status,
                requested=dict(changes),
                reported=reported,
                message=message,
            )
            self._operations[operation_id] = outcome
            if status is CommandStatus.PENDING:
                self._pending.setdefault(device_id, []).append(operation_id)
            return outcome

        try:
            reported = self.driver.apply(device_id, **changes)
        except CommandAccepted as exc:
            # No read-back: the change is expected later, and reading now would
            # only show the old state. ``reported`` is the last known state.
            last_known = self._reported.get(device_id)
            return result(
                CommandStatus.PENDING,
                dict(last_known[0]) if last_known else None,
                f"{exc}. Accepted but not confirmed yet: check later with a state read; "
                "do not tell the user it is done.",
            )
        except DeviceError as exc:
            try:
                actual = self._read(device_id)
            except DeviceError:
                return result(
                    CommandStatus.UNKNOWN, None, f"{exc}. Read-back failed too; actual state unknown."
                )
            if self._matches(descriptor, changes, actual):
                return result(
                    CommandStatus.SUCCEEDED,
                    actual,
                    f"{exc}, but reading the state back shows the change took effect.",
                )
            return result(CommandStatus.FAILED, actual, f"{exc}. Actual state read back: {actual}")

        self._reported[device_id] = (dict(reported), self._clock())
        if self._matches(descriptor, changes, reported):
            return result(CommandStatus.SUCCEEDED, reported, None)
        return result(
            CommandStatus.FAILED,
            reported,
            f"{descriptor.name} answered, but reports a different state: {reported}",
        )

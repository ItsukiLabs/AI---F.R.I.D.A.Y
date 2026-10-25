"""Catalog tools for any device adapter, generated from device capabilities.

The model sees narrow, typed tools ("turn a device on", "set a target
temperature"), which keeps descriptions, schemas and permission tiers
clear; underneath, every actuator goes through the one generic
``DeviceService.apply``. This is the split two reviews recommended
(2026-10-25): specific tools for the LLM, a generic adapter inside.

Tools:

- ``home_list_devices``, ``home_get_state``: read-only;
- ``home_set_power``: devices with the ``on`` capability;
- ``home_set_<capability>`` for every other writable capability (e.g.
  ``home_set_brightness``, ``home_set_target_temperature``). Setting one
  also turns the device on when it has a power switch, so "a bit dark in
  here" is one call.

A command that ``failed`` or is ``unknown`` raises ``DeviceError`` with the
result in the message, so the loop reports it to the model as a tool error
and the model can't mistake it for success. A ``pending`` command (slow
device, stage 3) is returned normally with a note: it isn't a failure, but
it isn't done either.

Every actuator description carries the clarifying rule from Sasha
(PAPER_NOTES.md #5): when the user's words fit more than one device, ask
which one instead of guessing.
"""

from __future__ import annotations

import json
from typing import Any, Callable

from backend.devices.service import DeviceError, DeviceService
from backend.schemas import PermissionTier, ToolAnnotations, ToolContract, ToolExample
from backend.schemas.device_contract import POWER, Capability, CommandStatus, DeviceDescriptor

_READ_ONLY = ToolAnnotations(
    read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=True
)
# Physical side effect, but reversible and safe to repeat with the same arguments.
_ACTUATOR = ToolAnnotations(
    read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=True
)

# Trigger phrases per standard capability (EasyTool: a scenario with arguments
# is the cheapest, most effective improvement to a tool description).
_SET_EXAMPLES: dict[str, tuple[str, Any]] = {
    "brightness": ("User: 'agak gelap nih di ruang tamu'", 80),
    "target_temperature": ("User: 'AC kamar dingin banget, naikin suhunya'", 26),
}


def _object(properties: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": sorted(properties),
        "additionalProperties": False,
    }


# Appended to every actuator tool description (stage 3, disambiguation).
ASK_WHICH_DEVICE = (
    " If the user's words fit more than one device (e.g. two lamps in the same "
    "room) and they did not say which, do not call this tool: ask which one first."
)

PENDING_NOTE = (
    "The device accepted the command but has not confirmed it yet. Tell the user "
    "it was sent and is still in progress; do not say it is done. Check later "
    "with home_get_state."
)


def _settle(service: DeviceService, device_id: str, changes: dict[str, Any]) -> dict[str, Any]:
    outcome = service.apply(device_id, changes)
    payload = outcome.model_dump(mode="json", exclude_none=True)
    if outcome.status is CommandStatus.PENDING:
        return {**payload, "note": PENDING_NOTE}
    if outcome.status is not CommandStatus.SUCCEEDED:
        raise DeviceError(
            f"{outcome.message or 'command not confirmed'} "
            f"[status={outcome.status.value}, operation_id={outcome.operation_id}, "
            f"result={json.dumps(payload, ensure_ascii=False)}]"
        )
    return payload


def build_device_tools(
    service: DeviceService, domain: str
) -> list[tuple[ToolContract, Callable[..., Any]]]:
    devices = service.list_devices()

    def home_list_devices() -> dict[str, Any]:
        return {
            "devices": [
                {
                    "device_id": d.device_id,
                    "name": d.name,
                    "room": d.room,
                    "kind": d.kind,
                    "capabilities": [c.name for c in d.capabilities],
                }
                for d in service.list_devices()
            ]
        }

    tools: list[tuple[ToolContract, Callable[..., Any]]] = [
        (
            ToolContract(
                name="home_list_devices",
                version="1.1.0",
                domain=domain,
                description=(
                    "List every device in the home with its id, name, room, kind "
                    "and capabilities (the state keys it has)."
                ),
                input_schema={"type": "object", "properties": {}, "additionalProperties": False},
                annotations=_READ_ONLY,
                permission_tier=PermissionTier.READ_ONLY,
                examples=[ToolExample(scenario="User: 'perangkat apa saja yang ada di rumah?'")],
            ),
            home_list_devices,
        )
    ]
    if not devices:
        return tools

    def device_property(with_capability: str | None) -> dict[str, Any]:
        chosen = [
            d for d in devices if with_capability is None or d.capability(with_capability) is not None
        ]
        names = "; ".join(f"{d.device_id} = {d.name} ({d.room})" for d in chosen)
        return {
            "type": "string",
            "enum": sorted(d.device_id for d in chosen),
            "description": f"Which device. {names}",
        }

    sample = next((d for d in devices if d.capability(POWER.name)), devices[0])

    def home_get_state(device_id: str) -> dict[str, Any]:
        return service.read_state(device_id).model_dump(mode="json")

    tools.append(
        (
            ToolContract(
                name="home_get_state",
                version="2.0.0",
                domain=domain,
                description=(
                    "Read a device's state. 'reported' is what the device says now "
                    "(e.g. on/off, brightness, target_temperature, current_temperature "
                    "= measured room temperature); 'desired' is what was last requested; "
                    "'connection' says whether the device answered (if not, 'reported' is "
                    "the last known value and 'stale' is true). Use it to check whether "
                    "an earlier command really took effect."
                ),
                input_schema=_object({"device_id": device_property(None)}),
                annotations=_READ_ONLY,
                permission_tier=PermissionTier.READ_ONLY,
                examples=[
                    ToolExample(
                        scenario="User: 'lampunya udah nyala belum?'",
                        arguments={"device_id": sample.device_id},
                    )
                ],
            ),
            home_get_state,
        )
    )

    powered = [d for d in devices if d.capability(POWER.name)]
    if powered:

        def home_set_power(device_id: str, on: bool) -> dict[str, Any]:
            return _settle(service, device_id, {"on": on})

        tools.append(
            (
                ToolContract(
                    name="home_set_power",
                    version="2.0.0",
                    domain=domain,
                    description=(
                        "Turn a device (lamp or AC) on or off. Returns the command "
                        "result with the state the device reports."
                    )
                    + ASK_WHICH_DEVICE,
                    input_schema=_object(
                        {
                            "device_id": device_property(POWER.name),
                            "on": {"type": "boolean", "description": "true = on, false = off"},
                        }
                    ),
                    annotations=_ACTUATOR,
                    permission_tier=PermissionTier.STANDARD,
                    examples=[
                        ToolExample(
                            scenario="User: 'nyalakan lampu ruang tamu'",
                            arguments={"device_id": powered[0].device_id, "on": True},
                        )
                    ],
                ),
                home_set_power,
            )
        )

    for capability in _settable_capabilities(devices):
        tools.append(_set_tool(service, domain, capability, devices, device_property))
    return tools


def _settable_capabilities(devices: list[DeviceDescriptor]) -> list[Capability]:
    seen: dict[str, Capability] = {}
    for device in devices:
        for capability in device.capabilities:
            if capability.writable and capability.name != POWER.name:
                seen.setdefault(capability.name, capability)
    return [seen[name] for name in sorted(seen)]


def _set_tool(
    service: DeviceService,
    domain: str,
    capability: Capability,
    devices: list[DeviceDescriptor],
    device_property: Callable[[str | None], dict[str, Any]],
) -> tuple[ToolContract, Callable[..., Any]]:
    key = capability.name
    first = next(d for d in devices if d.capability(key))

    def set_value(device_id: str, **arguments: Any) -> dict[str, Any]:
        changes = {key: arguments[key]}
        if service.descriptor(device_id).capability(POWER.name):
            changes = {"on": True, **changes}
        return _settle(service, device_id, changes)

    examples = []
    if key in _SET_EXAMPLES:
        scenario, value = _SET_EXAMPLES[key]
        examples.append(
            ToolExample(scenario=scenario, arguments={"device_id": first.device_id, key: value})
        )
    unit = f" ({capability.unit})" if capability.unit else ""
    return (
        ToolContract(
            name=f"home_set_{key}",
            version="1.0.0",
            domain=domain,
            description=(
                f"Set a device's {capability.description}{unit}; turns the device on "
                "if it has a power switch. Returns the command result."
            )
            + ASK_WHICH_DEVICE,
            input_schema=_object(
                {"device_id": device_property(key), key: capability.json_schema()}
            ),
            annotations=_ACTUATOR,
            permission_tier=PermissionTier.STANDARD,
            examples=examples,
        ),
        set_value,
    )

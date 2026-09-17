"""Example tool: get the current time.

Read-only, deterministic enough to test, and needs no IoT/OS integration
that doesn't exist yet (M4/M5) — used to exercise the M1 loop end to end
against a real (if trivial) capability instead of a mock.
"""

from datetime import datetime, timezone
from typing import Any

from backend.schemas import PermissionTier, ToolAnnotations, ToolContract, ToolExample

TIME_TOOL_CONTRACT = ToolContract(
    name="get_current_time",
    version="1.0.0",
    domain="time",
    examples=[
        ToolExample(scenario="User: 'Jam berapa sekarang?'", arguments={}),
        ToolExample(scenario="User asks what today's date is", arguments={}),
    ],
    description="Get the current date and time in UTC, ISO 8601 format.",
    input_schema={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    output_schema={
        "type": "object",
        "properties": {"iso_datetime": {"type": "string"}},
        "required": ["iso_datetime"],
    },
    annotations=ToolAnnotations(
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=False,
    ),
    permission_tier=PermissionTier.READ_ONLY,
)


def get_current_time() -> dict[str, Any]:
    return {"iso_datetime": datetime.now(timezone.utc).isoformat()}

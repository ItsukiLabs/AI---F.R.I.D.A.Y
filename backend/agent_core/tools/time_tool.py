"""Example tool: get the current time.

Read-only, deterministic enough to test, and needs no IoT/OS integration
that doesn't exist yet (M4/M5) — used to exercise the M1 loop end to end
against a real (if trivial) capability instead of a mock.

Returns local time: the zone from ``FRIDAY_TIMEZONE`` (an IANA name such as
``Asia/Jakarta``), or the OS local zone when it isn't set. The first smoke
test with a real model (2026-10-23) answered in UTC, which is wrong for a
user who lives in one place.
"""

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from backend.agent_core.config import get_timezone_name
from backend.schemas import PermissionTier, ToolAnnotations, ToolContract, ToolExample

TIME_TOOL_CONTRACT = ToolContract(
    name="get_current_time",
    version="1.1.0",
    domain="time",
    examples=[
        ToolExample(scenario="User: 'Jam berapa sekarang?'", arguments={}),
        ToolExample(scenario="User asks what today's date is", arguments={}),
    ],
    description=(
        "Get the current local date and time in the user's time zone "
        "(ISO 8601 with UTC offset, plus the zone name)."
    ),
    input_schema={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    output_schema={
        "type": "object",
        "properties": {
            "iso_datetime": {"type": "string"},
            "timezone": {"type": "string"},
            "utc_offset": {"type": "string"},
        },
        "required": ["iso_datetime", "timezone", "utc_offset"],
    },
    annotations=ToolAnnotations(
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=False,
    ),
    permission_tier=PermissionTier.READ_ONLY,
)


def _format_offset(now: datetime) -> str:
    offset = now.utcoffset()
    minutes = int(offset.total_seconds() // 60) if offset is not None else 0
    sign = "+" if minutes >= 0 else "-"
    hours, minutes = divmod(abs(minutes), 60)
    return f"{sign}{hours:02d}:{minutes:02d}"


def get_current_time(now: datetime | None = None) -> dict[str, Any]:
    """``now`` is for tests (an aware datetime); callers pass nothing."""
    name = get_timezone_name()
    if name is not None:
        now = (now or datetime.now(ZoneInfo(name))).astimezone(ZoneInfo(name))
        zone = name
    else:
        now = (now or datetime.now()).astimezone()
        zone = now.tzname() or "local"
    return {"iso_datetime": now.isoformat(), "timezone": zone, "utc_offset": _format_offset(now)}

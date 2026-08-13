"""Explicit tool registration list — small enough that auto-discovery isn't worth it."""

from backend.agent_core.tools.time_tool import TIME_TOOL_CONTRACT, get_current_time

ALL_TOOLS = [
    (TIME_TOOL_CONTRACT, get_current_time),
]

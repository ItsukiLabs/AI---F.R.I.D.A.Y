"""M4: keep recently used catalog tools loaded across turns (MemTool-style retention).

A turn's registry starts fresh, so a tool the model loaded with
``find_tools`` in one turn is gone in the next ("turn on the lamp", then
"turn it off again" needs another search). Instead of storing extra state,
retention is derived from the stored conversation: catalog tools that were
called *successfully* in the last N turns are loaded again. It survives a
restart and needs no change to ``SessionRecord``.

Only successful calls count. A call rejected because the tool was not
loaded (``ToolNotLoadedError``) is an error result, so it never earns a
tool a place in the next turn: tools that change the world still have to
be found deliberately at least once (MemTool, arXiv 2507.21428, keeps tools
by use too).
"""

from __future__ import annotations

from typing import Any

DEFAULT_TOOL_RETENTION_TURNS = 3


def recently_used_tool_names(messages: list[dict[str, Any]], turns: int | None) -> list[str]:
    """Names of tools called successfully in the last ``turns`` turns, most recent first.

    A turn starts at a plain-text user message. ``turns=None`` looks at the
    whole stored conversation; ``turns=0`` returns nothing.
    """
    if turns is not None and turns <= 0:
        return []

    succeeded = {
        block["tool_use_id"]
        for m in messages
        if m["role"] == "user" and isinstance(m["content"], list)
        for block in m["content"]
        if block.get("type") == "tool_result" and not block.get("is_error")
    }

    names: list[str] = []
    seen_turns = 0
    for message in reversed(messages):
        if message["role"] == "user" and isinstance(message["content"], str):
            seen_turns += 1
            if turns is not None and seen_turns >= turns:
                break
            continue
        if message["role"] != "assistant" or not isinstance(message["content"], list):
            continue
        for block in message["content"]:
            if (
                block.get("type") == "tool_use"
                and block.get("id") in succeeded
                and block["name"] not in names
            ):
                names.append(block["name"])
    return names

"""M2b recall tool: recall_memory.

The MemGPT "archival search" idea as an explicit tool: the model decides
when to look into past conversations, the same way it decides when to call
remember_user_fact (M2c). Nothing is injected automatically every turn.

Built by ``make_recall_tools(archive, current_session)`` and bound to a live
``ArchiveStore`` — like profile_tools.py, not part of the static ALL_TOOLS
list. The closure carries no try/except: backend/agent_core/loop.py's
``_execute_tool_call`` already turns any exception (e.g. ArchiveLoadError)
into a verbal tool_result observation.

The tool description is load-bearing for the project's "context ≠ memory"
principle: hits are verbatim quotes of what was said at the time, dated
and attributed, and the model is told to treat them as such — never to
restate them as current facts. Durable facts still only enter through
remember_user_fact; this tool never writes.
"""

from __future__ import annotations

from typing import Any, Callable

from backend.agent_core.config import get_memory_recall_default_limit
from backend.memory.archive_store import ArchiveStore
from backend.memory.session import Session
from backend.schemas import PermissionTier, ToolAnnotations, ToolContract, ToolExample

RECALL_MAX_TEXT_CHARS = 600
RECALL_MAX_LIMIT = 20

RECALL_MEMORY_CONTRACT = ToolContract(
    name="recall_memory",
    version="1.0.0",
    domain="memory",
    examples=[
        ToolExample(
            scenario="User: 'Minggu lalu kita bahas resep apa ya?'",
            arguments={"query": "resep"},
        ),
        ToolExample(
            scenario="User asks what they said earlier about their trip to Bali",
            arguments={"query": "Bali trip", "limit": 3},
        ),
    ],
    description=(
        "Search F.R.I.D.A.Y's archive of past conversation turns across ALL "
        "previous sessions, by keyword. Results are VERBATIM QUOTES of what "
        "was said at the time (by the user or by you), each with the session "
        "it came from and when it was indexed (normally the moment it was "
        "said). They are NOT verified facts: they may be outdated, superseded "
        "by later conversations, or one-off remarks. Present them as \"in an "
        "earlier conversation you said...\", never restate them as current "
        "truth. Turns already visible in the current conversation are not "
        "returned. If the user wants something remembered durably as a fact, "
        "use remember_user_fact instead — this tool never writes anything."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "minLength": 1,
                "maxLength": 500,
                "description": (
                    "Keywords (Indonesian or English) likely to appear verbatim "
                    "in the past turn. Fewer, specific words work best."
                ),
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": RECALL_MAX_LIMIT,
                "description": "Maximum number of hits to return; omit for the default.",
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    },
    output_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "count": {"type": "integer"},
            "hits": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "ordinal": {"type": "integer"},
                        "role": {"type": "string"},
                        "text": {"type": "string"},
                        "session_started_at": {"type": "string"},
                        "indexed_at": {"type": "string"},
                        "truncated": {"type": "boolean"},
                    },
                    "required": [
                        "session_id",
                        "ordinal",
                        "role",
                        "text",
                        "session_started_at",
                        "indexed_at",
                        "truncated",
                    ],
                },
            },
            "note": {"type": "string"},
        },
        "required": ["query", "count", "hits"],
    },
    annotations=ToolAnnotations(
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
    permission_tier=PermissionTier.READ_ONLY,
)


def make_recall_tools(
    archive: ArchiveStore,
    current_session: Session | None = None,
) -> list[tuple[ToolContract, Callable[..., Any]]]:
    """Bind recall_memory to ``archive``.

    ``current_session`` (when given) has its live, in-context window
    excluded from results. The cutoff is read *when the tool is called*,
    not when it's built: compaction runs at the top of ``run_agent()``,
    after the registry has been composed, and moves turns out of the live
    window — a snapshot taken here would be stale by then.
    """

    def recall_memory(query: str, limit: int | None = None) -> dict[str, Any]:
        effective_limit = min(limit or get_memory_recall_default_limit(), RECALL_MAX_LIMIT)
        exclude = None
        if current_session is not None:
            exclude = (current_session.session_id, len(current_session.archived_turns))

        hits = archive.search(query, limit=effective_limit, exclude=exclude)

        rendered = []
        for hit in hits:
            payload = hit.model_dump()
            truncated = len(hit.text) > RECALL_MAX_TEXT_CHARS
            if truncated:
                payload["text"] = hit.text[:RECALL_MAX_TEXT_CHARS] + " …"
            payload["truncated"] = truncated
            rendered.append(payload)

        result: dict[str, Any] = {"query": query, "count": len(rendered), "hits": rendered}
        if not rendered:
            result["note"] = (
                "No past conversation turns matched. Try fewer or different keywords."
            )
        return result

    return [(RECALL_MEMORY_CONTRACT, recall_memory)]

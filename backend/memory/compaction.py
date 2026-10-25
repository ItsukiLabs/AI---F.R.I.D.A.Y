"""Recursive-summarization compaction for M2a active context.

Anthropic's Messages API rejects a message list that splits a ``tool_use``
block from its paired ``tool_result``. The only universally safe cut point
is immediately before a plain new user turn, and a single ``run_agent()``
call only ever introduces one such turn, at its own start — so compaction
is structurally a between-calls concern, never triggered mid-loop.

Follows "Recursively Summarizing Enables Long-Term Dialogue Memory"
(Memory Think/PAPER_NOTES.md, category #2): each compaction folds
``old_summary + next_chunk -> new_summary`` via an LLM call, rather than
re-summarizing from scratch or truncating outright.
"""

from __future__ import annotations

import json
from typing import Any

from backend.agent_core.llm_client import LLMClient
from backend.memory.errors import CompactionError
from backend.memory.session import Session

SUMMARIZATION_SYSTEM_PROMPT = (
    "You are compacting a conversation transcript for F.R.I.D.A.Y's short-term "
    "memory. Write a concise summary, roughly under 250 words, that preserves "
    "whatever is most useful for continuing this conversation: facts the user "
    "explicitly stated, decisions made, unresolved questions, and commitments "
    "the assistant made.\n\n"
    "Stay strictly literal: record only what was actually said. Never invent "
    "details, and never promote an incidental statement into a general "
    "preference or trait unless the user stated it as one — for example, "
    "'I ate fried rice today' must stay a one-time event in the summary, not "
    "become 'the user likes fried rice'. Output only the summary text."
)


def _find_safe_cut_index(messages: list[dict[str, Any]], keep_recent_messages: int) -> int | None:
    """Nearest safe boundary at/before ``len(messages) - keep_recent_messages``.

    A boundary is safe when it lands on a plain user turn (never inside a
    tool_use/tool_result pair) and leaves at least one message to fold into
    the summary — a cut at index 0 would summarize nothing.
    """
    limit = len(messages) - keep_recent_messages
    if limit <= 0:
        return None
    for i in range(min(limit, len(messages) - 1), 0, -1):
        message = messages[i]
        if message["role"] == "user" and isinstance(message["content"], str):
            return i
    return None


def _render_transcript(chunk: list[dict[str, Any]]) -> str:
    lines = []
    for message in chunk:
        content = message["content"]
        text = content if isinstance(content, str) else json.dumps(content)
        lines.append(f"{message['role']}: {text}")
    return "\n".join(lines)


def _build_summarization_messages(
    old_summary: str | None, chunk: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    prefix = f"Existing summary of earlier conversation:\n{old_summary}\n\n" if old_summary else ""
    return [
        {
            "role": "user",
            "content": (
                f"{prefix}New conversation excerpt to fold into the summary:\n"
                f"{_render_transcript(chunk)}\n\nWrite the updated summary now."
            ),
        }
    ]


def compact(session: Session, llm: LLMClient, keep_recent_messages: int = 6) -> bool:
    """Fold old turns into ``session.summary``, keeping the tail verbatim.

    Returns False (no-op) when there's no safe cut point — history too
    short, or nothing but one long tool-calling chain.

    Raises ``CompactionError`` when the LLM returns an empty summary, and
    lets an LLM exception propagate; in both cases the session is left
    exactly as it was. (Before 2026-10-25 an empty reply kept the old
    summary but still dropped the old turns from the active context.)
    """
    cut = _find_safe_cut_index(session.messages, keep_recent_messages)
    if cut is None:
        return False

    to_summarize = session.messages[:cut]
    remaining = session.messages[cut:]

    response = llm.send(
        messages=_build_summarization_messages(session.summary, to_summarize),
        tools=[],
        system=SUMMARIZATION_SYSTEM_PROMPT,
    )

    summary = (response.text or "").strip()
    if not summary:
        raise CompactionError(
            f"the model returned an empty summary for {len(to_summarize)} message(s)"
        )

    session.summary = summary
    session.archived_turns.extend(to_summarize)  # M2b hook — not read/pruned by M2a
    session.messages = remaining
    session.compaction_count += 1
    return True

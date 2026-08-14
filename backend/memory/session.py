"""Runtime session state for M2a short-term memory.

Wraps ``SessionRecord`` (the on-disk shape, see schemas/memory_contract.py)
with the mutable helpers ``loop.py`` and ``compaction.py`` need.
``messages`` is the durable, storage-shape history — mutated in place and
persisted verbatim. ``to_llm_messages()`` is a presentation-only transform
computed fresh on every LLM call that prepends the running summary without
touching storage — that separation is what lets compaction solve the
Lost-in-the-Middle placement problem without complicating persistence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from backend.agent_core.llm_client import LLMResponse
from backend.schemas import MessageRecord, SessionRecord


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Session:
    session_id: str
    created_at: str
    updated_at: str
    messages: list[dict[str, Any]] = field(default_factory=list)
    summary: str | None = None
    archived_turns: list[dict[str, Any]] = field(default_factory=list)
    compaction_count: int = 0
    last_input_tokens: int | None = None
    last_output_tokens: int | None = None

    @classmethod
    def new(cls, session_id: str) -> Session:
        now = iso_now()
        return cls(session_id=session_id, created_at=now, updated_at=now)

    @classmethod
    def from_record(cls, record: SessionRecord) -> Session:
        return cls(
            session_id=record.session_id,
            created_at=record.created_at,
            updated_at=record.updated_at,
            messages=[m.model_dump() for m in record.messages],
            summary=record.summary,
            archived_turns=[m.model_dump() for m in record.archived_turns],
            compaction_count=record.compaction_count,
            last_input_tokens=record.last_input_tokens,
            last_output_tokens=record.last_output_tokens,
        )

    def to_record(self) -> SessionRecord:
        return SessionRecord(
            session_id=self.session_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            messages=[MessageRecord(**m) for m in self.messages],
            summary=self.summary,
            archived_turns=[MessageRecord(**m) for m in self.archived_turns],
            compaction_count=self.compaction_count,
            last_input_tokens=self.last_input_tokens,
            last_output_tokens=self.last_output_tokens,
        )

    def append_user_message(self, text: str) -> None:
        self.messages.append({"role": "user", "content": text})

    def record_usage(self, response: LLMResponse) -> None:
        self.last_input_tokens = response.input_tokens
        self.last_output_tokens = response.output_tokens

    def needs_compaction(self, threshold_tokens: int, safety_margin_tokens: int = 0) -> bool:
        """True once the last known usage, plus a safety margin, reaches the threshold.

        ``last_input_tokens`` is exact but one turn stale — it's the usage
        the *previous* call actually incurred, not this one. The margin
        compensates for that staleness without estimating the size of the
        turn about to be sent (see get_memory_compaction_safety_margin_tokens
        in agent_core/config.py for why that's deliberately not attempted).
        """
        return (
            self.last_input_tokens is not None
            and self.last_input_tokens + safety_margin_tokens >= threshold_tokens
        )

    def to_llm_messages(self) -> list[dict[str, Any]]:
        if not self.summary:
            return self.messages
        return [
            {"role": "user", "content": f"[Earlier conversation summary]\n{self.summary}"},
            {
                "role": "assistant",
                "content": "Understood — continuing with that context in mind.",
            },
        ] + self.messages

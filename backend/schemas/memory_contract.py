"""Session memory contract — the on-disk format for M2a short-term memory.

Unlike ``ToolContract`` (M0), a session file has only one axis of change:
the file format shape itself. There's no per-tool ``version`` to separate
from a ``contract_version``, so a single ``schema_version`` string is
right-sized here rather than echoing that split.

References: Memory Think/PAPER_NOTES.md, category #2 (MemGPT, Lost in the
Middle, Recursively Summarizing Enables Long-Term Dialogue Memory).
"""

from typing import Any, Literal

from pydantic import BaseModel, Field

MEMORY_SCHEMA_VERSION = "1.0.0"


class MessageRecord(BaseModel):
    """One conversation turn, mirroring the Anthropic Messages API wire format 1:1."""

    role: Literal["user", "assistant"]
    content: Any


class SessionRecord(BaseModel):
    """On-disk representation of one M2a conversation session."""

    schema_version: str = Field(default=MEMORY_SCHEMA_VERSION)
    session_id: str
    created_at: str
    updated_at: str
    messages: list[MessageRecord] = Field(default_factory=list)
    summary: str | None = None
    archived_turns: list[MessageRecord] = Field(default_factory=list)
    compaction_count: int = 0
    last_input_tokens: int | None = None
    last_output_tokens: int | None = None

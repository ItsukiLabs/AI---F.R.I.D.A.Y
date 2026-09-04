"""Profile memory contract — the on-disk format for M2c long-lived user facts.

Independent ``schema_version`` from ``memory_contract.py`` (M2a) on purpose:
a profile file and a session file are different axes of change (adding a
field to one must never force a version bump on the other), same reasoning
that already justified ``SessionRecord`` not reusing ``CONTRACT_VERSION``
from ``tool_contract.py`` (M0).

References: Memory Think/PAPER_NOTES.md, category #2 (MemGPT core memory;
MemoryBank/FSFM forgetting frameworks, whose decay/eviction logic is
deliberately NOT implemented yet — see Memory Think/M2_memory.md TODO).
"""

from typing import Literal

from pydantic import BaseModel, Field

PROFILE_SCHEMA_VERSION = "1.0.0"


class ProfileFact(BaseModel):
    """One durable fact about the user, only ever written via an explicit
    remember_user_fact tool call — never inferred automatically."""

    id: str
    text: str
    category: str
    status: Literal["active", "superseded", "deleted"] = "active"
    created_at: str
    updated_at: str
    supersedes: str | None = None
    superseded_by: str | None = None
    deleted_reason: str | None = None


class ProfileRecord(BaseModel):
    """On-disk representation of the (singleton) M2c user profile."""

    schema_version: str = Field(default=PROFILE_SCHEMA_VERSION)
    user_id: str = "primary"
    created_at: str
    updated_at: str
    facts: list[ProfileFact] = Field(default_factory=list)
    next_fact_seq: int = 0

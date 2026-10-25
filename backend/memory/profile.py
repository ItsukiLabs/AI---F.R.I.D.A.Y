"""Runtime profile state for M2c — durable, cross-session facts about the user.

Wraps ``ProfileRecord`` (the on-disk shape, see schemas/profile_contract.py)
with the mutable helpers the remember/forget tools need. Unlike ``Session``
(M2a, scoped to one conversation), ``Profile`` is a singleton shared across
every session — it's how F.R.I.D.A.Y recognizes the same user across a
brand new session_id, not just across a process restart.

Facts are only ever written through ``remember_fact``/``forget_fact``,
which are only ever called from the remember_user_fact/forget_user_fact
tools (backend/agent_core/tools/profile_tools.py) — this module has no
automatic/background extraction path by design (see Memory Think/M2_memory.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.memory.profile_errors import ProfileFactNotFoundError
from backend.memory.session import iso_now
from backend.schemas import ProfileFact, ProfileRecord


@dataclass
class Profile:
    user_id: str
    created_at: str
    updated_at: str
    facts: list[ProfileFact] = field(default_factory=list)
    next_fact_seq: int = 0
    dirty: bool = False

    @classmethod
    def new(cls, user_id: str = "primary") -> Profile:
        now = iso_now()
        return cls(user_id=user_id, created_at=now, updated_at=now)

    @classmethod
    def from_record(cls, record: ProfileRecord) -> Profile:
        return cls(
            user_id=record.user_id,
            created_at=record.created_at,
            updated_at=record.updated_at,
            facts=list(record.facts),
            next_fact_seq=record.next_fact_seq,
        )

    def to_record(self) -> ProfileRecord:
        return ProfileRecord(
            user_id=self.user_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            facts=self.facts,
            next_fact_seq=self.next_fact_seq,
        )

    def _find(self, fact_id: str) -> ProfileFact | None:
        for fact in self.facts:
            if fact.id == fact_id:
                return fact
        return None

    def active_facts(self) -> list[ProfileFact]:
        return [f for f in self.facts if f.status == "active"]

    def remember_fact(self, text: str, category: str, supersedes: str | None = None) -> ProfileFact:
        """Append a new active fact, optionally superseding an existing active one.

        ``supersedes`` must name a currently *active* fact — superseding a
        fact that's already superseded/deleted, or one that doesn't exist,
        raises rather than silently creating a dangling/ambiguous link.
        """
        if supersedes is not None:
            old = self._find(supersedes)
            if old is None or old.status != "active":
                raise ProfileFactNotFoundError(
                    f"cannot supersede {supersedes!r}: no active fact with that id"
                )

        self.next_fact_seq += 1
        now = iso_now()
        new_fact = ProfileFact(
            id=f"fact_{self.next_fact_seq:04d}",
            text=text,
            category=category,
            status="active",
            created_at=now,
            updated_at=now,
            supersedes=supersedes,
        )
        self.facts.append(new_fact)

        if supersedes is not None:
            old = self._find(supersedes)
            assert old is not None  # validated above
            old.status = "superseded"
            old.superseded_by = new_fact.id
            old.updated_at = now

        self.updated_at = now
        self.dirty = True
        return new_fact

    def forget_fact(self, fact_id: str, reason: str | None = None) -> ProfileFact:
        """Mark a fact deleted. Idempotent: forgetting an already-deleted
        fact is a no-op success, not an error — repeating "forget X" must
        never fail just because it already happened."""
        fact = self._find(fact_id)
        if fact is None:
            raise ProfileFactNotFoundError(f"no fact with id {fact_id!r}")

        if fact.status == "deleted":
            return fact

        now = iso_now()
        fact.status = "deleted"
        fact.deleted_reason = reason
        fact.updated_at = now
        self.updated_at = now
        self.dirty = True
        return fact

    def to_context_block(self) -> str:
        """Render active facts for injection into the system prompt.

        Empty string when there's nothing active — callers append this
        conditionally so an empty profile never adds a stray empty section.
        """
        active = self.active_facts()
        if not active:
            return ""
        lines = [f"- [{f.id}] ({f.category}) {f.text}" for f in active]
        return (
            "Known facts about the user. These were saved on purpose with "
            "remember_user_fact and are your primary source about the user: "
            "answer from them directly, without calling recall_memory. Use "
            "recall_memory only for things said in past conversations that "
            "are not listed here. Cite the id in brackets if you need to "
            "supersede or forget one.\n"
            + "\n".join(lines)
        )

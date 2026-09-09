"""Archive contract — the shape of one M2b long-term recall hit, and the
schema version of the SQLite archive that produces it.

Independent ``ARCHIVE_SCHEMA_VERSION`` for the same reason ``PROFILE_SCHEMA_VERSION``
is independent of ``MEMORY_SCHEMA_VERSION``: the archive database and the
session/profile JSON files are separate axes of change. Adding a column to
the archive must never force a version bump on session files (which would
make every existing session unloadable — SessionStore has no migration).

Unlike the other contracts there is no on-disk pydantic *record* here: the
durable shape is the SQLite DDL in backend/memory/archive_store.py. What
crosses the boundary into the agent loop is a ``RecallHit`` — a verbatim
quote of a past turn plus its provenance.

References: Memory Think/PAPER_NOTES.md, category #2 ("Storage Is Not
Memory" — retrieval-centered archive over verbatim events; MemGPT —
archival search as an explicit tool).
"""

from typing import Literal

from pydantic import BaseModel

ARCHIVE_SCHEMA_VERSION = "1.0.0"


class RecallHit(BaseModel):
    """One past conversation turn returned by ``ArchiveStore.search``.

    ``text`` is the searchable rendering of the turn (plain user/assistant
    text, or a flattened view of tool_use/tool_result blocks) — a quote of
    what was said at the time, never a derived fact.

    ``session_started_at`` is the ``Session.created_at`` of the conversation
    it came from; ``indexed_at`` is when the archive recorded it. They differ
    only for sessions that predate M2b and were backfilled on first ingest.
    """

    session_id: str
    ordinal: int
    role: Literal["user", "assistant"]
    text: str
    session_started_at: str
    indexed_at: str

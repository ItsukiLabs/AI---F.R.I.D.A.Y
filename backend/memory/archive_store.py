"""SQLite + FTS5 persistence for M2b long-term recall.

One database file at ``<base_dir>/memory.db`` holding every turn of every
session, verbatim. Retrieval-centered by design (see "Storage Is Not
Memory", Memory Think/PAPER_NOTES.md category #2): nothing is extracted,
summarized, or interpreted at ingest — what's discarded before the query
is known can't be recovered at retrieval time. All the intelligence lives
in ``search()``, over raw events. No embeddings, no vector index, no
external service; ``sqlite3`` is stdlib.

Ingest is **idempotent per session generation**. A session's full ordered
history is always ``archived_turns + messages`` (compaction only ever moves
turns from the latter to the former, so the total only grows), and the
archive remembers how many of those it has already stored, keyed on
``(session_id, session_created_at)``. ``created_at`` is what distinguishes
two different conversations that happened to reuse the same ``session_id``
(a session file deleted and recreated) — without it, turns from the new
conversation would be numbered as if they continued the old one.

Same two robustness properties as SessionStore/ProfileStore, duplicated
rather than shared for the same reason ProfileStore duplicated them:

1. **Transactional writes.** ``ingest()`` runs in one transaction — a crash
   mid-ingest rolls back to the previous ingested_count, and the next turn
   catches up.
2. **Fail loud on untrustworthy data.** A database file that exists but is
   corrupt, not SQLite, from a foreign schema, or from an unsupported
   schema version raises a specific exception rather than behaving like an
   empty archive.

Concurrent writers are out of scope (single-writer assumption, same as
M2a/M2c) — SQLite's own locking makes it safe, not fast.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import stat
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from backend.memory.archive_errors import (
    ArchiveError,
    ArchiveLoadError,
    ArchiveSaveError,
    UnsupportedArchiveSchemaError,
)
from backend.memory.session import Session, iso_now
from backend.schemas import ARCHIVE_SCHEMA_VERSION, RecallHit

DEFAULT_ARCHIVE_DIR = Path(__file__).parent / "archive"

_ARCHIVE_FILENAME = "memory.db"

# Word tokens as FTS5's unicode61 tokenizer would see them. Anything else in a
# query (quotes, parentheses, '*', '-', operator keywords) is syntax to FTS5
# and can never reach it through this pattern — each token is then quoted as
# a phrase, so even "AND"/"OR"/"NOT" become plain literals.
_TOKEN_PATTERN = re.compile(r"[^\W_]+")

_SCHEMA_DDL = """
CREATE TABLE meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE sessions_ingest (
    session_id         TEXT    NOT NULL,
    session_created_at TEXT    NOT NULL,
    ingested_count     INTEGER NOT NULL,
    last_ingested_at   TEXT    NOT NULL,
    PRIMARY KEY (session_id, session_created_at)
);

CREATE TABLE turns (
    id                 INTEGER PRIMARY KEY,
    session_id         TEXT    NOT NULL,
    session_created_at TEXT    NOT NULL,
    ordinal            INTEGER NOT NULL,
    role               TEXT    NOT NULL,
    text               TEXT    NOT NULL,
    content_json       TEXT    NOT NULL,
    ingested_at        TEXT    NOT NULL,
    UNIQUE (session_id, session_created_at, ordinal)
);

CREATE VIRTUAL TABLE turns_fts USING fts5(
    text,
    content='turns',
    content_rowid='id',
    tokenize='unicode61 remove_diacritics 2'
);
"""

_SEARCH_SQL = """
SELECT t.session_id, t.ordinal, t.role, t.text, t.session_created_at, t.ingested_at
FROM turns_fts
JOIN turns AS t ON t.id = turns_fts.rowid
WHERE turns_fts MATCH ?
{exclude_clause}
ORDER BY bm25(turns_fts), t.id DESC
LIMIT ?
"""


def _restrict_permissions(path: Path) -> None:
    """Best-effort: restrict the archive file to owner read/write only.

    Same platform caveat as store.py's copy: a real restriction on POSIX,
    only a read-only toggle on Windows. Never allowed to block a write.
    """
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def _render_text(content: Any) -> str:
    """Flatten Anthropic message content into searchable plain text.

    A plain string turn is kept as is. A content-block list is joined line
    by line: text blocks verbatim, tool_use as ``[tool_use <name>] <input>``
    and tool_result as ``[tool_result] <content>`` so past tool activity is
    findable by tool name or by what it returned. This is the *index* view
    only — ``content_json`` keeps the original structure untouched.
    """
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return json.dumps(content, ensure_ascii=False)

    parts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            parts.append(json.dumps(block, ensure_ascii=False))
            continue
        block_type = block.get("type")
        if block_type == "text":
            parts.append(str(block.get("text", "")))
        elif block_type == "tool_use":
            parts.append(
                f"[tool_use {block.get('name')}] "
                f"{json.dumps(block.get('input'), ensure_ascii=False)}"
            )
        elif block_type == "tool_result":
            label = "[tool_result: error]" if block.get("is_error") else "[tool_result]"
            inner = block.get("content")
            inner_text = inner if isinstance(inner, str) else json.dumps(inner, ensure_ascii=False)
            parts.append(f"{label} {inner_text}")
        else:
            parts.append(json.dumps(block, ensure_ascii=False))
    return "\n".join(parts)


def _tokens(query: str) -> list[str]:
    return _TOKEN_PATTERN.findall(query)


def _fts_query(tokens: list[str], operator: str) -> str:
    # Tokens can't contain '"' (see _TOKEN_PATTERN) — doubling is defensive.
    quoted = ['"' + token.replace('"', '""') + '"' for token in tokens]
    return operator.join(quoted)


class ArchiveStore:
    def __init__(self, base_dir: Path | str | None = None) -> None:
        self.base_dir = Path(base_dir) if base_dir is not None else DEFAULT_ARCHIVE_DIR

    @property
    def db_path(self) -> Path:
        return self.base_dir / _ARCHIVE_FILENAME

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self.db_path))
        except (OSError, sqlite3.Error) as exc:
            raise ArchiveLoadError(f"could not open archive at {self.db_path}: {exc}") from exc

        try:
            try:
                self._ensure_schema(conn)
            except ArchiveError:
                raise
            except sqlite3.Error as exc:
                raise ArchiveLoadError(
                    f"archive at {self.db_path} could not be read: {exc}"
                ) from exc
            yield conn
        finally:
            conn.close()

    def _ensure_schema(self, conn: sqlite3.Connection) -> None:
        """Create the schema on a brand-new file; verify it on an existing one.

        Three outcomes, mirroring SessionStore/ProfileStore.load():
        - no tables at all → fresh archive, create everything;
        - tables but no ``meta`` → some other SQLite file, refuse to touch it;
        - ``meta`` with a different schema_version → unsupported, refuse
          (no migration; the file is left exactly as found).
        """
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        if not tables:
            with conn:
                conn.executescript(_SCHEMA_DDL)
                conn.execute(
                    "INSERT INTO meta (key, value) VALUES ('schema_version', ?)",
                    (ARCHIVE_SCHEMA_VERSION,),
                )
            _restrict_permissions(self.db_path)
            return

        if "meta" not in tables:
            raise ArchiveLoadError(
                f"{self.db_path} is a SQLite database but not a F.R.I.D.A.Y archive "
                "(no 'meta' table) — refusing to use it."
            )

        row = conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()
        stored_version = row[0] if row else None
        if stored_version != ARCHIVE_SCHEMA_VERSION:
            raise UnsupportedArchiveSchemaError(
                f"archive has schema_version {stored_version!r}, but this build only "
                f"supports {ARCHIVE_SCHEMA_VERSION!r}. Migration is not implemented — "
                "the file has been left untouched."
            )

    def ingest(self, session: Session) -> int:
        """Archive every turn of ``session`` not yet stored. Returns how many were added.

        Safe to call after every turn: already-archived turns are skipped by
        count, so calling it twice in a row adds nothing, and a session that
        predates M2b is backfilled in full the first time.
        """
        history = session.archived_turns + session.messages
        now = iso_now()

        with self._connect() as conn:
            try:
                with conn:
                    row = conn.execute(
                        "SELECT ingested_count FROM sessions_ingest "
                        "WHERE session_id = ? AND session_created_at = ?",
                        (session.session_id, session.created_at),
                    ).fetchone()
                    already = row[0] if row else 0

                    if len(history) < already:
                        raise ArchiveSaveError(
                            f"session {session.session_id!r} (started {session.created_at}) "
                            f"has {len(history)} turns but the archive already holds "
                            f"{already} for it — history shrank, refusing to renumber "
                            "archived turns."
                        )

                    for ordinal in range(already, len(history)):
                        message = history[ordinal]
                        cursor = conn.execute(
                            "INSERT INTO turns (session_id, session_created_at, ordinal, "
                            "role, text, content_json, ingested_at) "
                            "VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (
                                session.session_id,
                                session.created_at,
                                ordinal,
                                message["role"],
                                _render_text(message["content"]),
                                json.dumps(message["content"], ensure_ascii=False),
                                now,
                            ),
                        )
                        conn.execute(
                            "INSERT INTO turns_fts (rowid, text) VALUES (?, ?)",
                            (cursor.lastrowid, _render_text(message["content"])),
                        )

                    conn.execute(
                        "INSERT OR REPLACE INTO sessions_ingest "
                        "(session_id, session_created_at, ingested_count, last_ingested_at) "
                        "VALUES (?, ?, ?, ?)",
                        (session.session_id, session.created_at, len(history), now),
                    )
            except sqlite3.Error as exc:
                raise ArchiveSaveError(
                    f"could not archive session {session.session_id!r}: {exc}"
                ) from exc

        return len(history) - already

    def search(
        self,
        query: str,
        limit: int = 5,
        exclude: tuple[str, int] | None = None,
    ) -> list[RecallHit]:
        """Keyword search over every archived turn, best match first.

        Tries all terms first (precision), and only if nothing matches falls
        back to any term (recall) — models tend to phrase queries loosely.

        ``exclude=(session_id, cutoff)`` hides turns of that session with
        ``ordinal >= cutoff`` — used to keep a live conversation's own
        in-context window out of its recall results, while its compacted
        (``archived_turns``) part stays searchable.
        """
        tokens = _tokens(query)
        if not tokens:
            return []

        exclude_clause = ""
        exclude_params: tuple[Any, ...] = ()
        if exclude is not None:
            exclude_clause = "AND NOT (t.session_id = ? AND t.ordinal >= ?)"
            exclude_params = (exclude[0], exclude[1])
        sql = _SEARCH_SQL.format(exclude_clause=exclude_clause)

        with self._connect() as conn:
            rows = conn.execute(
                sql, (_fts_query(tokens, " "), *exclude_params, limit)
            ).fetchall()
            if not rows and len(tokens) > 1:
                rows = conn.execute(
                    sql, (_fts_query(tokens, " OR "), *exclude_params, limit)
                ).fetchall()

        return [
            RecallHit(
                session_id=row[0],
                ordinal=row[1],
                role=row[2],
                text=row[3],
                session_started_at=row[4],
                indexed_at=row[5],
            )
            for row in rows
        ]

    def count_turns(self, session_id: str | None = None) -> int:
        """Diagnostic/test helper: archived turns overall, or for one session_id."""
        with self._connect() as conn:
            if session_id is None:
                row = conn.execute("SELECT COUNT(*) FROM turns").fetchone()
            else:
                row = conn.execute(
                    "SELECT COUNT(*) FROM turns WHERE session_id = ?", (session_id,)
                ).fetchone()
        return int(row[0])

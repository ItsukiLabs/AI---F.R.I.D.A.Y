"""The action journal: a durable record of every device command (Sprint 4, stage 4).

Closes gap S5 (M2 v2 A2): the session file used to be the only trace of a
device action, so a failed session save after a lamp had already moved left
no record that it moved. Now ``DeviceService.apply`` writes the command here
**before** touching the device (``prepared``), then the outcome
(``succeeded`` / ``failed`` / ``pending`` / ``unknown``), all under the same
``operation_id`` the device layer uses.

A database transaction cannot roll a lamp back, so this is a journal, not a
transaction (ChatGPT's review, 2026-10-25): it only guarantees that what
happened, or might have happened, is written down.

- Writing ``prepared`` fails -> the command is not sent (fail closed).
- Writing the outcome fails -> the command already happened; the entry
  stays ``prepared`` and is reported as uncertain on the next start.
- On start, ``recover()`` turns entries left ``prepared`` or ``pending`` by an
  earlier run into ``unknown``: their in-memory state is gone, so nobody can
  settle them any more. They are reported to the owner, never retried.

Who/what/how comes from ``ActionContext`` (set by the agent loop for the tool
call being run): the tool name, the session, and how the call was approved
(``auto`` or the confirmer's source, e.g. ``terminal``).

Single-writer, like every other store in the project. The file is
restricted to its owner (best effort, like the archive: real on POSIX, only
a read-only toggle on Windows).
"""

from __future__ import annotations

import json
import os
import sqlite3
import stat
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

JOURNAL_SCHEMA_VERSION = 1

PREPARED = "prepared"
# Statuses an entry can still be in when nobody will settle it any more.
UNRESOLVED = ("prepared", "pending")

_SCHEMA_DDL = """
CREATE TABLE meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE actions (
    operation_id TEXT PRIMARY KEY,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL,
    device_id    TEXT NOT NULL,
    requested    TEXT NOT NULL,
    status       TEXT NOT NULL,
    reported     TEXT,
    message      TEXT,
    tool_name    TEXT,
    session_id   TEXT,
    approval     TEXT,
    reviewed_at  TEXT
);

CREATE INDEX actions_by_time ON actions (created_at);
"""


class JournalError(Exception):
    """The journal could not be opened, read or written."""


@dataclass(frozen=True)
class ActionContext:
    tool_name: str | None = None
    session_id: str | None = None
    approval: str | None = None


# Set by the agent loop around one tool call; read by the device layer.
current_action: ContextVar[ActionContext | None] = ContextVar("current_action", default=None)


@dataclass(frozen=True)
class JournalEntry:
    operation_id: str
    created_at: str
    updated_at: str
    device_id: str
    requested: dict[str, Any]
    status: str
    reported: dict[str, Any] | None
    message: str | None
    tool_name: str | None
    session_id: str | None
    approval: str | None
    reviewed_at: str | None


def _restrict_permissions(path: Path) -> None:
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _dumps(value: Any) -> str | None:
    return None if value is None else json.dumps(value, ensure_ascii=False)


def _entry(row: sqlite3.Row) -> JournalEntry:
    return JournalEntry(
        operation_id=row["operation_id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        device_id=row["device_id"],
        requested=json.loads(row["requested"]),
        status=row["status"],
        reported=json.loads(row["reported"]) if row["reported"] else None,
        message=row["message"],
        tool_name=row["tool_name"],
        session_id=row["session_id"],
        approval=row["approval"],
        reviewed_at=row["reviewed_at"],
    )


class ActionJournal:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._ensure_schema()
        _restrict_permissions(self.path)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        try:
            conn = sqlite3.connect(self.path)
        except sqlite3.Error as exc:
            raise JournalError(f"cannot open action journal {self.path}: {exc}") from exc
        conn.row_factory = sqlite3.Row
        try:
            with conn:  # one transaction: commit on success, roll back on error
                yield conn
        except sqlite3.Error as exc:
            raise JournalError(f"action journal {self.path}: {exc}") from exc
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            tables = {
                row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            if not tables:
                conn.executescript(_SCHEMA_DDL)
                conn.execute(
                    "INSERT INTO meta (key, value) VALUES ('schema_version', ?)",
                    (str(JOURNAL_SCHEMA_VERSION),),
                )
                return
            if "meta" not in tables or "actions" not in tables:
                raise JournalError(f"{self.path} is not an action journal")
            row = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
            if row is None or row[0] != str(JOURNAL_SCHEMA_VERSION):
                raise JournalError(
                    f"{self.path} has unsupported journal schema version "
                    f"{row[0] if row else None!r}"
                )

    # -- writes -----------------------------------------------------------

    def prepare(self, operation_id: str, device_id: str, requested: dict[str, Any]) -> None:
        """Record a command about to be sent. Raises ``JournalError``; then don't send it."""
        context = current_action.get() or ActionContext()
        now = _now()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO actions (operation_id, created_at, updated_at, device_id, requested,"
                " status, tool_name, session_id, approval) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    operation_id,
                    now,
                    now,
                    device_id,
                    _dumps(requested),
                    PREPARED,
                    context.tool_name,
                    context.session_id,
                    context.approval,
                ),
            )

    def finish(
        self,
        operation_id: str,
        status: str,
        reported: dict[str, Any] | None = None,
        message: str | None = None,
    ) -> None:
        """Record a command's outcome (or a pending one settling later)."""
        with self._connect() as conn:
            updated = conn.execute(
                "UPDATE actions SET status = ?, reported = ?, message = ?, updated_at = ?"
                " WHERE operation_id = ?",
                (status, _dumps(reported), message, _now(), operation_id),
            ).rowcount
        if not updated:
            raise JournalError(f"no journal entry for operation {operation_id!r}")

    def recover(self) -> list[JournalEntry]:
        """On start: entries an earlier run left unsettled become ``unknown``.

        Returns every ``unknown`` entry the owner has not reviewed yet (the
        recovered ones and older ones), oldest first. Nothing is retried.
        """
        placeholders = ", ".join("?" for _ in UNRESOLVED)
        with self._connect() as conn:
            conn.execute(
                f"UPDATE actions SET status = 'unknown', updated_at = ?, message ="
                f" COALESCE(message || ' ', '') || '[F.R.I.D.A.Y stopped before the"
                f" outcome was known; check the device.]' WHERE status IN ({placeholders})",
                (_now(), *UNRESOLVED),
            )
        return self.unreviewed()

    def mark_reviewed(self) -> int:
        """The owner has looked at the uncertain entries. Returns how many were marked."""
        with self._connect() as conn:
            return conn.execute(
                "UPDATE actions SET reviewed_at = ? WHERE status = 'unknown' AND reviewed_at IS NULL",
                (_now(),),
            ).rowcount

    # -- reads ------------------------------------------------------------

    def get(self, operation_id: str) -> JournalEntry | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM actions WHERE operation_id = ?", (operation_id,)
            ).fetchone()
        return _entry(row) if row else None

    def recent(self, limit: int = 10) -> list[JournalEntry]:
        """The last ``limit`` entries, newest first."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM actions ORDER BY created_at DESC, rowid DESC LIMIT ?", (limit,)
            ).fetchall()
        return [_entry(row) for row in rows]

    def unreviewed(self) -> list[JournalEntry]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM actions WHERE status = 'unknown' AND reviewed_at IS NULL"
                " ORDER BY created_at, rowid"
            ).fetchall()
        return [_entry(row) for row in rows]

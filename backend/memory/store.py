"""JSON file persistence for M2a sessions.

One file per session at ``<base_dir>/<session_id>.json``. Deliberately
simple (no database) — this is short-term/active-context memory for one
machine, not the long-term retrieval store M2b will add later.
"""

from __future__ import annotations

import re
from pathlib import Path

from backend.memory.session import Session, iso_now
from backend.schemas import SessionRecord

_SESSION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

DEFAULT_SESSIONS_DIR = Path(__file__).parent / "sessions"


class SessionStore:
    def __init__(self, base_dir: Path | str | None = None) -> None:
        self.base_dir = Path(base_dir) if base_dir is not None else DEFAULT_SESSIONS_DIR

    def _path_for(self, session_id: str) -> Path:
        if not _SESSION_ID_PATTERN.match(session_id):
            raise ValueError(
                f"session_id {session_id!r} must match {_SESSION_ID_PATTERN.pattern!r}"
            )
        return self.base_dir / f"{session_id}.json"

    def load(self, session_id: str) -> Session | None:
        path = self._path_for(session_id)
        if not path.exists():
            return None
        record = SessionRecord.model_validate_json(path.read_text(encoding="utf-8"))
        return Session.from_record(record)

    def save(self, session: Session) -> None:
        session.updated_at = iso_now()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        path = self._path_for(session.session_id)
        path.write_text(session.to_record().model_dump_json(indent=2), encoding="utf-8")

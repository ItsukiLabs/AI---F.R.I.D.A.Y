"""JSON file persistence for M2a sessions.

One file per session at ``<base_dir>/<session_id>.json``. Deliberately
simple (no database) — this is short-term/active-context memory for one
machine, not the long-term retrieval store M2b will add later.

Two robustness properties this module guarantees:

1. **Atomic writes.** ``save()`` never writes to the target path directly —
   it writes to a temp file in the same directory, then ``os.replace()``s it
   into place. A crash mid-write leaves the temp file orphaned, never a
   truncated target file, so ``load()`` never sees a half-written session.
2. **Fail loud on untrustworthy data.** If a session file exists but is
   corrupt, unreadable, or from an unsupported schema version, ``load()``
   raises a specific exception rather than silently returning ``None`` (which
   would look identical to "no session yet" and invite callers to silently
   start a fresh one over real, recoverable-looking-but-actually-lost data).
   Only a genuinely *missing* file returns ``None``.

Concurrent writes to the same session_id are explicitly out of scope for
M2a (v1 assumes one writer at a time) — see Memory Think/M2_memory.md.
"""

from __future__ import annotations

import json
import os
import re
import stat
import tempfile
from pathlib import Path

from pydantic import ValidationError

from backend.memory.errors import SessionLoadError, SessionSaveError, UnsupportedSessionSchemaError
from backend.memory.session import Session, iso_now
from backend.schemas import MEMORY_SCHEMA_VERSION, SessionRecord

_SESSION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

DEFAULT_SESSIONS_DIR = Path(__file__).parent / "sessions"


def _restrict_permissions(path: Path) -> None:
    """Best-effort: restrict a session file to owner read/write only.

    On POSIX this is a real access-control restriction (chmod 0600). On
    Windows, ``os.chmod`` only toggles the read-only attribute — it does
    NOT restrict which other accounts can read the file; that would
    require NTFS ACL manipulation (e.g. via pywin32), which is out of
    scope for M2a. Documented platform limitation, not a bug: on Windows,
    session files rely on the OS user-profile directory's own ACLs for
    privacy, same as any other app data under a user's profile.

    Never allowed to block a save — failures here are swallowed.
    """
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


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

        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise SessionLoadError(
                f"could not read session file for {session_id!r}: {exc}"
            ) from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SessionLoadError(
                f"session file for {session_id!r} is not valid JSON: {exc}"
            ) from exc

        stored_version = payload.get("schema_version") if isinstance(payload, dict) else None
        if stored_version != MEMORY_SCHEMA_VERSION:
            raise UnsupportedSessionSchemaError(
                f"session {session_id!r} has schema_version {stored_version!r}, but this "
                f"build only supports {MEMORY_SCHEMA_VERSION!r}. Migration is not "
                "implemented — the file has been left untouched."
            )

        try:
            record = SessionRecord.model_validate(payload)
        except ValidationError as exc:
            raise SessionLoadError(
                f"session file for {session_id!r} does not match the expected schema: {exc}"
            ) from exc

        return Session.from_record(record)

    def save(self, session: Session) -> None:
        session.updated_at = iso_now()
        path = self._path_for(session.session_id)
        payload = session.to_record().model_dump_json(indent=2)

        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(
                dir=self.base_dir, prefix=f".{session.session_id}.tmp-"
            )
            tmp_path = Path(tmp_name)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
                    tmp_file.write(payload)
                _restrict_permissions(tmp_path)
                os.replace(tmp_path, path)  # atomic on both POSIX and Windows
            except BaseException:
                tmp_path.unlink(missing_ok=True)
                raise
        except OSError as exc:
            raise SessionSaveError(
                f"could not save session {session.session_id!r}: {exc}"
            ) from exc

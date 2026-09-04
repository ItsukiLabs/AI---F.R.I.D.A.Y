"""JSON file persistence for the M2c singleton user profile.

One file at ``<base_dir>/profile.json`` — unlike SessionStore (one file per
session_id), the profile is a singleton: F.R.I.D.A.Y has exactly one user
profile shared across every session.

Same two robustness properties as SessionStore (backend/memory/store.py),
duplicated rather than shared: the helper functions are small and stable,
and this deliberately avoids touching the already-reviewed-and-shipped M2a
store module for a purely cosmetic DRY gain.

1. **Atomic writes.** ``save()`` writes to a temp file in the same
   directory, then ``os.replace()``s it into place — a crash mid-write
   never leaves a truncated ``profile.json``.
2. **Fail loud on untrustworthy data.** A profile file that exists but is
   corrupt, unreadable, or from an unsupported schema version raises a
   specific exception rather than silently returning ``None`` — only a
   genuinely *missing* file returns ``None``.
"""

from __future__ import annotations

import json
import os
import stat
import tempfile
from pathlib import Path

from pydantic import ValidationError

from backend.memory.profile import Profile
from backend.memory.profile_errors import (
    ProfileLoadError,
    ProfileSaveError,
    UnsupportedProfileSchemaError,
)
from backend.memory.session import iso_now
from backend.schemas import PROFILE_SCHEMA_VERSION, ProfileRecord

DEFAULT_PROFILE_DIR = Path(__file__).parent / "profile"

_PROFILE_FILENAME = "profile.json"


def _restrict_permissions(path: Path) -> None:
    """Best-effort: restrict the profile file to owner read/write only.

    Same platform caveat as store.py's copy: a real restriction on POSIX,
    only a read-only toggle on Windows. Never allowed to block a save.
    """
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


class ProfileStore:
    def __init__(self, base_dir: Path | str | None = None) -> None:
        self.base_dir = Path(base_dir) if base_dir is not None else DEFAULT_PROFILE_DIR

    def _path(self) -> Path:
        return self.base_dir / _PROFILE_FILENAME

    def load(self) -> Profile | None:
        path = self._path()
        if not path.exists():
            return None

        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ProfileLoadError(f"could not read profile file: {exc}") from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ProfileLoadError(f"profile file is not valid JSON: {exc}") from exc

        stored_version = payload.get("schema_version") if isinstance(payload, dict) else None
        if stored_version != PROFILE_SCHEMA_VERSION:
            raise UnsupportedProfileSchemaError(
                f"profile has schema_version {stored_version!r}, but this build "
                f"only supports {PROFILE_SCHEMA_VERSION!r}. Migration is not "
                "implemented — the file has been left untouched."
            )

        try:
            record = ProfileRecord.model_validate(payload)
        except ValidationError as exc:
            raise ProfileLoadError(f"profile file does not match the expected schema: {exc}") from exc

        return Profile.from_record(record)

    def save(self, profile: Profile) -> None:
        profile.updated_at = iso_now()
        path = self._path()
        payload = profile.to_record().model_dump_json(indent=2)

        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(dir=self.base_dir, prefix=".profile.tmp-")
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
            raise ProfileSaveError(f"could not save profile: {exc}") from exc

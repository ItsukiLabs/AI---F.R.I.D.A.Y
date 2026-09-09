"""Domain-specific exceptions for the M2b long-term archive.

Mirrors backend/memory/errors.py (M2a) and profile_errors.py (M2c) — raised
instead of leaking raw sqlite3.Error / OSError, and ArchiveStore never
silently behaves like an empty archive when a database file actually exists
but can't be trusted (see _ensure_schema() in archive_store.py).
"""

from __future__ import annotations


class ArchiveError(Exception):
    """Base class for all M2b archive errors."""


class ArchiveLoadError(ArchiveError):
    """The archive database exists but could not be opened or read (corrupt,
    not a SQLite file, foreign schema, unreadable)."""


class ArchiveSaveError(ArchiveError):
    """Turns could not be written to the archive.

    Also raised when a session's history is *shorter* than what the archive
    has already recorded for that session generation — that can only happen
    through manual editing of a session file, and silently re-numbering
    turns over existing rows would corrupt provenance.
    """


class UnsupportedArchiveSchemaError(ArchiveLoadError):
    """The archive's stored schema_version doesn't match what this build supports.

    A specific ArchiveLoadError, not a generic one — same split as
    UnsupportedSessionSchemaError / UnsupportedProfileSchemaError.
    """

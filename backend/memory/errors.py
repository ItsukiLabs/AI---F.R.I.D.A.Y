"""Domain-specific exceptions for M2a session persistence.

Raised instead of leaking raw ``json.JSONDecodeError`` / ``OSError`` /
pydantic ``ValidationError`` to callers, so the application layer can catch
one known exception type and decide how to surface it — without needing to
know persistence internals, and without ``SessionStore`` ever silently
falling back to an empty session when a file actually exists but can't be
trusted (see ``load()`` in store.py).
"""

from __future__ import annotations


class SessionError(Exception):
    """Base class for all M2a session persistence errors."""


class SessionLoadError(SessionError):
    """A session file exists but could not be loaded (corrupt/malformed/unreadable)."""


class SessionSaveError(SessionError):
    """A session could not be persisted to disk."""


class UnsupportedSessionSchemaError(SessionLoadError):
    """A session file's schema_version doesn't match what this build supports.

    A specific SessionLoadError, not a generic one — code that only cares
    "did loading fail" can catch SessionLoadError; code that wants to
    distinguish "your data is from an incompatible version" can catch this.
    """

"""Domain-specific exceptions for M2c profile persistence and fact logic.

Mirrors backend/memory/errors.py (M2a session errors) — raised instead of
leaking raw json.JSONDecodeError / OSError / pydantic ValidationError, and
ProfileStore never silently falls back to an empty profile when a file
actually exists but can't be trusted (see load() in profile_store.py).
"""

from __future__ import annotations


class ProfileError(Exception):
    """Base class for all M2c profile errors."""


class ProfileLoadError(ProfileError):
    """A profile file exists but could not be loaded (corrupt/malformed/unreadable)."""


class ProfileSaveError(ProfileError):
    """A profile could not be persisted to disk."""


class UnsupportedProfileSchemaError(ProfileLoadError):
    """A profile file's schema_version doesn't match what this build supports.

    A specific ProfileLoadError, not a generic one — code that only cares
    "did loading fail" can catch ProfileLoadError; code that wants to
    distinguish "your data is from an incompatible version" can catch this.
    """


class ProfileFactNotFoundError(ProfileError):
    """A fact_id referenced by remember_fact(supersedes=...) or forget_fact()
    does not resolve to a fact this profile can act on (missing entirely, or
    — for supersedes specifically — not currently active)."""

"""M2a short-term/active-context memory.

``run_with_memory`` (runner.py) is deliberately NOT re-exported here — it
imports ``backend.agent_core.loop``, which imports ``backend.memory.session``,
so pulling it into this package's own import chain would be circular.
Import it directly: ``from backend.memory.runner import run_with_memory``.
"""

from backend.memory.compaction import compact
from backend.memory.errors import SessionError, SessionLoadError, SessionSaveError, UnsupportedSessionSchemaError
from backend.memory.profile import Profile
from backend.memory.profile_errors import (
    ProfileError,
    ProfileFactNotFoundError,
    ProfileLoadError,
    ProfileSaveError,
    UnsupportedProfileSchemaError,
)
from backend.memory.profile_store import ProfileStore
from backend.memory.session import Session
from backend.memory.store import SessionStore

__all__ = [
    "Session",
    "SessionStore",
    "SessionError",
    "SessionLoadError",
    "SessionSaveError",
    "UnsupportedSessionSchemaError",
    "Profile",
    "ProfileStore",
    "ProfileError",
    "ProfileLoadError",
    "ProfileSaveError",
    "UnsupportedProfileSchemaError",
    "ProfileFactNotFoundError",
    "compact",
]

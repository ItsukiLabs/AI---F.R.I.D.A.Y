"""F.R.I.D.A.Y memory system: M2a sessions, M2b archive, M2c profile.

This package holds only the models and stores. The per-turn entry point that
wires them into the agent loop lives in ``backend.orchestrator.Orchestrator``
(M2 v2 A1, 2026-09-09) — it imports this package and ``backend.agent_core``;
nothing here imports back, which is what keeps the import graph acyclic
(``agent_core.loop`` already imports ``memory.session``).
"""

from backend.memory.archive_errors import (
    ArchiveError,
    ArchiveLoadError,
    ArchiveSaveError,
    UnsupportedArchiveSchemaError,
)
from backend.memory.archive_store import ArchiveStore
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
    "ArchiveStore",
    "ArchiveError",
    "ArchiveLoadError",
    "ArchiveSaveError",
    "UnsupportedArchiveSchemaError",
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

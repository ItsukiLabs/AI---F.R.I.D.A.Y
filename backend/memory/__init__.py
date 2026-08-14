"""M2a short-term/active-context memory.

``run_with_memory`` (runner.py) is deliberately NOT re-exported here — it
imports ``backend.agent_core.loop``, which imports ``backend.memory.session``,
so pulling it into this package's own import chain would be circular.
Import it directly: ``from backend.memory.runner import run_with_memory``.
"""

from backend.memory.compaction import compact
from backend.memory.errors import SessionError, SessionLoadError, SessionSaveError, UnsupportedSessionSchemaError
from backend.memory.session import Session
from backend.memory.store import SessionStore

__all__ = [
    "Session",
    "SessionStore",
    "SessionError",
    "SessionLoadError",
    "SessionSaveError",
    "UnsupportedSessionSchemaError",
    "compact",
]

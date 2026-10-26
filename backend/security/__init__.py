"""M11 Security & Permission (mini, Sprint 4 stage 4).

- ``permissions.py``: the owner's settings file, which tier each tool is;
- ``gate.py``: the gate every tool call passes before it runs, and the
  confirmers that ask the owner (terminal now; voice/camera later).
"""

from backend.security.gate import (
    ConfirmationAnswer,
    ConfirmationRequest,
    Confirmer,
    GateDecision,
    PermissionGate,
    TerminalConfirmer,
    Verdict,
)
from backend.security.permissions import (
    PermissionConfigError,
    PermissionPolicy,
    ToolRule,
    load_permission_policy,
)

__all__ = [
    "ConfirmationAnswer",
    "ConfirmationRequest",
    "Confirmer",
    "GateDecision",
    "PermissionConfigError",
    "PermissionGate",
    "PermissionPolicy",
    "TerminalConfirmer",
    "ToolRule",
    "Verdict",
    "load_permission_policy",
]

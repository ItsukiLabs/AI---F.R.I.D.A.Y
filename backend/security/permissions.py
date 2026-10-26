"""The owner's permission settings: which tier every tool falls under.

Until Sprint 4 a tool's tier came from the tool itself
(``ToolContract.permission_tier``, ``annotations.read_only_hint``). A tool
that misdescribes itself would then grant itself access, so the
classification now comes from a file the owner writes (stage 4, decided
2026-10-25): ``config/permissions.json`` by default, ``FRIDAY_PERMISSIONS_FILE``
to point elsewhere.

A tool missing from the file is **unclassified** and is never run, read-only
or not: a new capability has to be listed by the owner before F.R.I.D.A.Y
may use it.

File format::

    {
      "schema_version": 1,
      "confirmation_ttl_seconds": 180,
      "tools": {
        "home_get_state": {"tier": "read_only"},
        "home_set_power": {"tier": "standard"},
        "home_set_target_temperature": {"tier": "standard", "confirm": true}
      }
    }

``critical`` tools always need the owner's confirmation; ``standard`` ones
only when ``"confirm": true``; ``read_only`` ones never.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from backend.schemas import PermissionTier

PERMISSIONS_SCHEMA_VERSION = 1
DEFAULT_CONFIRMATION_TTL_SECONDS = 180


class PermissionConfigError(ValueError):
    """The permissions file is missing, unreadable, or invalid."""


class ToolRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tier: PermissionTier
    # Ask the owner before every call. Only meaningful for ``standard``:
    # ``critical`` always asks, ``read_only`` never does.
    confirm: bool = False

    @model_validator(mode="after")
    def _confirm_fits_tier(self) -> "ToolRule":
        if self.confirm and self.tier is PermissionTier.READ_ONLY:
            raise ValueError("'confirm' cannot be set on a read_only tool")
        return self

    @property
    def needs_confirmation(self) -> bool:
        return self.tier is PermissionTier.CRITICAL or self.confirm


class PermissionPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = PERMISSIONS_SCHEMA_VERSION
    # How long an owner's "yes" stays valid for the one action it was asked for.
    confirmation_ttl_seconds: int = Field(default=DEFAULT_CONFIRMATION_TTL_SECONDS, ge=1)
    tools: dict[str, ToolRule] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _known_version(self) -> "PermissionPolicy":
        if self.schema_version != PERMISSIONS_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported schema_version {self.schema_version} "
                f"(expected {PERMISSIONS_SCHEMA_VERSION})"
            )
        return self

    def rule(self, tool_name: str) -> ToolRule | None:
        """The owner's rule for ``tool_name``; None means unclassified."""
        return self.tools.get(tool_name)

    def is_read_only(self, tool_name: str) -> bool:
        rule = self.rule(tool_name)
        return rule is not None and rule.tier is PermissionTier.READ_ONLY


def load_permission_policy(path: str | Path) -> PermissionPolicy:
    """Read and validate the owner's permissions file. Raises ``PermissionConfigError``."""
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PermissionConfigError(f"permissions file not found: {path}") from None
    except (OSError, json.JSONDecodeError) as exc:
        raise PermissionConfigError(f"cannot read permissions file {path}: {exc}") from exc
    try:
        return PermissionPolicy.model_validate(raw)
    except ValidationError as exc:
        raise PermissionConfigError(f"invalid permissions file {path}: {exc}") from exc

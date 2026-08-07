"""Tool contract — the manifest format every F.R.I.D.A.Y tool/skill is described by.

Shape follows the Model Context Protocol tool primitive (name, description,
JSON Schema input/output, behavioral annotation hints) plus a
``contract_version``/``version`` split inspired by Agent-OS's versioned
plugin model, so a tool can evolve without breaking callers written
against an older contract shape.

References: Memory Think/PAPER_NOTES.md, category #1 (MCP, Agent-OS).
"""

import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from backend.schemas.versioning import CONTRACT_VERSION

_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
_SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


class PermissionTier(str, Enum):
    """Coarse access tier a tool call falls under.

    Full authorization logic belongs to M11 (Security); this is only the
    label a tool declares about itself so the contract carries enough
    information for that layer to enforce least-privilege later without
    every tool needing to be redefined.
    """

    READ_ONLY = "read_only"
    STANDARD = "standard"
    CRITICAL = "critical"


class ToolAnnotations(BaseModel):
    """Behavioral hints about a tool, mirrored from MCP tool annotations."""

    read_only_hint: bool = Field(
        default=False,
        description="Tool only reads state; never modifies the environment.",
    )
    destructive_hint: bool = Field(
        default=True,
        description=(
            "Tool may perform destructive/irreversible updates. "
            "Meaningless when read_only_hint is True."
        ),
    )
    idempotent_hint: bool = Field(
        default=False,
        description="Calling the tool repeatedly with the same args has no additional effect.",
    )
    open_world_hint: bool = Field(
        default=True,
        description="Tool interacts with an open-world/external system rather than a closed domain.",
    )


class ToolContract(BaseModel):
    """Manifest describing a single callable tool."""

    contract_version: str = Field(default=CONTRACT_VERSION)
    name: str
    version: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None
    annotations: ToolAnnotations = Field(default_factory=ToolAnnotations)
    permission_tier: PermissionTier = PermissionTier.STANDARD

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        if not _NAME_PATTERN.match(value):
            raise ValueError(
                f"tool name {value!r} must be snake_case matching {_NAME_PATTERN.pattern!r}"
            )
        return value

    @field_validator("version", "contract_version")
    @classmethod
    def _validate_semver(cls, value: str) -> str:
        if not _SEMVER_PATTERN.match(value):
            raise ValueError(f"{value!r} must be a semver string like '1.0.0'")
        return value

    @field_validator("description")
    @classmethod
    def _validate_description(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("description must not be empty")
        return value

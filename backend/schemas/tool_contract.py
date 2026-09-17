"""Tool contract — the manifest format every F.R.I.D.A.Y tool/skill is described by.

Shape follows the Model Context Protocol tool primitive (name, description,
JSON Schema input/output, behavioral annotation hints) plus a
``contract_version``/``version`` split inspired by Agent-OS's versioned
plugin model, so a tool can evolve without breaking callers written
against an older contract shape.

Contract 1.1.0 (M4, Sprint 3) adds two fields and one derived value, all
additive — a 1.0.0-style contract without them still validates:

- ``domain`` groups tools the way MCP-Zero groups them under a server
  (``time``, ``memory``, later one domain per M5 device adapter). The tool
  catalog indexes domains alongside tools (Tool-to-Agent Retrieval).
- ``examples`` are concrete scenarios with arguments (EasyTool). They show
  the model how to fill the arguments *and* the catalog indexes their text
  as search material (ScaleMCP's synthetic questions) — one artifact, two
  uses. Every example is validated against ``input_schema`` when the
  contract is built, so a wrong example is rejected here instead of being
  imitated by the model later.
- ``content_hash`` fingerprints everything the tool advertises except its
  version numbers (ScaleMCP's sync hash), so the catalog notices a changed
  tool even when nobody remembered to bump ``version``.

References: Memory Think/PAPER_NOTES.md, category #1 (MCP, Agent-OS) and
category #4 (MCP-Zero, ScaleMCP, Tool-to-Agent Retrieval, EasyTool).
"""

import hashlib
import json
import re
from enum import Enum
from typing import Any

import jsonschema
from pydantic import BaseModel, Field, field_validator, model_validator

from backend.schemas.versioning import CONTRACT_VERSION

IDENTIFIER_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
_SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

DEFAULT_DOMAIN = "general"

# Version numbers say nothing about what a tool *is*: bumping one alone must
# not look like a content change to the catalog, and changing content without
# bumping must still be detected.
_HASH_EXCLUDED_FIELDS = {"contract_version", "version"}


def validate_identifier(value: str, what: str) -> str:
    """Shared snake_case rule for tool names, domains and catalog providers."""
    if not IDENTIFIER_PATTERN.match(value):
        raise ValueError(
            f"{what} {value!r} must be snake_case matching {IDENTIFIER_PATTERN.pattern!r}"
        )
    return value


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


class ToolExample(BaseModel):
    """One concrete use of a tool: the situation, and the arguments to pass."""

    scenario: str = Field(
        description="The situation in plain words, typically what the user said.",
    )
    arguments: dict[str, Any] = Field(default_factory=dict)

    @field_validator("scenario")
    @classmethod
    def _validate_scenario(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("example scenario must not be empty")
        return value


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
    domain: str = DEFAULT_DOMAIN
    examples: list[ToolExample] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return validate_identifier(value, "tool name")

    @field_validator("domain")
    @classmethod
    def _validate_domain(cls, value: str) -> str:
        return validate_identifier(value, "domain")

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

    @model_validator(mode="after")
    def _validate_examples(self) -> "ToolContract":
        for index, example in enumerate(self.examples):
            try:
                jsonschema.validate(example.arguments, self.input_schema)
            except jsonschema.ValidationError as exc:
                raise ValueError(
                    f"example {index} ({example.scenario!r}) does not match "
                    f"input_schema: {exc.message}"
                ) from exc
            except jsonschema.SchemaError as exc:
                raise ValueError(f"input_schema is not a valid JSON Schema: {exc.message}") from exc
        return self

    @property
    def content_hash(self) -> str:
        """SHA-256 over the canonical JSON of every field except version numbers."""
        payload = self.model_dump(mode="json", exclude=_HASH_EXCLUDED_FIELDS)
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

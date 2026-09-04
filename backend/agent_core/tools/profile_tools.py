"""M2c profile tools: remember_user_fact / forget_user_fact.

Unlike backend/agent_core/tools/time_tool.py (stateless, module-level),
these tools need a live ``Profile`` to mutate — so they're built by
``make_profile_tools(profile)`` and bound to that specific object, not
registered in the static ALL_TOOLS list. The closures call straight
through to ``Profile.remember_fact``/``forget_fact`` with no try/except of
their own: backend/agent_core/loop.py's ``_execute_tool_call`` already
catches any exception a tool raises and turns it into a verbal tool_result
observation, so letting ProfileFactNotFoundError propagate here is what
makes that recovery path work.
"""

from __future__ import annotations

from typing import Any, Callable

from backend.memory.profile import Profile
from backend.schemas import PermissionTier, ToolAnnotations, ToolContract

REMEMBER_USER_FACT_CONTRACT = ToolContract(
    name="remember_user_fact",
    version="1.0.0",
    description=(
        "Save a fact about the user that should be remembered across every "
        "future conversation, not just this one. Only call this when the "
        "user has stated something explicitly and durably true about "
        "themselves (name, preference, allergy, constraint, etc) — never "
        "for one-off events or things you inferred. If this fact replaces "
        "an existing known fact (see the list in your system prompt), pass "
        "its id as `supersedes` instead of leaving two conflicting facts."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "fact": {
                "type": "string",
                "minLength": 1,
                "maxLength": 2000,
                "description": (
                    "The fact stated plainly and literally, exactly as the user "
                    "said it — do not infer or generalize."
                ),
            },
            "category": {
                "type": "string",
                "minLength": 1,
                "maxLength": 64,
                "description": (
                    "Short label grouping this fact. Reuse a category already "
                    "shown in the known-facts list when this fact belongs there; "
                    "otherwise pick a new concise one."
                ),
            },
            "supersedes": {
                "type": ["string", "null"],
                "description": (
                    "id (e.g. 'fact_0007') of an existing active fact this one "
                    "replaces, or null if it doesn't conflict with anything known."
                ),
            },
        },
        "required": ["fact", "category"],
        "additionalProperties": False,
    },
    output_schema={
        "type": "object",
        "properties": {"id": {"type": "string"}, "status": {"type": "string"}},
        "required": ["id", "status"],
    },
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=False,
    ),
    permission_tier=PermissionTier.STANDARD,
)

FORGET_USER_FACT_CONTRACT = ToolContract(
    name="forget_user_fact",
    version="1.0.0",
    description=(
        "Delete a previously remembered fact about the user. Only call this "
        "when the user explicitly asks to forget/remove something — never "
        "on your own judgment. Calling this on a fact that's already "
        "forgotten is safe and simply confirms it's gone."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "fact_id": {
                "type": "string",
                "description": "id (e.g. 'fact_0007') of the fact to forget.",
            },
            "reason": {
                "type": ["string", "null"],
                "description": "Optional short note on why this is being forgotten.",
            },
        },
        "required": ["fact_id"],
        "additionalProperties": False,
    },
    output_schema={
        "type": "object",
        "properties": {"id": {"type": "string"}, "status": {"type": "string"}},
        "required": ["id", "status"],
    },
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=True,
        open_world_hint=False,
    ),
    permission_tier=PermissionTier.STANDARD,
)


def make_profile_tools(profile: Profile) -> list[tuple[ToolContract, Callable[..., Any]]]:
    def remember_user_fact(
        fact: str, category: str, supersedes: str | None = None
    ) -> dict[str, str]:
        record = profile.remember_fact(fact, category, supersedes=supersedes)
        return {"id": record.id, "status": record.status}

    def forget_user_fact(fact_id: str, reason: str | None = None) -> dict[str, str]:
        record = profile.forget_fact(fact_id, reason=reason)
        return {"id": record.id, "status": record.status}

    return [
        (REMEMBER_USER_FACT_CONTRACT, remember_user_fact),
        (FORGET_USER_FACT_CONTRACT, forget_user_fact),
    ]

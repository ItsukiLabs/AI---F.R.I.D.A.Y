"""The ReAct agent loop: Thought -> Action -> Observation, repeat.

Built on native Claude tool-calling rather than manual text parsing (the
ReAct paper's original approach predates tool-calling APIs) — model text
before a tool_use block *is* the Thought, the tool_use block *is* the
Action, and the tool_result we send back *is* the Observation. Same
semantics, more robust than regex-parsing a "Thought: ... Action: ..."
transcript.

Reflexion is scoped to a single run: a failed tool call becomes a verbal
observation appended to the conversation, not a silent retry — the model
sees what went wrong and can adjust. Persisting reflections across runs is
M2 (Memory), not M1.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

import jsonschema

from backend.agent_core.config import (
    get_memory_compaction_safety_margin_tokens,
    get_memory_compaction_threshold_tokens,
    get_memory_keep_recent_messages,
    get_tool_result_max_chars,
)
from backend.agent_core.llm_client import LLMClient, LLMResponse, ToolCallRequest
from backend.agent_core.tool_registry import ToolNotLoadedError, ToolRegistry
from backend.memory.compaction import compact
from backend.memory.errors import CompactionError
from backend.memory.profile import Profile
from backend.memory.session import Session

logger = logging.getLogger(__name__)

# Raised from 6 (2026-10-25): find_tools costs one step, and a device task
# such as "find the lamp tool, turn it on, read it back" needs several.
DEFAULT_MAX_ITERATIONS = 10

# Exception text that reaches the model is cut to this length; the full
# traceback goes to the local log. Device errors stay readable (they carry
# the read-back state), while a huge or noisy message can't flood the context.
TOOL_ERROR_MAX_CHARS = 500

DEFAULT_SYSTEM_PROMPT = (
    "You are F.R.I.D.A.Y, a personal AI assistant. Use the available tools "
    "when they would genuinely help answer the request, and give a direct "
    "final answer once you have what you need. If no tool can do what the "
    "user asked, say so plainly: never claim to have done something you "
    "didn't, and never use an unrelated tool as a stand-in. Earlier messages "
    "can be out of date about the physical world: when asked about a "
    "device's current state, read it with a tool instead of answering from "
    "the conversation history. If a request could mean more than one device "
    "and the user did not say which, ask which one instead of guessing."
)


@dataclass
class AgentResult:
    text: str
    exceeded_max_iterations: bool = False
    iterations: int = 0
    # Non-fatal problems the caller should know about (e.g. the archive could
    # not be updated after an otherwise successful turn; M2 v2 A2, S7).
    warnings: list[str] = field(default_factory=list)


def _assistant_message(response: LLMResponse) -> dict[str, Any]:
    """Rebuild an Anthropic-shaped assistant turn from a provider-agnostic LLMResponse."""
    content: list[dict[str, Any]] = []
    if response.text:
        content.append({"type": "text", "text": response.text})
    for call in response.tool_calls:
        content.append(
            {"type": "tool_use", "id": call.id, "name": call.name, "input": call.arguments}
        )
    return {"role": "assistant", "content": content}


def _execute_tool_call(call: ToolCallRequest, registry: ToolRegistry) -> tuple[str, bool]:
    """Run one tool call. Returns (tool_result_content, is_error) — never raises."""
    try:
        registered = registry.resolve(call.name)
    except ToolNotLoadedError as exc:
        return str(exc), True
    except KeyError as exc:
        return f"Tool '{call.name}' is not registered: {exc}", True

    try:
        jsonschema.validate(call.arguments, registered.contract.input_schema)
    except jsonschema.ValidationError as exc:
        return (
            f"Invalid arguments for tool '{call.name}': {exc.message}. "
            "Fix the arguments and try again."
        ), True

    try:
        result = registered.fn(**call.arguments)
    except Exception as exc:  # tool failures become reflections, not crashes
        logger.warning("tool %s failed", call.name, exc_info=True)
        return f"Tool '{call.name}' failed ({type(exc).__name__}): {_clip(str(exc))}", True

    if isinstance(result, str):
        return _limit_size(result), False
    try:
        content = json.dumps(result, ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        logger.warning("tool %s returned a non-JSON result", call.name, exc_info=True)
        return (
            f"Tool '{call.name}' returned a result that could not be serialized "
            f"({type(exc).__name__}). This is a bug in the tool, not in your call."
        ), True
    return _limit_size(content), False


def _clip(text: str) -> str:
    if len(text) <= TOOL_ERROR_MAX_CHARS:
        return text
    return text[:TOOL_ERROR_MAX_CHARS] + " …"


def _limit_size(content: str) -> str:
    """Cap a tool result's size, keeping it valid JSON when it is cut.

    A cut result is wrapped as ``{"truncated": true, "original_chars": N,
    "preview": "..."}`` so the model knows it saw only part of it, instead of
    receiving a JSON document that stops mid-way.
    """
    limit = get_tool_result_max_chars()
    if len(content) <= limit:
        return content
    return json.dumps(
        {
            "truncated": True,
            "original_chars": len(content),
            "preview": content[:limit],
            "note": "The result was too large and was cut. Ask for something narrower if you need the rest.",
        },
        ensure_ascii=False,
    )


def run_agent(
    user_input: str,
    registry: ToolRegistry,
    llm: LLMClient,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    system: str = DEFAULT_SYSTEM_PROMPT,
    session: Session | None = None,
    profile: Profile | None = None,
) -> AgentResult:
    warnings: list[str] = []
    if session is not None:
        if session.needs_compaction(
            get_memory_compaction_threshold_tokens(),
            get_memory_compaction_safety_margin_tokens(),
        ):
            try:
                compact(session, llm, keep_recent_messages=get_memory_keep_recent_messages())
            except CompactionError as exc:
                # The session is untouched, so the turn can go on with the
                # full (just larger) context; the caller still hears about it.
                logger.warning("compaction skipped for session %s: %s", session.session_id, exc)
                warnings.append(f"compaction skipped: {exc} (context kept as is)")
        session.append_user_message(user_input)
        messages = session.messages
    else:
        messages = [{"role": "user", "content": user_input}]

    for iteration in range(1, max_iterations + 1):
        # Re-read every iteration: find_tools (M4) binds catalog tools into
        # this registry mid-turn, and they must be visible on the very next
        # call. A turn's registry only ever grows, so every earlier tool_use
        # block in the history still names an installed tool.
        tools = registry.to_llm_tools()
        llm_input = session.to_llm_messages() if session is not None else messages
        effective_system = system
        if profile is not None:
            block = profile.to_context_block()
            if block:
                effective_system = f"{system}\n\n{block}"
        response = llm.send(messages=llm_input, tools=tools, system=effective_system)
        if session is not None:
            session.record_usage(response)

        messages.append(_assistant_message(response))

        if not response.tool_calls:
            return AgentResult(text=response.text or "", iterations=iteration, warnings=warnings)

        tool_results = []
        for call in response.tool_calls:
            content, is_error = _execute_tool_call(call, registry)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": call.id,
                    "content": content,
                    "is_error": is_error,
                }
            )
        messages.append({"role": "user", "content": tool_results})

    # Record the reply the user is shown, so the stored conversation ends on an
    # assistant turn instead of a tool_result the model never answered
    # (M2 v2 A2, S8).
    text = (
        f"I wasn't able to finish this within {max_iterations} steps. "
        "Try breaking the request into smaller pieces."
    )
    messages.append({"role": "assistant", "content": [{"type": "text", "text": text}]})
    return AgentResult(
        text=text,
        exceeded_max_iterations=True,
        iterations=max_iterations,
        warnings=warnings,
    )

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
from dataclasses import dataclass
from typing import Any

import jsonschema

from backend.agent_core.config import (
    get_memory_compaction_safety_margin_tokens,
    get_memory_compaction_threshold_tokens,
    get_memory_keep_recent_messages,
)
from backend.agent_core.llm_client import LLMClient, LLMResponse, ToolCallRequest
from backend.agent_core.tool_registry import ToolRegistry
from backend.memory.compaction import compact
from backend.memory.profile import Profile
from backend.memory.session import Session

DEFAULT_SYSTEM_PROMPT = (
    "You are F.R.I.D.A.Y, a personal AI assistant. Use the available tools "
    "when they would genuinely help answer the request, and give a direct "
    "final answer once you have what you need. If no tool can do what the "
    "user asked, say so plainly: never claim to have done something you "
    "didn't, and never use an unrelated tool as a stand-in."
)


@dataclass
class AgentResult:
    text: str
    exceeded_max_iterations: bool = False
    iterations: int = 0


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
        registered = registry.get(call.name)
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
        return f"Tool '{call.name}' failed: {exc}", True

    return (result if isinstance(result, str) else json.dumps(result)), False


def run_agent(
    user_input: str,
    registry: ToolRegistry,
    llm: LLMClient,
    max_iterations: int = 6,
    system: str = DEFAULT_SYSTEM_PROMPT,
    session: Session | None = None,
    profile: Profile | None = None,
) -> AgentResult:
    if session is not None:
        if session.needs_compaction(
            get_memory_compaction_threshold_tokens(),
            get_memory_compaction_safety_margin_tokens(),
        ):
            compact(session, llm, keep_recent_messages=get_memory_keep_recent_messages())
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
            return AgentResult(text=response.text or "", iterations=iteration)

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

    return AgentResult(
        text=(
            f"I wasn't able to finish this within {max_iterations} steps. "
            "Try breaking the request into smaller pieces."
        ),
        exceeded_max_iterations=True,
        iterations=max_iterations,
    )

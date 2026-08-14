"""LLM client abstraction for M1's ReAct loop.

Provider-agnostic on purpose: Sprint 1 only wires up Anthropic (project
decision — cloud API first for prototyping speed, local inference lands in
Sprint 8 / M12-M13), but ``loop.py`` talks to the ``LLMClient`` protocol,
not the SDK directly, so swapping providers later doesn't touch the loop.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import anthropic

from backend.agent_core.config import (
    get_anthropic_api_key,
    get_anthropic_model,
    get_llm_provider,
)
from backend.schemas import ToolContract


@dataclass
class ToolCallRequest:
    """A single tool invocation the model asked for."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    """Provider-agnostic view of one LLM turn."""

    text: str | None
    tool_calls: list[ToolCallRequest] = field(default_factory=list)
    stop_reason: str = "end_turn"
    input_tokens: int | None = None
    output_tokens: int | None = None


class LLMClient(Protocol):
    def send(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        system: str,
    ) -> LLMResponse: ...


def tool_contract_to_anthropic_tool(contract: ToolContract) -> dict[str, Any]:
    """Convert a ToolContract (M0) into Anthropic's Messages API tool format.

    1:1 conversion — M0 modeled ``input_schema`` on the MCP tool primitive on
    purpose (see PAPER_NOTES.md category #1), and Anthropic's tool
    ``input_schema`` is the same JSON Schema shape.
    """
    return {
        "name": contract.name,
        "description": contract.description,
        "input_schema": contract.input_schema,
    }


class AnthropicLLMClient:
    """LLMClient implementation backed by the official ``anthropic`` SDK."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        api_key = api_key or get_anthropic_api_key()
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and fill it in."
            )
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model or get_anthropic_model()

    def send(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        system: str,
    ) -> LLMResponse:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=system,
            messages=messages,
            tools=tools,
        )

        text: str | None = None
        tool_calls: list[ToolCallRequest] = []
        for block in response.content:
            if block.type == "text":
                text = (text or "") + block.text
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCallRequest(id=block.id, name=block.name, arguments=block.input)
                )

        return LLMResponse(
            text=text,
            tool_calls=tool_calls,
            stop_reason=response.stop_reason,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )


def get_llm_client(provider: str | None = None) -> LLMClient:
    """Factory. Only "anthropic" is wired up in Sprint 1."""
    provider = provider or get_llm_provider()
    if provider == "anthropic":
        return AnthropicLLMClient()
    if provider == "openai":
        raise NotImplementedError(
            "OpenAI provider is not implemented yet. Sprint 1 only wires up "
            "Anthropic (cloud-first decision, see SPRINT1_LOG.md 2026-08-07); "
            "OpenAI support is a Sprint 8 (M12/M13) concern."
        )
    raise ValueError(f"Unknown LLM provider: {provider!r}")

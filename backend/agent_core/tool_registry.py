"""Registry mapping tool name to its ToolContract (M0) and implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from backend.agent_core.llm_client import tool_contract_to_anthropic_tool
from backend.schemas import ToolContract


@dataclass
class RegisteredTool:
    contract: ToolContract
    fn: Callable[..., Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(self, contract: ToolContract, fn: Callable[..., Any]) -> None:
        if contract.name in self._tools:
            raise ValueError(f"Tool {contract.name!r} is already registered")
        self._tools[contract.name] = RegisteredTool(contract=contract, fn=fn)

    def get(self, name: str) -> RegisteredTool:
        try:
            return self._tools[name]
        except KeyError:
            raise KeyError(f"No tool registered under name {name!r}") from None

    def registered_tools(self) -> list[RegisteredTool]:
        return list(self._tools.values())

    def to_llm_tools(self) -> list[dict[str, Any]]:
        return [
            tool_contract_to_anthropic_tool(registered.contract)
            for registered in self._tools.values()
        ]

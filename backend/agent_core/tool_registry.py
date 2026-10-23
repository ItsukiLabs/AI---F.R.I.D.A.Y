"""Tools installed for one agent run: what the model actually sees and can call.

Since M4 this is deliberately the *small* half of tool registration. Every
tool F.R.I.D.A.Y knows about lives in ``backend/registry/catalog.py``
(``ToolCatalog``); a turn only gets the pinned ones up front, and
``find_tools`` copies matching tools from the catalog into the running
turn's ``ToolRegistry`` with ``bind()``. ``run_agent()`` re-reads
``to_llm_tools()`` on every iteration, so a tool bound in one step is
callable in the next.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from backend.agent_core.llm_client import tool_contract_to_anthropic_tool
from backend.schemas import ToolContract


@dataclass
class RegisteredTool:
    contract: ToolContract
    fn: Callable[..., Any]


class ToolNotLoadedError(KeyError):
    """The tool exists but must be loaded (e.g. with ``find_tools``) before it can be called.

    The message is meant for the model, so ``str()`` returns it unquoted.
    """

    def __str__(self) -> str:
        return str(self.args[0]) if self.args else ""


# Called with a tool name the registry doesn't have. Returns the tool if it
# could be installed on the spot, None if it is unknown, or raises
# ToolNotLoadedError to tell the model how to get it.
MissingToolResolver = Callable[[str], "RegisteredTool | None"]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}
        self._resolver: MissingToolResolver | None = None

    def set_missing_tool_resolver(self, resolver: MissingToolResolver | None) -> None:
        """Consulted by ``resolve()`` for names that are not installed (M4 catalog)."""
        self._resolver = resolver

    def register(self, contract: ToolContract, fn: Callable[..., Any]) -> None:
        if contract.name in self._tools:
            raise ValueError(f"Tool {contract.name!r} is already registered")
        self._tools[contract.name] = RegisteredTool(contract=contract, fn=fn)

    def bind(self, contract: ToolContract, fn: Callable[..., Any]) -> bool:
        """Install a tool unless the same tool is already installed.

        Returns True if the tool was newly installed, False if it was
        already there. Unlike ``register()``, binding the same tool twice is
        normal — the model may search for the same capability again in one
        turn. A *different* tool under an existing name is still an error:
        keeping either one silently would let the model call something other
        than what it was shown.
        """
        existing = self._tools.get(contract.name)
        if existing is None:
            self._tools[contract.name] = RegisteredTool(contract=contract, fn=fn)
            return True
        if existing.contract.content_hash != contract.content_hash:
            raise ValueError(
                f"A different tool is already registered under name {contract.name!r}"
            )
        return False

    def has(self, name: str) -> bool:
        return name in self._tools

    def get(self, name: str) -> RegisteredTool:
        try:
            return self._tools[name]
        except KeyError:
            raise KeyError(f"No tool registered under name {name!r}") from None

    def resolve(self, name: str) -> RegisteredTool:
        """``get()``, falling back to the missing-tool resolver for names not installed.

        Raises ``ToolNotLoadedError`` if the resolver says the tool must be
        loaded first, ``KeyError`` if nobody knows the name.
        """
        if name in self._tools:
            return self._tools[name]
        if self._resolver is not None:
            resolved = self._resolver(name)
            if resolved is not None:
                return resolved
        return self.get(name)

    def registered_tools(self) -> list[RegisteredTool]:
        return list(self._tools.values())

    def to_llm_tools(self) -> list[dict[str, Any]]:
        return [
            tool_contract_to_anthropic_tool(registered.contract)
            for registered in self._tools.values()
        ]

"""M4 meta-tool ``find_tools``: the model asks for a capability it doesn't have yet.

MCP-Zero's active tool discovery as one ordinary tool. Instead of showing
the model every tool F.R.I.D.A.Y has, a turn starts with the pinned tools
plus this one; when a request needs something else, the model searches the
catalog and the matching tools are bound into the running turn's registry,
callable from the model's very next step (``run_agent()`` re-reads the
registry every iteration). Searching again with better words is the
recovery path when the first results don't fit — MCP-Zero's iterative
capability extension.

The contract is built per turn, not at import time: its description lists
the catalog's discoverable domains, so the model knows what kind of thing
is findable without seeing any of those tools' schemas.

"Nothing found" is an answer, not a failure (ToolLLM's *Finish by Giving
Up*, Sasha's clarify-before-acting): the result tells the model to say
plainly that it can't do this rather than improvise with an unrelated tool
— false positives on physical actions are what users judge most harshly.

Binding only makes a tool *callable*; it authorizes nothing.
``permission_tier`` is reported so the model sees what it is about to use;
enforcing it at execution time is M11's job.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable

from backend.agent_core.tool_registry import (
    MissingToolResolver,
    RegisteredTool,
    ToolNotLoadedError,
    ToolRegistry,
)
from backend.registry.catalog import CatalogHit, ToolCatalog
from backend.schemas import PermissionTier, ToolAnnotations, ToolContract, ToolExample

FIND_TOOLS_NAME = "find_tools"
FIND_TOOLS_DEFAULT_LIMIT = 5
FIND_TOOLS_MAX_LIMIT = 10

_DESCRIPTION = (
    "Search F.R.I.D.A.Y's tool catalog for tools that are not loaded yet. Call "
    "this when the request needs a capability none of your current tools "
    "provide, such as controlling a device. Matching tools are loaded "
    "immediately and can be called in your next step of this same turn. "
    "Search for the capability, not the user's whole sentence: an operation "
    "plus its target works best. If the results don't fit, search again with "
    "different words. If nothing relevant exists, tell the user plainly that "
    "you can't do it: never pretend it was done, and never use an unrelated "
    "tool instead."
)

_FOUND_NOTE = (
    "Tools with status 'loaded' can now be called directly in your next step. "
    "Read each description before using one; if none fits the request, search "
    "again with different words."
)

_NOT_FOUND_NOTE = (
    "No tool in the catalog matches. If the query may have been phrased badly, "
    "try once more with different words; otherwise tell the user plainly that "
    "you can't do this. Do not claim it was done and do not use an unrelated tool."
)


def build_find_tools_contract(catalog: ToolCatalog) -> ToolContract:
    domains = catalog.discoverable_domains()
    if domains:
        listing = "\n".join(
            f"- {domain}: {summary}" if summary else f"- {domain}" for domain, summary in domains
        )
    else:
        listing = "- (none)"

    domain_property: dict[str, Any] = {
        "type": "string",
        "description": "Optional: search only this domain.",
    }
    if domains:
        domain_property["enum"] = [domain for domain, _ in domains]

    return ToolContract(
        name=FIND_TOOLS_NAME,
        version="1.0.0",
        domain="registry",
        description=f"{_DESCRIPTION}\n\nDomains you can search:\n{listing}",
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200,
                    "description": (
                        "The capability you need as an operation plus its target, "
                        "in Indonesian or English (e.g. 'turn on light', "
                        "'atur suhu AC')."
                    ),
                },
                "domain": domain_property,
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": FIND_TOOLS_MAX_LIMIT,
                    "description": "Maximum number of tools to load; omit for the default.",
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "count": {"type": "integer"},
                "tools": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "domain": {"type": "string"},
                            "description": {"type": "string"},
                            "permission_tier": {"type": "string"},
                            "status": {"type": "string", "enum": ["loaded", "already_available"]},
                            "example": {"type": "object"},
                        },
                        "required": ["name", "domain", "description", "permission_tier", "status"],
                    },
                },
                "note": {"type": "string"},
            },
            "required": ["query", "count", "tools", "note"],
        },
        annotations=ToolAnnotations(
            # Changes which tools this turn can call, never the environment.
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
        permission_tier=PermissionTier.READ_ONLY,
        examples=[
            ToolExample(
                scenario="User asks to turn on the living room light and no light tool is loaded",
                arguments={"query": "turn on light"},
            ),
            ToolExample(
                scenario="User: 'AC kamar dingin banget, naikin suhunya' with no AC tool loaded",
                arguments={"query": "atur suhu AC", "limit": 3},
            ),
        ],
    )


def _render(hit: CatalogHit, status: str) -> dict[str, Any]:
    contract = hit.contract
    rendered: dict[str, Any] = {
        "name": contract.name,
        "domain": contract.domain,
        "description": contract.description,
        "permission_tier": contract.permission_tier.value,
        "status": status,
    }
    if contract.examples:
        example = contract.examples[0]
        rendered["example"] = {"scenario": example.scenario, "arguments": example.arguments}
    return rendered


def make_discovery_tool(
    catalog: ToolCatalog,
    turn_registry: ToolRegistry,
) -> tuple[ToolContract, Callable[..., Any]]:
    """Build ``find_tools`` bound to ``catalog`` and the turn's ``turn_registry``.

    No try/except of its own: a name collision raised by ``bind()`` becomes
    a verbal tool_result observation through ``loop._execute_tool_call``.
    """

    def find_tools(
        query: str,
        domain: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        effective_limit = min(limit or FIND_TOOLS_DEFAULT_LIMIT, FIND_TOOLS_MAX_LIMIT)
        hits = catalog.search(query, domain=domain, limit=effective_limit)

        tools = []
        for hit in hits:
            newly_bound = turn_registry.bind(hit.contract, hit.fn)
            tools.append(_render(hit, "loaded" if newly_bound else "already_available"))

        return {
            "query": query,
            "count": len(tools),
            "tools": tools,
            "note": _FOUND_NOTE if tools else _NOT_FOUND_NOTE,
        }

    return build_find_tools_contract(catalog), find_tools


class AutoLoadPolicy(str, Enum):
    """What happens when the model calls a catalog tool it never loaded.

    The model may know a tool's name from an earlier turn (loaded tools do
    not carry over) or from an example, and call it directly.
    """

    READ_ONLY = "read_only"  # load read-only tools on the spot; others need find_tools
    ALL = "all"  # load any catalog tool on the spot
    NEVER = "never"  # every catalog tool needs find_tools first


def make_catalog_resolver(
    catalog: ToolCatalog,
    turn_registry: ToolRegistry,
    policy: AutoLoadPolicy | str = AutoLoadPolicy.READ_ONLY,
    is_read_only: Callable[[str], bool] | None = None,
) -> MissingToolResolver:
    """Missing-tool resolver for ``turn_registry``: auto-load or explain, per ``policy``.

    ``is_read_only`` decides what counts as read-only; since Sprint 4 the
    orchestrator passes the owner's permission settings here. Without it,
    the tool's own ``read_only_hint`` is used.

    Default ``READ_ONLY``: reading a device's state skips the extra
    ``find_tools`` step, but a tool that changes the world is only callable
    after the model deliberately searched for it and saw its description and
    permission tier.
    """
    policy = AutoLoadPolicy(policy)

    def resolve(name: str) -> RegisteredTool | None:
        if not catalog.has(name):
            return None
        contract = catalog.get(name).contract
        if is_read_only is not None:
            read_only = is_read_only(name)
        else:
            read_only = contract.annotations.read_only_hint
        if policy is AutoLoadPolicy.ALL or (policy is AutoLoadPolicy.READ_ONLY and read_only):
            entry = catalog.get(name)
            turn_registry.bind(entry.contract, entry.fn)
            return turn_registry.get(name)
        reason = "" if read_only else " It is not read-only, so it is never loaded automatically."
        raise ToolNotLoadedError(
            f"Tool '{name}' exists in the catalog but is not loaded in this turn.{reason} "
            f"Load it first with {FIND_TOOLS_NAME} (e.g. query: '{name.replace('_', ' ')}'), "
            "read its description, then call it."
        )

    return resolve

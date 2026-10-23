"""M4 Tool Registry: the catalog of every known tool, and the ``find_tools`` meta-tool.

The per-turn half (tools installed for one run) stays in
``backend/agent_core/tool_registry.py`` so ``agent_core`` never imports this
package; the dependency points one way, ``registry`` -> ``agent_core``.
"""

from backend.registry.catalog import (
    APP_PROVIDER,
    CatalogEntry,
    CatalogHit,
    SyncReport,
    ToolCatalog,
)
from backend.registry.discovery_tool import (
    FIND_TOOLS_NAME,
    AutoLoadPolicy,
    build_find_tools_contract,
    make_catalog_resolver,
    make_discovery_tool,
)
from backend.registry.retention import DEFAULT_TOOL_RETENTION_TURNS, recently_used_tool_names

__all__ = [
    "APP_PROVIDER",
    "AutoLoadPolicy",
    "CatalogEntry",
    "CatalogHit",
    "DEFAULT_TOOL_RETENTION_TURNS",
    "FIND_TOOLS_NAME",
    "SyncReport",
    "ToolCatalog",
    "build_find_tools_contract",
    "make_catalog_resolver",
    "make_discovery_tool",
    "recently_used_tool_names",
]

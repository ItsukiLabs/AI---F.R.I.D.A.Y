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
    build_find_tools_contract,
    make_discovery_tool,
)

__all__ = [
    "APP_PROVIDER",
    "CatalogEntry",
    "CatalogHit",
    "FIND_TOOLS_NAME",
    "SyncReport",
    "ToolCatalog",
    "build_find_tools_contract",
    "make_discovery_tool",
]

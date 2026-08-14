"""Auto-saving entry point for M2a — the actual reachable "remember across
restarts" feature.

``run_agent()`` itself stays free of I/O side effects (easy to unit test,
no hidden disk writes). ``run_with_memory()`` is the thin, explicit place
where "load session, run one turn, persist it" happens — deliberately not
routed through ``backend/orchestrator/``, which is still an empty
placeholder folder from Sprint 1 with no scheduled sprint of its own (see
Memory Think/SPRINT2_LOG.md).

Kept out of ``backend/memory/__init__.py``'s exports on purpose: this
module imports ``backend.agent_core.loop``, and ``loop.py`` imports
``backend.memory.session`` — re-exporting ``run_with_memory`` from the
package ``__init__`` would make that a circular import.
"""

from __future__ import annotations

from backend.agent_core.llm_client import LLMClient
from backend.agent_core.loop import DEFAULT_SYSTEM_PROMPT, AgentResult, run_agent
from backend.agent_core.tool_registry import ToolRegistry
from backend.memory.session import Session
from backend.memory.store import SessionStore


def run_with_memory(
    user_input: str,
    registry: ToolRegistry,
    llm: LLMClient,
    session_id: str,
    store: SessionStore | None = None,
    max_iterations: int = 6,
    system: str = DEFAULT_SYSTEM_PROMPT,
) -> AgentResult:
    store = store or SessionStore()
    session = store.load(session_id) or Session.new(session_id)
    result = run_agent(
        user_input,
        registry,
        llm,
        max_iterations=max_iterations,
        system=system,
        session=session,
    )
    store.save(session)
    return result

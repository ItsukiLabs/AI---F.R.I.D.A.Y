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
from backend.agent_core.tools.profile_tools import make_profile_tools
from backend.memory.profile import Profile
from backend.memory.profile_store import ProfileStore
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


def run_with_profile_memory(
    user_input: str,
    registry: ToolRegistry,
    llm: LLMClient,
    session_id: str,
    session_store: SessionStore | None = None,
    profile_store: ProfileStore | None = None,
    max_iterations: int = 6,
    system: str = DEFAULT_SYSTEM_PROMPT,
) -> AgentResult:
    """Like ``run_with_memory``, plus a cross-session user profile (M2c).

    Unlike ``session`` (scoped to ``session_id``), ``profile`` is a
    singleton shared across every session_id — this is what lets a brand
    new session recall facts remembered in a completely different one.

    The caller's ``registry`` is copied into a fresh ``ToolRegistry`` each
    call rather than mutated in place: ``ToolRegistry.register()`` raises
    if a name is already registered, so registering the profile tools
    directly onto a ``registry`` reused across repeated calls (a real chat
    loop calls this once per turn) would fail on the second call.
    """
    session_store = session_store or SessionStore()
    profile_store = profile_store or ProfileStore()
    session = session_store.load(session_id) or Session.new(session_id)
    profile = profile_store.load() or Profile.new()

    turn_registry = ToolRegistry()
    for registered in registry.registered_tools():
        turn_registry.register(registered.contract, registered.fn)
    for contract, fn in make_profile_tools(profile):
        turn_registry.register(contract, fn)

    result = run_agent(
        user_input,
        turn_registry,
        llm,
        max_iterations=max_iterations,
        system=system,
        session=session,
        profile=profile,
    )

    session_store.save(session)
    if profile.dirty:
        profile_store.save(profile)
    return result

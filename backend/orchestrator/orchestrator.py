"""The single entry point for one F.R.I.D.A.Y turn: agent loop + all memory layers + tools.

``run_agent()`` (agent_core/loop.py) stays free of I/O side effects — easy to
unit test, no hidden disk writes. ``Orchestrator.run_turn()`` is the one
explicit place where "load session + profile, compose the per-turn tool
registry, run one turn, persist everything" happens. It replaces the three
``run_with_*`` runners that used to live in ``backend/memory/runner.py``
(M2a/M2c/M2b each shipped its own, 80% identical); the product always runs
with all three memory layers, so a single wiring is the only one that makes
sense — and Sprint 3 (M4/M5 device) needs exactly one turn function to call.

Tools come from two places (M4, Sprint 3):

- ``registry`` — the pre-M4 way: every tool in it is installed on every turn.
  Kept so existing callers and tests work unchanged.
- ``catalog`` (``backend/registry``) — the M4 way: *pinned* catalog tools are
  installed on every turn, *discoverable* ones only through ``find_tools``,
  which is installed whenever the catalog has anything to discover. M5
  device adapters ``sync()`` their tools into the catalog.

Both may be given at once; a tool name present in both raises when the turn
registry is composed (fail loud rather than silently pick one).

This is the generic agent+memory+tools glue the README describes for
``backend/orchestrator/``. It is *not* M14 Multi-Agent Orchestration
(Sprint 9), whose scope is coordinating several agents.

Import direction is one-way: this package imports ``agent_core``,
``memory`` and ``registry``; nothing imports back into ``orchestrator``, so
the circular import that kept the runners out of
``backend/memory/__init__.py`` cannot occur here.
"""

from __future__ import annotations

import logging

from backend.agent_core.llm_client import LLMClient
from backend.agent_core.loop import DEFAULT_SYSTEM_PROMPT, AgentResult, run_agent
from backend.agent_core.tool_registry import ToolRegistry
from backend.agent_core.tools.profile_tools import make_profile_tools
from backend.agent_core.tools.recall_tools import make_recall_tools
from backend.memory.archive_store import ArchiveStore
from backend.memory.profile import Profile
from backend.memory.profile_store import ProfileStore
from backend.memory.session import Session
from backend.memory.store import SessionStore
from backend.registry import ToolCatalog, make_discovery_tool

logger = logging.getLogger(__name__)


def _append_assistant_note(session: Session, text: str) -> None:
    """Add ``text`` to the stored conversation as assistant content.

    Extends the last message if it is already an assistant turn, so roles
    keep alternating; otherwise starts a new assistant message.
    """
    block = {"type": "text", "text": text}
    last = session.messages[-1] if session.messages else None
    if last is not None and last["role"] == "assistant":
        if isinstance(last["content"], str):
            last["content"] = [{"type": "text", "text": last["content"]}]
        last["content"].append(block)
    else:
        session.messages.append({"role": "assistant", "content": [block]})


def _interrupted_note(exc: BaseException) -> str:
    """Stored in place of the reply a failed turn never produced."""
    return (
        f"[Turn interrupted before a reply could be given ({type(exc).__name__}). "
        "Actions above may already have taken effect; check device state "
        "instead of assuming either way.]"
    )


def _profile_not_saved_note(exc: BaseException) -> str:
    """Stored after a turn whose profile changes could not be written."""
    return (
        f"[Saving the user profile failed ({type(exc).__name__}): facts remembered or "
        "forgotten in this turn were NOT saved, whatever was said above. Say so if "
        "the user relies on them.]"
    )


class Orchestrator:
    """Built once, then ``run_turn()`` per user turn.

    ``registry`` holds the caller's always-installed application tools (e.g.
    ``get_current_time``); ``catalog`` holds the M4 tool catalog. Memory tools
    (``remember_user_fact``, ``forget_user_fact``, ``recall_memory``) are bound
    per turn to the freshly loaded profile/session, and ``find_tools`` per turn
    to that turn's registry — all added to a *fresh* per-turn registry, so
    neither the caller's registry nor the catalog is ever mutated by a turn
    (``ToolRegistry.register()`` raises on a duplicate name, so registering
    onto a reused registry would blow up on the second turn), and a tool that
    ``find_tools`` loaded in one turn is gone at the start of the next.

    Stores default to the real on-disk locations under ``backend/memory/``;
    inject ``tmp_path``-based ones in tests.
    """

    def __init__(
        self,
        llm: LLMClient,
        registry: ToolRegistry | None = None,
        session_store: SessionStore | None = None,
        profile_store: ProfileStore | None = None,
        archive_store: ArchiveStore | None = None,
        max_iterations: int = 6,
        system: str = DEFAULT_SYSTEM_PROMPT,
        catalog: ToolCatalog | None = None,
    ) -> None:
        self.llm = llm
        self.registry = registry if registry is not None else ToolRegistry()
        self.catalog = catalog
        self.session_store = session_store or SessionStore()
        self.profile_store = profile_store or ProfileStore()
        self.archive_store = archive_store or ArchiveStore()
        self.max_iterations = max_iterations
        self.system = system

    def _turn_registry(self, profile: Profile, session: Session) -> ToolRegistry:
        turn_registry = ToolRegistry()
        for registered in self.registry.registered_tools():
            turn_registry.register(registered.contract, registered.fn)
        if self.catalog is not None:
            for entry in self.catalog.pinned_tools():
                turn_registry.register(entry.contract, entry.fn)
        for contract, fn in make_profile_tools(profile):
            turn_registry.register(contract, fn)
        for contract, fn in make_recall_tools(self.archive_store, current_session=session):
            turn_registry.register(contract, fn)
        if self.catalog is not None and self.catalog.has_discoverable_tools():
            contract, fn = make_discovery_tool(self.catalog, turn_registry)
            turn_registry.register(contract, fn)
        return turn_registry

    def run_turn(self, user_input: str, session_id: str) -> AgentResult:
        """Run one turn of ``session_id`` and persist it.

        Three memory layers: ``session`` is this conversation (scoped to
        ``session_id``), ``profile`` is the singleton of durable user facts
        shared by every session, ``archive`` is every turn of every session
        verbatim, searchable via ``recall_memory``. Both session and profile
        are re-read from their stores on every turn — the stores are the
        source of truth; nothing is cached on this object.

        Write order (M2 v2 A2, decided 2026-10-23): profile first (only if
        dirty), session second, archive **last**. Profile goes first so a
        failed profile save cannot leave a session that says "I'll remember
        that" while the profile is empty (S6): the session is still written,
        with a note that the profile changes were not saved (so device actions
        in the same turn are not lost), and the exception propagates. The archive is derived data and
        self-healing (``ingest()`` is idempotent by count), so an archive
        failure is logged and reported in ``AgentResult.warnings`` instead of
        raised: raising would throw away the reply of a turn that already
        happened and invite the user to repeat a device command (S7).

        If ``run_agent`` raises after the turn started (e.g. the LLM API fails
        after a device already acted, S4), the partial turn is kept: an
        "interrupted" marker is appended as the assistant reply, everything is
        persisted, and the original exception is re-raised. A failure while
        persisting that partial turn is attached to the original exception as
        a note rather than replacing it.
        """
        session = self.session_store.load(session_id) or Session.new(session_id)
        profile = self.profile_store.load() or Profile.new()

        try:
            result = run_agent(
                user_input,
                self._turn_registry(profile, session),
                self.llm,
                max_iterations=self.max_iterations,
                system=self.system,
                session=session,
                profile=profile,
            )
        except Exception as exc:
            # A stored turn always ends on an assistant message, so a trailing
            # user message (the input or tool results) means this turn was cut
            # off mid-way. If compaction failed before the input was appended,
            # nothing changed and persisting just rewrites the same session.
            if session.messages:
                if session.messages[-1]["role"] == "user":
                    _append_assistant_note(session, _interrupted_note(exc))
                try:
                    self._persist(session, profile)
                except Exception as save_exc:
                    exc.add_note(f"Saving the interrupted turn also failed: {save_exc!r}")
            raise

        result.warnings.extend(self._persist(session, profile))
        return result

    def _persist(self, session: Session, profile: Profile) -> list[str]:
        """Write profile, session, archive in that order; returns non-fatal warnings."""
        if profile.dirty:
            try:
                self.profile_store.save(profile)
            except Exception as exc:
                # Keep the turn (it may hold device actions) but correct any
                # "I'll remember that" in it, then still fail loud. The archive
                # is skipped; it catches up on the next successful turn.
                _append_assistant_note(session, _profile_not_saved_note(exc))
                try:
                    self.session_store.save(session)
                except Exception as save_exc:
                    exc.add_note(f"Saving the session afterwards also failed: {save_exc!r}")
                raise
        self.session_store.save(session)
        try:
            self.archive_store.ingest(session)
        except Exception as exc:
            logger.warning("archive ingest failed for session %s: %r", session.session_id, exc)
            return [f"archive not updated: {exc!r} (will retry on the next turn)"]
        return []

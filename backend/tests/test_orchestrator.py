"""Tests for the single per-turn entry point.

Ported from the three ``test_memory_runner*.py`` files that covered the
M2a/M2c/M2b runners (deleted with ``backend/memory/runner.py``), plus two
cases for what is now a contract of the class itself: the caller's registry
is never mutated, and injected stores are used as-is across turns.
"""

import json

import pytest

from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.agent_core.tool_registry import ToolRegistry
from backend.memory.archive_errors import ArchiveSaveError
from backend.memory.archive_store import ArchiveStore
from backend.memory.profile_store import ProfileStore
from backend.memory.store import SessionStore
from backend.orchestrator import Orchestrator
from backend.schemas import ToolContract


class FakeLLMClient:
    def __init__(self, responses: list[LLMResponse]):
        self._responses = list(responses)
        self.calls: list[dict] = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": list(messages), "tools": tools, "system": system})
        return self._responses.pop(0)


def _text(text: str) -> LLMResponse:
    return LLMResponse(text=text, tool_calls=[])


def _remember_call(fact: str, category: str, call_id: str = "call_1", **extra) -> LLMResponse:
    return LLMResponse(
        text=None,
        tool_calls=[
            ToolCallRequest(
                id=call_id,
                name="remember_user_fact",
                arguments={"fact": fact, "category": category, **extra},
            )
        ],
        stop_reason="tool_use",
    )


def _recall_call(query: str, call_id: str = "call_1") -> LLMResponse:
    return LLMResponse(
        text=None,
        tool_calls=[ToolCallRequest(id=call_id, name="recall_memory", arguments={"query": query})],
        stop_reason="tool_use",
    )


def _stores(tmp_path) -> dict:
    return {
        "session_store": SessionStore(base_dir=tmp_path / "sessions"),
        "profile_store": ProfileStore(base_dir=tmp_path / "profile"),
        "archive_store": ArchiveStore(base_dir=tmp_path / "archive"),
    }


def _orchestrator(tmp_path, llm, registry: ToolRegistry | None = None) -> Orchestrator:
    return Orchestrator(llm, registry or ToolRegistry(), **_stores(tmp_path))


def _tool_result_payload(call: dict) -> dict:
    """The tool_result block of the last message the LLM was sent, decoded."""
    last = call["messages"][-1]
    assert last["role"] == "user"
    block = last["content"][0]
    assert block["type"] == "tool_result"
    assert block["is_error"] is False
    return json.loads(block["content"])


# --- session layer (M2a) ---------------------------------------------------


def test_run_turn_creates_and_persists_a_new_session(tmp_path):
    orch = _orchestrator(tmp_path, FakeLLMClient([_text("Hi!")]))

    result = orch.run_turn("hello", session_id="s1")

    assert result.text == "Hi!"
    loaded = orch.session_store.load("s1")
    assert loaded is not None
    assert loaded.messages[0] == {"role": "user", "content": "hello"}
    assert loaded.messages[1] == {
        "role": "assistant",
        "content": [{"type": "text", "text": "Hi!"}],
    }


def test_same_orchestrator_continues_an_existing_session_across_turns(tmp_path):
    """One Orchestrator object, two turns — proves the per-turn registry is
    rebuilt (registering memory tools twice onto one registry would raise)."""
    llm = FakeLLMClient([_text("My name is F.R.I.D.A.Y."), _text("You just asked my name.")])
    orch = _orchestrator(tmp_path, llm)

    orch.run_turn("what is your name?", session_id="s1")
    orch.run_turn("what did I just ask?", session_id="s1")

    loaded = orch.session_store.load("s1")
    assert loaded is not None
    assert len(loaded.messages) == 4
    assert loaded.messages[2] == {"role": "user", "content": "what did I just ask?"}
    assert llm.calls[1]["messages"][0]["content"] == "what is your name?"


# --- profile layer (M2c) ---------------------------------------------------


def test_turn_that_remembers_a_fact_persists_profile_json(tmp_path):
    llm = FakeLLMClient([_remember_call("Allergic to peanuts.", "health"), _text("Got it.")])
    orch = _orchestrator(tmp_path, llm)

    orch.run_turn("remember I am allergic to peanuts", session_id="s1")

    assert (tmp_path / "profile" / "profile.json").exists()
    assert orch.profile_store.load().active_facts()[0].text == "Allergic to peanuts."


def test_turn_without_fact_tool_call_does_not_write_profile_json(tmp_path):
    orch = _orchestrator(tmp_path, FakeLLMClient([_text("Sure, no facts here.")]))

    orch.run_turn("what is the weather like", session_id="s1")

    assert not (tmp_path / "profile" / "profile.json").exists()


def test_profile_is_visible_across_different_session_ids(tmp_path):
    """Unlike Session (scoped to one session_id), a fact remembered in one
    session is recalled from a completely different session_id."""
    stores = _stores(tmp_path)

    llm1 = FakeLLMClient([_remember_call("Name is Ernold.", "identity"), _text("Got it.")])
    Orchestrator(llm1, ToolRegistry(), **stores).run_turn(
        "remember my name is Ernold", session_id="session-A"
    )

    llm2 = FakeLLMClient([_text("Your name is Ernold.")])
    Orchestrator(llm2, ToolRegistry(), **stores).run_turn("what is my name?", session_id="session-B")

    assert "Name is Ernold." in llm2.calls[0]["system"]
    # session-B's own history never saw session-A's turns
    assert llm2.calls[0]["messages"] == [{"role": "user", "content": "what is my name?"}]


def test_supersede_flow_across_two_separate_turns(tmp_path):
    llm1 = FakeLLMClient([_remember_call("Lives in Bandung.", "location"), _text("Got it.")])
    orch = _orchestrator(tmp_path, llm1)
    orch.run_turn("remember I live in Bandung", session_id="s1")

    old_id = orch.profile_store.load().active_facts()[0].id

    llm2 = FakeLLMClient(
        [
            _remember_call("Lives in Jakarta.", "location", call_id="call_2", supersedes=old_id),
            _text("Updated."),
        ]
    )
    orch.llm = llm2
    orch.run_turn("actually I moved to Jakarta", session_id="s2")  # a different session again

    final = orch.profile_store.load()
    statuses = {f.id: f.status for f in final.facts}
    assert statuses[old_id] == "superseded"
    assert final.active_facts()[0].text == "Lives in Jakarta."


# --- archive layer (M2b) ---------------------------------------------------


def test_turn_is_ingested_after_session_save(tmp_path):
    orch = _orchestrator(tmp_path, FakeLLMClient([_text("Halo!")]))

    orch.run_turn("halo", session_id="s1")

    assert (tmp_path / "sessions" / "s1.json").exists()
    assert orch.archive_store.db_path.exists()
    assert orch.archive_store.count_turns("s1") == 2


def test_caller_tools_plus_all_memory_tools_are_offered_to_llm(tmp_path):
    registry = ToolRegistry()
    registry.register(
        ToolContract(
            name="ping",
            version="1.0.0",
            description="Ping.",
            input_schema={"type": "object", "properties": {}},
        ),
        lambda: "pong",
    )
    llm = FakeLLMClient([_text("ok")])

    _orchestrator(tmp_path, llm, registry).run_turn("hi", session_id="s1")

    offered = {tool["name"] for tool in llm.calls[0]["tools"]}
    assert {"ping", "recall_memory", "remember_user_fact", "forget_user_fact"} <= offered


def test_recall_across_different_session_ids_proves_the_point(tmp_path):
    """Something said in session-A is quotable from a brand new session-B —
    via an explicit recall_memory call, as a verbatim quote with provenance,
    without ever touching the profile (recall reads; it never turns chat
    into facts)."""
    stores = _stores(tmp_path)

    llm_a = FakeLLMClient([_text("Oke, aku catat di obrolan ini.")])
    Orchestrator(llm_a, ToolRegistry(), **stores).run_turn(
        "aku alergi kacang tanah, tolong catat", session_id="session-A"
    )

    llm_b = FakeLLMClient(
        [_recall_call("alergi kacang"), _text("Di obrolan sebelumnya kamu bilang alergi kacang tanah.")]
    )
    result = Orchestrator(llm_b, ToolRegistry(), **stores).run_turn(
        "aku pernah bilang alergi apa ya?", session_id="session-B"
    )

    assert result.text.startswith("Di obrolan sebelumnya")
    assert llm_b.calls[0]["messages"] == [
        {"role": "user", "content": "aku pernah bilang alergi apa ya?"}
    ]
    payload = _tool_result_payload(llm_b.calls[1])
    assert payload["count"] == 1
    hit = payload["hits"][0]
    assert hit["session_id"] == "session-A"
    assert hit["role"] == "user"
    assert "alergi kacang tanah" in hit["text"]
    assert not (tmp_path / "profile" / "profile.json").exists()


def test_recall_does_not_return_current_sessions_live_turns(tmp_path):
    orch = _orchestrator(tmp_path, FakeLLMClient([_text("Oke.")]))
    orch.run_turn("kode rahasianya mangga", session_id="s1")

    llm2 = FakeLLMClient([_recall_call("mangga"), _text("...")])
    orch.llm = llm2
    orch.run_turn("cari mangga", session_id="s1")

    payload = _tool_result_payload(llm2.calls[1])
    assert payload["count"] == 0  # turn 1 is still in s1's live window


def test_ingest_failure_raises_after_session_is_durable_and_next_turn_catches_up(tmp_path):
    stores = _stores(tmp_path)

    class BrokenArchive:
        db_path = stores["archive_store"].db_path

        def search(self, *args, **kwargs):
            return []

        def ingest(self, session):
            raise ArchiveSaveError("disk on fire")

    broken = Orchestrator(
        FakeLLMClient([_text("Oke.")]),
        ToolRegistry(),
        session_store=stores["session_store"],
        profile_store=stores["profile_store"],
        archive_store=BrokenArchive(),
    )
    with pytest.raises(ArchiveSaveError):
        broken.run_turn("satu", session_id="s1")
    # fail loud, but the session itself is already durable
    assert len(stores["session_store"].load("s1").messages) == 2

    Orchestrator(FakeLLMClient([_text("Dua.")]), ToolRegistry(), **stores).run_turn(
        "dua", session_id="s1"
    )

    assert stores["archive_store"].count_turns("s1") == 4  # turn 1 backfilled + turn 2


# --- contract of the class itself -----------------------------------------


def test_callers_registry_is_never_mutated(tmp_path):
    registry = ToolRegistry()
    orch = _orchestrator(tmp_path, FakeLLMClient([_text("ok"), _text("ok")]), registry)

    orch.run_turn("hi", session_id="s1")
    orch.run_turn("hi again", session_id="s1")

    assert registry.registered_tools() == []
    assert orch.registry is registry


def test_injected_stores_are_used_as_is_across_turns(tmp_path):
    stores = _stores(tmp_path)
    orch = Orchestrator(FakeLLMClient([_text("ok"), _text("ok")]), ToolRegistry(), **stores)

    orch.run_turn("hi", session_id="s1")
    orch.run_turn("hi", session_id="s2")

    assert orch.session_store is stores["session_store"]
    assert orch.profile_store is stores["profile_store"]
    assert orch.archive_store is stores["archive_store"]
    assert stores["session_store"].load("s1") is not None
    assert stores["session_store"].load("s2") is not None
    assert stores["archive_store"].count_turns("s1") == 2
    assert stores["archive_store"].count_turns("s2") == 2

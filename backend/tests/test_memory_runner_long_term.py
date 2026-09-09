import json

import pytest

from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.agent_core.tool_registry import ToolRegistry
from backend.memory.archive_errors import ArchiveSaveError
from backend.memory.archive_store import ArchiveStore
from backend.memory.profile_store import ProfileStore
from backend.memory.runner import (
    run_with_long_term_memory,
    run_with_memory,
    run_with_profile_memory,
)
from backend.memory.store import SessionStore
from backend.schemas import ToolContract


class FakeLLMClient:
    def __init__(self, responses: list[LLMResponse]):
        self._responses = list(responses)
        self.calls: list[dict] = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": list(messages), "tools": tools, "system": system})
        return self._responses.pop(0)


def _recall_call(query: str, call_id: str = "call_1") -> LLMResponse:
    return LLMResponse(
        text=None,
        tool_calls=[ToolCallRequest(id=call_id, name="recall_memory", arguments={"query": query})],
        stop_reason="tool_use",
    )


def _stores(tmp_path):
    return {
        "session_store": SessionStore(base_dir=tmp_path / "sessions"),
        "profile_store": ProfileStore(base_dir=tmp_path / "profile"),
        "archive_store": ArchiveStore(base_dir=tmp_path / "archive"),
    }


def _tool_result_payload(call: dict) -> dict:
    """The tool_result block of the last message the LLM was sent, decoded."""
    last = call["messages"][-1]
    assert last["role"] == "user"
    block = last["content"][0]
    assert block["type"] == "tool_result"
    assert block["is_error"] is False
    return json.loads(block["content"])


def test_turn_is_ingested_after_session_save(tmp_path):
    stores = _stores(tmp_path)
    llm = FakeLLMClient([LLMResponse(text="Halo!", tool_calls=[])])

    run_with_long_term_memory("halo", ToolRegistry(), llm, session_id="s1", **stores)

    assert (tmp_path / "sessions" / "s1.json").exists()
    assert stores["archive_store"].db_path.exists()
    assert stores["archive_store"].count_turns("s1") == 2


def test_recall_memory_and_profile_tools_are_offered_to_llm(tmp_path):
    stores = _stores(tmp_path)
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
    llm = FakeLLMClient([LLMResponse(text="ok", tool_calls=[])])

    run_with_long_term_memory("hi", registry, llm, session_id="s1", **stores)

    offered = {tool["name"] for tool in llm.calls[0]["tools"]}
    assert {"ping", "recall_memory", "remember_user_fact", "forget_user_fact"} <= offered


def test_recall_across_different_session_ids_proves_the_point(tmp_path):
    """The test that proves the point of M2b: something said in session-A is
    quotable from a brand new session-B — via an explicit recall_memory
    call, as a verbatim quote with provenance, without ever touching the
    profile (recall reads; it never turns chat into facts)."""
    stores = _stores(tmp_path)

    llm_a = FakeLLMClient([LLMResponse(text="Oke, aku catat di obrolan ini.", tool_calls=[])])
    run_with_long_term_memory(
        "aku alergi kacang tanah, tolong catat",
        ToolRegistry(),
        llm_a,
        session_id="session-A",
        **stores,
    )

    llm_b = FakeLLMClient(
        [
            _recall_call("alergi kacang"),
            LLMResponse(text="Di obrolan sebelumnya kamu bilang alergi kacang tanah.", tool_calls=[]),
        ]
    )
    result = run_with_long_term_memory(
        "aku pernah bilang alergi apa ya?",
        ToolRegistry(),
        llm_b,
        session_id="session-B",  # deliberately a different session_id
        **stores,
    )

    assert result.text.startswith("Di obrolan sebelumnya")
    # session-B's own history never contained session-A's turns
    assert llm_b.calls[0]["messages"] == [
        {"role": "user", "content": "aku pernah bilang alergi apa ya?"}
    ]
    payload = _tool_result_payload(llm_b.calls[1])
    assert payload["count"] == 1
    hit = payload["hits"][0]
    assert hit["session_id"] == "session-A"
    assert hit["role"] == "user"
    assert "alergi kacang tanah" in hit["text"]
    # recall never writes facts
    assert not (tmp_path / "profile" / "profile.json").exists()


def test_recall_does_not_return_current_sessions_live_turns(tmp_path):
    stores = _stores(tmp_path)

    llm1 = FakeLLMClient([LLMResponse(text="Oke.", tool_calls=[])])
    run_with_long_term_memory(
        "kode rahasianya mangga", ToolRegistry(), llm1, session_id="s1", **stores
    )

    llm2 = FakeLLMClient([_recall_call("mangga"), LLMResponse(text="…", tool_calls=[])])
    run_with_long_term_memory("cari mangga", ToolRegistry(), llm2, session_id="s1", **stores)

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

    llm1 = FakeLLMClient([LLMResponse(text="Oke.", tool_calls=[])])
    with pytest.raises(ArchiveSaveError):
        run_with_long_term_memory(
            "satu",
            ToolRegistry(),
            llm1,
            session_id="s1",
            session_store=stores["session_store"],
            profile_store=stores["profile_store"],
            archive_store=BrokenArchive(),
        )
    # fail loud, but the session itself is already durable
    assert len(stores["session_store"].load("s1").messages) == 2

    llm2 = FakeLLMClient([LLMResponse(text="Dua.", tool_calls=[])])
    run_with_long_term_memory("dua", ToolRegistry(), llm2, session_id="s1", **stores)

    assert stores["archive_store"].count_turns("s1") == 4  # turn 1 backfilled + turn 2


def test_existing_runners_do_not_offer_recall_memory(tmp_path):
    """Guard against accidental wiring: the two pre-M2b entry points must
    keep exactly the tool surface they shipped with."""
    session_store = SessionStore(base_dir=tmp_path / "sessions")
    profile_store = ProfileStore(base_dir=tmp_path / "profile")

    llm1 = FakeLLMClient([LLMResponse(text="ok", tool_calls=[])])
    run_with_memory("hi", ToolRegistry(), llm1, session_id="a", store=session_store)
    assert llm1.calls[0]["tools"] == []

    llm2 = FakeLLMClient([LLMResponse(text="ok", tool_calls=[])])
    run_with_profile_memory(
        "hi",
        ToolRegistry(),
        llm2,
        session_id="b",
        session_store=session_store,
        profile_store=profile_store,
    )
    assert "recall_memory" not in {tool["name"] for tool in llm2.calls[0]["tools"]}

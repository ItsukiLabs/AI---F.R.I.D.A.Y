from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.agent_core.tool_registry import ToolRegistry
from backend.memory.profile_store import ProfileStore
from backend.memory.runner import run_with_profile_memory
from backend.memory.store import SessionStore


class FakeLLMClient:
    def __init__(self, responses: list[LLMResponse]):
        self._responses = list(responses)
        self.calls: list[dict] = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": list(messages), "tools": tools, "system": system})
        return self._responses.pop(0)


def _remember_call(fact: str, category: str, call_id: str = "call_1"):
    return LLMResponse(
        text=None,
        tool_calls=[
            ToolCallRequest(id=call_id, name="remember_user_fact", arguments={"fact": fact, "category": category})
        ],
        stop_reason="tool_use",
    )


def test_turn_that_remembers_a_fact_persists_profile_json(tmp_path):
    session_store = SessionStore(base_dir=tmp_path / "sessions")
    profile_store = ProfileStore(base_dir=tmp_path / "profile")
    llm = FakeLLMClient(
        [
            _remember_call("Allergic to peanuts.", "health"),
            LLMResponse(text="Got it.", tool_calls=[]),
        ]
    )

    run_with_profile_memory(
        "remember I'm allergic to peanuts",
        ToolRegistry(),
        llm,
        session_id="s1",
        session_store=session_store,
        profile_store=profile_store,
    )

    assert (tmp_path / "profile" / "profile.json").exists()
    loaded = profile_store.load()
    assert loaded.active_facts()[0].text == "Allergic to peanuts."


def test_turn_without_fact_tool_call_does_not_write_profile_json(tmp_path):
    session_store = SessionStore(base_dir=tmp_path / "sessions")
    profile_store = ProfileStore(base_dir=tmp_path / "profile")
    llm = FakeLLMClient([LLMResponse(text="Sure, no facts here.", tool_calls=[])])

    run_with_profile_memory(
        "what's the weather like",
        ToolRegistry(),
        llm,
        session_id="s1",
        session_store=session_store,
        profile_store=profile_store,
    )

    assert not (tmp_path / "profile" / "profile.json").exists()


def test_profile_is_visible_across_different_session_ids(tmp_path):
    """The test that proves the point of M2c: unlike Session (scoped to one
    session_id), a fact remembered in one session is recalled starting a
    completely different session_id, as long as the profile_store is shared."""
    session_store = SessionStore(base_dir=tmp_path / "sessions")
    profile_store = ProfileStore(base_dir=tmp_path / "profile")

    llm1 = FakeLLMClient(
        [
            _remember_call("Name is Ernold.", "identity"),
            LLMResponse(text="Got it.", tool_calls=[]),
        ]
    )
    run_with_profile_memory(
        "remember my name is Ernold",
        ToolRegistry(),
        llm1,
        session_id="session-A",
        session_store=session_store,
        profile_store=profile_store,
    )

    llm2 = FakeLLMClient([LLMResponse(text="Your name is Ernold.", tool_calls=[])])
    run_with_profile_memory(
        "what's my name?",
        ToolRegistry(),
        llm2,
        session_id="session-B",  # deliberately a different session_id
        session_store=session_store,
        profile_store=profile_store,
    )

    assert "Name is Ernold." in llm2.calls[0]["system"]
    # and session-B's own history never saw session-A's turns
    assert llm2.calls[0]["messages"] == [{"role": "user", "content": "what's my name?"}]


def test_supersede_flow_across_two_separate_calls(tmp_path):
    session_store = SessionStore(base_dir=tmp_path / "sessions")
    profile_store = ProfileStore(base_dir=tmp_path / "profile")

    llm1 = FakeLLMClient(
        [
            _remember_call("Lives in Bandung.", "location"),
            LLMResponse(text="Got it.", tool_calls=[]),
        ]
    )
    run_with_profile_memory(
        "remember I live in Bandung",
        ToolRegistry(),
        llm1,
        session_id="s1",
        session_store=session_store,
        profile_store=profile_store,
    )

    old_id = profile_store.load().active_facts()[0].id

    llm2 = FakeLLMClient(
        [
            LLMResponse(
                text=None,
                tool_calls=[
                    ToolCallRequest(
                        id="call_2",
                        name="remember_user_fact",
                        arguments={
                            "fact": "Lives in Jakarta.",
                            "category": "location",
                            "supersedes": old_id,
                        },
                    )
                ],
                stop_reason="tool_use",
            ),
            LLMResponse(text="Updated.", tool_calls=[]),
        ]
    )
    run_with_profile_memory(
        "actually I moved to Jakarta",
        ToolRegistry(),
        llm2,
        session_id="s2",  # a different session again
        session_store=session_store,
        profile_store=profile_store,
    )

    final = profile_store.load()
    statuses = {f.id: f.status for f in final.facts}
    assert statuses[old_id] == "superseded"
    assert final.active_facts()[0].text == "Lives in Jakarta."

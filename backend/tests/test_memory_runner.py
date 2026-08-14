from backend.agent_core.llm_client import LLMResponse
from backend.agent_core.tool_registry import ToolRegistry
from backend.memory.runner import run_with_memory
from backend.memory.store import SessionStore


class FakeLLMClient:
    def __init__(self, responses: list[LLMResponse]):
        self._responses = list(responses)
        self.calls: list[dict] = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": list(messages), "tools": tools, "system": system})
        return self._responses.pop(0)


def test_run_with_memory_creates_and_persists_a_new_session(tmp_path):
    store = SessionStore(base_dir=tmp_path)
    llm = FakeLLMClient([LLMResponse(text="Hi!", tool_calls=[])])

    result = run_with_memory("hello", ToolRegistry(), llm, session_id="s1", store=store)

    assert result.text == "Hi!"
    loaded = store.load("s1")
    assert loaded is not None
    assert loaded.messages[0] == {"role": "user", "content": "hello"}
    assert loaded.messages[1] == {
        "role": "assistant",
        "content": [{"type": "text", "text": "Hi!"}],
    }


def test_run_with_memory_continues_an_existing_session(tmp_path):
    store = SessionStore(base_dir=tmp_path)
    llm = FakeLLMClient(
        [
            LLMResponse(text="My name is F.R.I.D.A.Y.", tool_calls=[]),
            LLMResponse(text="You just asked my name.", tool_calls=[]),
        ]
    )

    run_with_memory("what's your name?", ToolRegistry(), llm, session_id="s1", store=store)
    run_with_memory("what did I just ask?", ToolRegistry(), llm, session_id="s1", store=store)

    loaded = store.load("s1")
    assert loaded is not None
    assert len(loaded.messages) == 4
    assert loaded.messages[2] == {"role": "user", "content": "what did I just ask?"}

    second_call_messages = llm.calls[1]["messages"]
    assert second_call_messages[0]["content"] == "what's your name?"

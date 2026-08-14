from backend.agent_core.llm_client import LLMResponse
from backend.memory.compaction import SUMMARIZATION_SYSTEM_PROMPT, compact
from backend.memory.session import Session


class FakeLLMClient:
    """Same test-double pattern as test_agent_loop.py — scripted responses, records calls."""

    def __init__(self, responses: list[LLMResponse]):
        self._responses = list(responses)
        self.calls: list[dict] = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": list(messages), "tools": tools, "system": system})
        return self._responses.pop(0)


def _session_with_turns(n_pairs: int) -> Session:
    session = Session.new("s1")
    for i in range(n_pairs):
        session.messages.append({"role": "user", "content": f"user turn {i}"})
        session.messages.append({"role": "assistant", "content": f"assistant turn {i}"})
    return session


def test_compact_folds_old_turns_into_summary_and_keeps_recent_tail():
    session = _session_with_turns(5)  # 10 messages total
    llm = FakeLLMClient([LLMResponse(text="Summary of the early conversation.")])

    changed = compact(session, llm, keep_recent_messages=4)

    assert changed is True
    assert session.summary == "Summary of the early conversation."
    assert len(session.messages) == 4
    assert session.compaction_count == 1
    assert len(llm.calls) == 1
    assert llm.calls[0]["system"] == SUMMARIZATION_SYSTEM_PROMPT
    assert llm.calls[0]["tools"] == []


def test_compact_moves_dropped_turns_into_archived_turns_in_order():
    session = _session_with_turns(5)
    original_first_six = session.messages[:6]
    llm = FakeLLMClient([LLMResponse(text="summary")])

    compact(session, llm, keep_recent_messages=4)

    assert session.archived_turns == original_first_six


def test_compact_returns_false_when_history_too_short_to_cut_safely():
    session = _session_with_turns(2)  # 4 messages
    llm = FakeLLMClient([])

    changed = compact(session, llm, keep_recent_messages=6)

    assert changed is False
    assert session.compaction_count == 0
    assert len(llm.calls) == 0


def test_compact_never_splits_a_tool_use_tool_result_pair():
    session = Session.new("s1")
    session.messages = [
        {"role": "user", "content": "do something"},
        {
            "role": "assistant",
            "content": [{"type": "tool_use", "id": "call_1", "name": "x", "input": {}}],
        },
        {
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": "call_1", "content": "ok"}],
        },
        {"role": "assistant", "content": "done"},
    ]
    llm = FakeLLMClient([LLMResponse(text="summary")])

    # keep_recent_messages=1 targets a cut near index 3, but every candidate
    # in range (indices 1-3) is either a tool_use/tool_result turn or an
    # assistant turn, not a plain user string — and index 0 is excluded
    # because cutting there would summarize nothing. No safe boundary exists,
    # so compact() must refuse rather than produce an invalid split.
    changed = compact(session, llm, keep_recent_messages=1)

    assert changed is False
    assert len(llm.calls) == 0


def test_compact_is_recursive_second_call_threads_previous_summary():
    session = _session_with_turns(5)
    llm = FakeLLMClient(
        [
            LLMResponse(text="First summary."),
            LLMResponse(text="Second summary, building on the first."),
        ]
    )

    compact(session, llm, keep_recent_messages=4)
    session.messages.append({"role": "user", "content": "new user turn"})
    session.messages.append({"role": "assistant", "content": "new assistant turn"})
    session.messages.append({"role": "user", "content": "another user turn"})
    session.messages.append({"role": "assistant", "content": "another assistant turn"})
    compact(session, llm, keep_recent_messages=4)

    second_call_prompt = llm.calls[1]["messages"][0]["content"]
    assert "First summary." in second_call_prompt
    assert session.summary == "Second summary, building on the first."

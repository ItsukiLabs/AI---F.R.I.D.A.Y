"""Session integration for run_agent() — test_agent_loop.py itself is left
untouched and stays the regression guard proving session=None behavior is
unchanged (every test there omits the new parameter).
"""

from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.agent_core.loop import DEFAULT_SYSTEM_PROMPT, run_agent
from backend.agent_core.tool_registry import ToolRegistry
from backend.memory.compaction import SUMMARIZATION_SYSTEM_PROMPT
from backend.memory.session import Session
from backend.schemas import ToolContract

ADD_CONTRACT = ToolContract(
    name="add",
    version="1.0.0",
    description="Add two integers.",
    input_schema={
        "type": "object",
        "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
        "required": ["a", "b"],
        "additionalProperties": False,
    },
)


def add(a: int, b: int) -> int:
    return a + b


def _registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ADD_CONTRACT, add)
    return registry


class FakeLLMClient:
    def __init__(self, responses: list[LLMResponse]):
        self._responses = list(responses)
        self.calls: list[dict] = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": list(messages), "tools": tools, "system": system})
        return self._responses.pop(0)


def test_final_answer_turn_is_recorded_in_session_history():
    session = Session.new("s1")
    llm = FakeLLMClient([LLMResponse(text="Hi there!", tool_calls=[])])

    run_agent("hello", _registry(), llm, session=session)

    assert session.messages == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": [{"type": "text", "text": "Hi there!"}]},
    ]


def test_tool_call_turn_preserves_tool_use_and_tool_result_structure_in_session():
    session = Session.new("s1")
    llm = FakeLLMClient(
        [
            LLMResponse(
                text="Let me add those.",
                tool_calls=[ToolCallRequest(id="call_1", name="add", arguments={"a": 2, "b": 3})],
                stop_reason="tool_use",
            ),
            LLMResponse(text="2 + 3 = 5.", tool_calls=[]),
        ]
    )

    run_agent("what's 2+3?", _registry(), llm, session=session)

    tool_result_turn = session.messages[2]
    assert tool_result_turn["content"][0]["tool_use_id"] == "call_1"
    assert tool_result_turn["content"][0]["content"] == "5"


def test_record_usage_updates_session_token_fields():
    session = Session.new("s1")
    llm = FakeLLMClient([LLMResponse(text="ok", tool_calls=[], input_tokens=321, output_tokens=12)])

    run_agent("hello", _registry(), llm, session=session)

    assert session.last_input_tokens == 321
    assert session.last_output_tokens == 12


def test_compaction_triggers_before_the_main_turn_when_threshold_exceeded():
    session = Session.new("s1")
    session.messages = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hey"}] * 4
    session.last_input_tokens = 999_999  # far above any reasonable threshold

    llm = FakeLLMClient(
        [
            LLMResponse(text="Summary of the earlier chat."),  # compaction call
            LLMResponse(text="Sure, continuing.", tool_calls=[]),  # main turn
        ]
    )

    run_agent("keep going", _registry(), llm, session=session, system=DEFAULT_SYSTEM_PROMPT)

    assert len(llm.calls) == 2
    assert llm.calls[0]["system"] == SUMMARIZATION_SYSTEM_PROMPT
    assert llm.calls[1]["system"] == DEFAULT_SYSTEM_PROMPT
    assert session.compaction_count == 1


def test_compaction_safety_margin_is_wired_through_config(monkeypatch):
    # Default threshold is 6000, default margin is 500 (agent_core/config.py).
    # 5800 alone is under threshold, but 5800 + 500 >= 6000 — this only
    # passes if loop.py actually reads the margin from config, not just the
    # raw threshold.
    monkeypatch.delenv("MEMORY_COMPACTION_THRESHOLD_TOKENS", raising=False)
    monkeypatch.delenv("MEMORY_COMPACTION_SAFETY_MARGIN_TOKENS", raising=False)

    session = Session.new("s1")
    session.messages = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hey"}] * 4
    session.last_input_tokens = 5800

    llm = FakeLLMClient(
        [
            LLMResponse(text="Summary of the earlier chat."),
            LLMResponse(text="Sure, continuing.", tool_calls=[]),
        ]
    )

    run_agent("keep going", _registry(), llm, session=session)

    assert session.compaction_count == 1


def test_session_none_behavior_is_unchanged():
    llm = FakeLLMClient([LLMResponse(text="Hi there!", tool_calls=[])])

    result = run_agent("hello", _registry(), llm)

    assert result.text == "Hi there!"

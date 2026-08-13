from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.agent_core.loop import run_agent
from backend.agent_core.tool_registry import ToolRegistry
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


class FakeLLMClient:
    """Test double — returns pre-scripted responses, one per call, in order."""

    def __init__(self, responses: list[LLMResponse]):
        self._responses = list(responses)
        self.calls: list[dict] = []

    def send(self, messages, tools, system):
        # Snapshot the list — run_agent mutates the same list object across
        # iterations by appending, so a bare reference would make every
        # recorded call show the final (post-loop) message history instead
        # of what was actually sent at that point in time.
        self.calls.append({"messages": list(messages), "tools": tools, "system": system})
        return self._responses.pop(0)


def _registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ADD_CONTRACT, add)
    return registry


def test_final_answer_without_tool_call():
    llm = FakeLLMClient([LLMResponse(text="Hi there!", tool_calls=[], stop_reason="end_turn")])

    result = run_agent("hello", _registry(), llm)

    assert result.text == "Hi there!"
    assert result.iterations == 1
    assert not result.exceeded_max_iterations
    assert len(llm.calls) == 1


def test_tool_call_then_final_answer():
    llm = FakeLLMClient(
        [
            LLMResponse(
                text="Let me add those.",
                tool_calls=[ToolCallRequest(id="call_1", name="add", arguments={"a": 2, "b": 3})],
                stop_reason="tool_use",
            ),
            LLMResponse(text="2 + 3 = 5.", tool_calls=[], stop_reason="end_turn"),
        ]
    )

    result = run_agent("what's 2+3?", _registry(), llm)

    assert result.text == "2 + 3 = 5."
    assert result.iterations == 2

    second_call_messages = llm.calls[1]["messages"]
    tool_result = second_call_messages[-1]["content"][0]
    assert tool_result["tool_use_id"] == "call_1"
    assert tool_result["content"] == "5"
    assert tool_result["is_error"] is False


def test_invalid_tool_args_trigger_reflection_then_retry():
    llm = FakeLLMClient(
        [
            LLMResponse(
                text=None,
                tool_calls=[
                    ToolCallRequest(id="call_1", name="add", arguments={"a": "not-a-number", "b": 3})
                ],
                stop_reason="tool_use",
            ),
            LLMResponse(
                text=None,
                tool_calls=[ToolCallRequest(id="call_2", name="add", arguments={"a": 2, "b": 3})],
                stop_reason="tool_use",
            ),
            LLMResponse(text="2 + 3 = 5.", tool_calls=[], stop_reason="end_turn"),
        ]
    )

    result = run_agent("add 2 and 3", _registry(), llm)

    assert result.text == "2 + 3 = 5."
    assert result.iterations == 3

    second_call_messages = llm.calls[1]["messages"]
    reflection = second_call_messages[-1]["content"][0]
    assert reflection["is_error"] is True
    assert "Invalid arguments" in reflection["content"]


def test_exceeds_max_iterations_stops_without_infinite_loop():
    responses = [
        LLMResponse(
            text=None,
            tool_calls=[ToolCallRequest(id=f"call_{i}", name="add", arguments={"a": 1, "b": 1})],
            stop_reason="tool_use",
        )
        for i in range(3)
    ]
    llm = FakeLLMClient(responses)

    result = run_agent("keep adding forever", _registry(), llm, max_iterations=3)

    assert result.exceeded_max_iterations is True
    assert result.iterations == 3
    assert len(llm.calls) == 3

"""M4: run_agent re-reads the registry every iteration, and the prompt forbids faking actions."""

from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.agent_core.loop import DEFAULT_SYSTEM_PROMPT, run_agent
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

LOADER_CONTRACT = ToolContract(
    name="load_math",
    version="1.0.0",
    description="Load math tools.",
    input_schema={"type": "object", "properties": {}, "additionalProperties": False},
)


class FakeLLMClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": list(messages), "tools": tools, "system": system})
        return self._responses.pop(0)


def _call(name, arguments, call_id):
    return LLMResponse(
        text=None,
        tool_calls=[ToolCallRequest(id=call_id, name=name, arguments=arguments)],
        stop_reason="tool_use",
    )


def _tool_names(call):
    return [tool["name"] for tool in call["tools"]]


def test_tool_bound_mid_turn_is_visible_and_callable_on_the_next_iteration():
    registry = ToolRegistry()

    def load_math():
        registry.bind(ADD_CONTRACT, lambda a, b: a + b)
        return "loaded add"

    registry.register(LOADER_CONTRACT, load_math)
    llm = FakeLLMClient(
        [
            _call("load_math", {}, "call_1"),
            _call("add", {"a": 2, "b": 3}, "call_2"),
            LLMResponse(text="2 + 3 = 5", tool_calls=[]),
        ]
    )

    result = run_agent("what is 2 + 3?", registry, llm)

    assert result.text == "2 + 3 = 5"
    assert _tool_names(llm.calls[0]) == ["load_math"]
    assert _tool_names(llm.calls[1]) == ["load_math", "add"]
    add_result = llm.calls[2]["messages"][-1]["content"][0]
    assert add_result["content"] == "5"
    assert add_result["is_error"] is False


def test_default_prompt_forbids_claiming_actions_that_did_not_happen():
    assert "never claim to have done something you didn't" in DEFAULT_SYSTEM_PROMPT
    assert "never use an unrelated tool" in DEFAULT_SYSTEM_PROMPT


def test_registry_bind_is_idempotent_and_rejects_a_different_tool_under_same_name():
    registry = ToolRegistry()

    assert registry.bind(ADD_CONTRACT, lambda a, b: a + b) is True
    assert registry.bind(ADD_CONTRACT, lambda a, b: a + b) is False
    assert registry.has("add")

    impostor = ToolContract(
        name="add",
        version="1.0.0",
        description="Concatenate strings.",
        input_schema={"type": "object", "properties": {}},
    )
    try:
        registry.bind(impostor, lambda: None)
    except ValueError as exc:
        assert "different tool" in str(exc)
    else:
        raise AssertionError("binding a different tool under an existing name must raise")

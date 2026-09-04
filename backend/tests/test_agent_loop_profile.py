"""Profile integration for run_agent() — test_agent_loop.py itself is left
untouched and stays the regression guard proving profile=None behavior is
unchanged (every test there omits the new parameter).
"""

from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.agent_core.loop import DEFAULT_SYSTEM_PROMPT, run_agent
from backend.agent_core.tool_registry import ToolRegistry
from backend.agent_core.tools.profile_tools import make_profile_tools
from backend.memory.profile import Profile


class FakeLLMClient:
    def __init__(self, responses: list[LLMResponse]):
        self._responses = list(responses)
        self.calls: list[dict] = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": list(messages), "tools": tools, "system": system})
        return self._responses.pop(0)


def test_profile_none_behavior_is_unchanged():
    llm = FakeLLMClient([LLMResponse(text="Hi there!", tool_calls=[])])

    result = run_agent("hello", ToolRegistry(), llm)

    assert result.text == "Hi there!"
    assert llm.calls[0]["system"] == DEFAULT_SYSTEM_PROMPT


def test_empty_profile_does_not_alter_system_prompt():
    profile = Profile.new()
    llm = FakeLLMClient([LLMResponse(text="Hi there!", tool_calls=[])])

    run_agent("hello", ToolRegistry(), llm, profile=profile)

    assert llm.calls[0]["system"] == DEFAULT_SYSTEM_PROMPT


def test_active_facts_are_injected_into_system_prompt():
    profile = Profile.new()
    profile.remember_fact("Allergic to peanuts.", category="health")
    llm = FakeLLMClient([LLMResponse(text="Hi there!", tool_calls=[])])

    run_agent("hello", ToolRegistry(), llm, profile=profile)

    assert "Allergic to peanuts." in llm.calls[0]["system"]
    assert DEFAULT_SYSTEM_PROMPT in llm.calls[0]["system"]


def test_tool_mutation_in_one_iteration_is_visible_in_the_next_iterations_system_prompt():
    profile = Profile.new()
    registry = ToolRegistry()
    for contract, fn in make_profile_tools(profile):
        registry.register(contract, fn)

    llm = FakeLLMClient(
        [
            LLMResponse(
                text=None,
                tool_calls=[
                    ToolCallRequest(
                        id="call_1",
                        name="remember_user_fact",
                        arguments={"fact": "Allergic to peanuts.", "category": "health"},
                    )
                ],
                stop_reason="tool_use",
            ),
            LLMResponse(text="Got it, noted.", tool_calls=[]),
        ]
    )

    run_agent("remember that I'm allergic to peanuts", registry, llm, profile=profile)

    assert "Allergic to peanuts." not in llm.calls[0]["system"]
    assert "Allergic to peanuts." in llm.calls[1]["system"]

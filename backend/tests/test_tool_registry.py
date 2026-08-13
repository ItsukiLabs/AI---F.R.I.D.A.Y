import pytest

from backend.agent_core.tool_registry import ToolRegistry
from backend.schemas import ToolContract

CONTRACT = ToolContract(
    name="get_weather",
    version="1.0.0",
    description="Get the weather.",
    input_schema={
        "type": "object",
        "properties": {"location": {"type": "string"}},
        "required": ["location"],
    },
)


def dummy(location: str) -> str:
    return f"sunny in {location}"


def test_register_and_get():
    registry = ToolRegistry()
    registry.register(CONTRACT, dummy)

    registered = registry.get("get_weather")

    assert registered.contract is CONTRACT
    assert registered.fn is dummy


def test_register_duplicate_raises():
    registry = ToolRegistry()
    registry.register(CONTRACT, dummy)

    with pytest.raises(ValueError):
        registry.register(CONTRACT, dummy)


def test_get_missing_raises_keyerror():
    registry = ToolRegistry()

    with pytest.raises(KeyError):
        registry.get("nonexistent")


def test_to_llm_tools_matches_anthropic_tool_format():
    registry = ToolRegistry()
    registry.register(CONTRACT, dummy)

    tools = registry.to_llm_tools()

    assert tools == [
        {
            "name": "get_weather",
            "description": "Get the weather.",
            "input_schema": CONTRACT.input_schema,
        }
    ]

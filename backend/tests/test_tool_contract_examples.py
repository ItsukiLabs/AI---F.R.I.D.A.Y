"""Contract 1.1.0 (M4): domain, examples, content_hash, and how examples reach the LLM."""

import pytest
from pydantic import ValidationError

from backend.agent_core.llm_client import tool_contract_to_anthropic_tool
from backend.schemas import CONTRACT_VERSION, PermissionTier, ToolContract, ToolExample

SCHEMA = {
    "type": "object",
    "properties": {
        "device": {"type": "string"},
        "brightness": {"type": "integer", "minimum": 0, "maximum": 100},
    },
    "required": ["device"],
    "additionalProperties": False,
}


def _contract(**overrides) -> ToolContract:
    fields = {
        "name": "set_brightness",
        "version": "1.0.0",
        "description": "Set a light's brightness.",
        "input_schema": SCHEMA,
    }
    fields.update(overrides)
    return ToolContract(**fields)


def test_contract_version_is_1_1_0():
    assert CONTRACT_VERSION == "1.1.0"
    assert _contract().contract_version == "1.1.0"


def test_pre_m4_contract_still_validates_with_defaults():
    contract = _contract()

    assert contract.domain == "general"
    assert contract.examples == []


@pytest.mark.parametrize("bad_domain", ["Device", "device-lamp", "1lamp", ""])
def test_invalid_domain_is_rejected(bad_domain):
    with pytest.raises(ValidationError):
        _contract(domain=bad_domain)


def test_valid_examples_are_accepted():
    contract = _contract(
        domain="device_lamp",
        examples=[
            ToolExample(scenario="User: 'agak gelap nih'", arguments={"device": "lampu_tamu", "brightness": 80}),
            {"scenario": "Dim the bedroom light", "arguments": {"device": "lampu_kamar", "brightness": 20}},
        ],
    )

    assert len(contract.examples) == 2
    assert contract.examples[1].arguments["brightness"] == 20


@pytest.mark.parametrize(
    "arguments",
    [
        {"brightness": 50},  # missing required "device"
        {"device": "lampu", "brightness": "high"},  # wrong type
        {"device": "lampu", "brightness": 150},  # out of range
        {"device": "lampu", "color": "red"},  # additionalProperties
    ],
)
def test_example_not_matching_input_schema_is_rejected(arguments):
    with pytest.raises(ValidationError, match="example 0"):
        _contract(examples=[ToolExample(scenario="bad example", arguments=arguments)])


def test_example_with_blank_scenario_is_rejected():
    with pytest.raises(ValidationError):
        ToolExample(scenario="   ", arguments={})


def test_content_hash_is_stable_sha256_hex():
    first = _contract()
    second = _contract()

    assert first.content_hash == second.content_hash
    assert len(first.content_hash) == 64
    int(first.content_hash, 16)


def test_content_hash_ignores_version_numbers():
    assert _contract(version="1.0.0").content_hash == _contract(version="2.3.4").content_hash
    assert _contract().content_hash == _contract(contract_version="1.0.0").content_hash


@pytest.mark.parametrize(
    "change",
    [
        {"description": "Set a light's brightness level."},
        {"domain": "device_lamp"},
        {"permission_tier": PermissionTier.CRITICAL},
        {"examples": [ToolExample(scenario="dim it", arguments={"device": "lampu"})]},
        {"input_schema": {**SCHEMA, "required": []}},
    ],
)
def test_content_hash_changes_when_content_changes(change):
    assert _contract(**change).content_hash != _contract().content_hash


def test_llm_tool_without_examples_is_unchanged():
    contract = _contract()

    assert tool_contract_to_anthropic_tool(contract) == {
        "name": "set_brightness",
        "description": "Set a light's brightness.",
        "input_schema": SCHEMA,
    }


def test_llm_tool_description_lists_examples_with_arguments():
    contract = _contract(
        examples=[ToolExample(scenario="User: 'agak gelap nih'", arguments={"device": "lampu_tamu", "brightness": 80})]
    )

    description = tool_contract_to_anthropic_tool(contract)["description"]

    assert description.startswith("Set a light's brightness.")
    assert "Examples:" in description
    assert "User: 'agak gelap nih'" in description
    assert '{"brightness": 80, "device": "lampu_tamu"}' in description

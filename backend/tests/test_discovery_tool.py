"""M4 find_tools: contract built from the catalog, binding hits into the turn registry."""

import jsonschema
import pytest

from backend.agent_core.tool_registry import ToolRegistry
from backend.registry import FIND_TOOLS_NAME, ToolCatalog, build_find_tools_contract, make_discovery_tool
from backend.registry.discovery_tool import FIND_TOOLS_MAX_LIMIT
from backend.schemas import PermissionTier, ToolContract, ToolExample


def _contract(name, description, domain, examples=None, tier=PermissionTier.STANDARD):
    return ToolContract(
        name=name,
        version="1.0.0",
        description=description,
        domain=domain,
        input_schema={"type": "object", "properties": {}},
        examples=examples or [],
        permission_tier=tier,
    )


def _catalog() -> ToolCatalog:
    catalog = ToolCatalog()
    catalog.register(_contract("get_current_time", "Get the current time.", "time"), lambda: "now")
    catalog.sync(
        "lamp_adapter",
        [
            (
                _contract(
                    "lamp_set_power",
                    "Turn the lamp on or off.",
                    "device_lamp",
                    examples=[ToolExample(scenario="User: 'nyalakan lampu'", arguments={})],
                    tier=PermissionTier.CRITICAL,
                ),
                lambda: "switched",
            ),
            (_contract("lamp_get_state", "Read whether the lamp is on.", "device_lamp"), lambda: "on"),
        ],
    )
    catalog.describe_domain("device_lamp", "Lampu gantung di ruang tamu")
    return catalog


def test_contract_lists_discoverable_domains_and_constrains_domain_argument():
    contract = build_find_tools_contract(_catalog())

    assert contract.name == FIND_TOOLS_NAME
    assert contract.domain == "registry"
    assert contract.permission_tier is PermissionTier.READ_ONLY
    assert "- device_lamp: Lampu gantung di ruang tamu" in contract.description
    assert "time" not in contract.description.split("Domains you can search:")[1]
    assert contract.input_schema["properties"]["domain"]["enum"] == ["device_lamp"]
    assert contract.examples  # validated against input_schema at construction


def test_contract_without_discoverable_tools_has_no_domain_enum():
    catalog = ToolCatalog()
    catalog.register(_contract("get_current_time", "Get the time.", "time"), lambda: "now")

    contract = build_find_tools_contract(catalog)

    assert "- (none)" in contract.description
    assert "enum" not in contract.input_schema["properties"]["domain"]


def test_find_tools_binds_hits_into_turn_registry():
    catalog = _catalog()
    registry = ToolRegistry()
    contract, find_tools = make_discovery_tool(catalog, registry)

    result = find_tools(query="lamp")

    jsonschema.validate(result, contract.output_schema)
    assert result["count"] == 2
    assert {tool["status"] for tool in result["tools"]} == {"loaded"}
    assert registry.has("lamp_set_power") and registry.has("lamp_get_state")
    assert registry.get("lamp_set_power").fn() == "switched"
    assert "next step" in result["note"]


def test_find_tools_reports_tier_and_first_example():
    registry = ToolRegistry()
    _, find_tools = make_discovery_tool(_catalog(), registry)

    result = find_tools(query="nyalakan")

    (tool,) = result["tools"]
    assert tool["name"] == "lamp_set_power"
    assert tool["permission_tier"] == "critical"
    assert tool["example"] == {"scenario": "User: 'nyalakan lampu'", "arguments": {}}


def test_searching_again_reports_already_available_without_error():
    registry = ToolRegistry()
    _, find_tools = make_discovery_tool(_catalog(), registry)
    find_tools(query="lamp")

    result = find_tools(query="lamp")

    assert {tool["status"] for tool in result["tools"]} == {"already_available"}


def test_pinned_tool_already_in_turn_registry_is_already_available():
    catalog = _catalog()
    registry = ToolRegistry()
    pinned = catalog.get("get_current_time")
    registry.register(pinned.contract, pinned.fn)
    _, find_tools = make_discovery_tool(catalog, registry)

    result = find_tools(query="current time")

    assert [(t["name"], t["status"]) for t in result["tools"]] == [("get_current_time", "already_available")]


def test_no_match_tells_model_to_say_it_cannot():
    registry = ToolRegistry()
    contract, find_tools = make_discovery_tool(_catalog(), registry)

    result = find_tools(query="vacuum robot")

    jsonschema.validate(result, contract.output_schema)
    assert result["count"] == 0
    assert result["tools"] == []
    assert "tell the user plainly" in result["note"]
    assert registry.registered_tools() == []


def test_limit_is_capped():
    catalog = ToolCatalog()
    catalog.sync(
        "many",
        [(_contract(f"lamp_tool_{i}", "A lamp tool.", "device_many"), lambda: None) for i in range(15)],
    )
    registry = ToolRegistry()
    _, find_tools = make_discovery_tool(catalog, registry)

    result = find_tools(query="lamp", limit=50)

    assert result["count"] == FIND_TOOLS_MAX_LIMIT


def test_name_collision_with_different_tool_in_turn_registry_raises():
    registry = ToolRegistry()
    registry.register(_contract("lamp_set_power", "Something else entirely.", "general"), lambda: None)
    _, find_tools = make_discovery_tool(_catalog(), registry)

    with pytest.raises(ValueError, match="different tool"):
        find_tools(query="lamp")

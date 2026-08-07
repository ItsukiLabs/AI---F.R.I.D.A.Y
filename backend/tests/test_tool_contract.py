import pytest
from pydantic import ValidationError

from backend.schemas import CONTRACT_VERSION, PermissionTier, ToolContract


def _minimal_kwargs(**overrides):
    kwargs = dict(
        name="get_weather",
        version="1.0.0",
        description="Fetch the current weather for a location.",
        input_schema={
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"],
        },
    )
    kwargs.update(overrides)
    return kwargs


def test_minimal_contract_uses_defaults():
    tool = ToolContract(**_minimal_kwargs())

    assert tool.contract_version == CONTRACT_VERSION
    assert tool.permission_tier == PermissionTier.STANDARD
    assert tool.annotations.read_only_hint is False
    assert tool.output_schema is None


@pytest.mark.parametrize("bad_name", ["GetWeather", "get-weather", "1get_weather", ""])
def test_rejects_non_snake_case_name(bad_name):
    with pytest.raises(ValidationError):
        ToolContract(**_minimal_kwargs(name=bad_name))


@pytest.mark.parametrize("bad_version", ["1.0", "v1.0.0", "1.0.0-beta", ""])
def test_rejects_non_semver_version(bad_version):
    with pytest.raises(ValidationError):
        ToolContract(**_minimal_kwargs(version=bad_version))


def test_rejects_blank_description():
    with pytest.raises(ValidationError):
        ToolContract(**_minimal_kwargs(description="   "))


def test_permission_tier_is_explicit_and_serializable():
    tool = ToolContract(**_minimal_kwargs(permission_tier=PermissionTier.CRITICAL))

    dumped = tool.model_dump(mode="json")

    assert dumped["permission_tier"] == "critical"
    assert dumped["contract_version"] == CONTRACT_VERSION

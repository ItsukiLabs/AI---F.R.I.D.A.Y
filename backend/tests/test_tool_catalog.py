"""M4 ToolCatalog: registration, hash-based sync (ScaleMCP), joint tool+domain search."""

import pytest

from backend.registry import APP_PROVIDER, ToolCatalog
from backend.schemas import ToolContract, ToolExample


def _contract(
    name: str,
    description: str,
    domain: str = "general",
    examples: list[ToolExample] | None = None,
    properties: dict | None = None,
    version: str = "1.0.0",
) -> ToolContract:
    return ToolContract(
        name=name,
        version=version,
        description=description,
        domain=domain,
        input_schema={"type": "object", "properties": properties or {}},
        examples=examples or [],
    )


def _fn(result="ok"):
    return lambda **kwargs: result


def _lamp_tools():
    return [
        (
            _contract(
                "lamp_set_power",
                "Turn the lamp on or off.",
                domain="device_lamp",
                properties={"on": {"type": "boolean", "description": "true to switch on"}},
            ),
            _fn(),
        ),
        (
            _contract(
                "lamp_set_brightness",
                "Change how bright the lamp is.",
                domain="device_lamp",
                examples=[ToolExample(scenario="User: 'redupkan sedikit'", arguments={})],
                properties={"level": {"type": "integer", "description": "percentage 0-100"}},
            ),
            _fn(),
        ),
    ]


def _names(hits):
    return [hit.contract.name for hit in hits]


# -- registration ---------------------------------------------------------


def test_register_defaults_to_pinned_app_tool():
    catalog = ToolCatalog()
    catalog.register(_contract("get_current_time", "Get the time."), _fn())

    entry = catalog.get("get_current_time")
    assert entry.pinned is True
    assert entry.provider == APP_PROVIDER
    assert [e.name for e in catalog.pinned_tools()] == ["get_current_time"]
    assert catalog.has_discoverable_tools() is False
    assert catalog.discoverable_domains() == []


def test_register_duplicate_name_raises():
    catalog = ToolCatalog()
    catalog.register(_contract("get_current_time", "Get the time."), _fn())

    with pytest.raises(ValueError, match="already in the catalog"):
        catalog.register(_contract("get_current_time", "Other."), _fn())


def test_get_missing_raises_keyerror():
    with pytest.raises(KeyError):
        ToolCatalog().get("nope")


@pytest.mark.parametrize("bad_provider", ["Lamp", "lamp-1", ""])
def test_invalid_provider_is_rejected(bad_provider):
    catalog = ToolCatalog()
    with pytest.raises(ValueError):
        catalog.register(_contract("a_tool", "A."), _fn(), provider=bad_provider)
    with pytest.raises(ValueError):
        catalog.sync(bad_provider, [])


# -- sync -----------------------------------------------------------------


def test_sync_adds_discoverable_tools_for_provider():
    catalog = ToolCatalog()

    report = catalog.sync("lamp_adapter", _lamp_tools())

    assert report.added == ("lamp_set_brightness", "lamp_set_power")
    assert report.updated == report.removed == report.unchanged == ()
    assert report.changed is True
    entry = catalog.get("lamp_set_power")
    assert entry.provider == "lamp_adapter"
    assert entry.pinned is False
    assert catalog.has_discoverable_tools() is True


def test_sync_same_tools_again_is_unchanged():
    catalog = ToolCatalog()
    catalog.sync("lamp_adapter", _lamp_tools())

    report = catalog.sync("lamp_adapter", _lamp_tools())

    assert report.unchanged == ("lamp_set_brightness", "lamp_set_power")
    assert report.changed is False


def test_sync_detects_changed_content_by_hash():
    catalog = ToolCatalog()
    catalog.sync("lamp_adapter", _lamp_tools())
    tools = _lamp_tools()
    tools[0] = (_contract("lamp_set_power", "Switch the lamp on or off.", domain="device_lamp"), _fn())

    report = catalog.sync("lamp_adapter", tools)

    assert report.updated == ("lamp_set_power",)
    assert report.unchanged == ("lamp_set_brightness",)
    assert catalog.get("lamp_set_power").contract.description == "Switch the lamp on or off."


def test_sync_version_bump_alone_is_unchanged_but_newest_contract_is_kept():
    catalog = ToolCatalog()
    catalog.sync("lamp_adapter", [(_contract("lamp_set_power", "Turn on/off.", domain="device_lamp"), _fn())])

    report = catalog.sync(
        "lamp_adapter",
        [(_contract("lamp_set_power", "Turn on/off.", domain="device_lamp", version="1.1.0"), _fn())],
    )

    assert report.changed is False
    assert catalog.get("lamp_set_power").contract.version == "1.1.0"


def test_sync_pinned_policy_change_counts_as_update():
    catalog = ToolCatalog()
    catalog.sync("lamp_adapter", _lamp_tools())

    report = catalog.sync("lamp_adapter", _lamp_tools(), pinned=True)

    assert report.updated == ("lamp_set_brightness", "lamp_set_power")
    assert catalog.get("lamp_set_power").pinned is True


def test_sync_removes_tools_no_longer_offered():
    catalog = ToolCatalog()
    catalog.sync("lamp_adapter", _lamp_tools())

    report = catalog.sync("lamp_adapter", _lamp_tools()[:1])

    assert report.removed == ("lamp_set_brightness",)
    assert not catalog.has("lamp_set_brightness")
    assert catalog.search("bright") == []


def test_sync_never_touches_other_providers_tools():
    catalog = ToolCatalog()
    catalog.register(_contract("get_current_time", "Get the time."), _fn())
    catalog.sync("lamp_adapter", _lamp_tools())

    catalog.sync("lamp_adapter", [])

    assert catalog.has("get_current_time")
    assert not catalog.has("lamp_set_power")


def test_sync_keeps_newest_callable_even_when_unchanged():
    catalog = ToolCatalog()
    catalog.sync("lamp_adapter", [(_lamp_tools()[0][0], _fn("old connection"))])

    catalog.sync("lamp_adapter", [(_lamp_tools()[0][0], _fn("new connection"))])

    assert catalog.get("lamp_set_power").fn() == "new connection"


def test_sync_name_collision_with_other_provider_raises_and_changes_nothing():
    catalog = ToolCatalog()
    catalog.sync("lamp_adapter", _lamp_tools())
    before = {e.name: e for e in catalog.entries()}

    with pytest.raises(ValueError, match="collides"):
        catalog.sync(
            "other_adapter",
            [
                (_contract("fan_set_speed", "Fan speed.", domain="device_fan"), _fn()),
                (_contract("lamp_set_power", "Impostor.", domain="device_fan"), _fn()),
            ],
        )

    assert {e.name: e for e in catalog.entries()} == before


def test_sync_duplicate_name_in_offer_raises():
    catalog = ToolCatalog()
    tool = _lamp_tools()[0]

    with pytest.raises(ValueError, match="twice"):
        catalog.sync("lamp_adapter", [tool, tool])


# -- search ---------------------------------------------------------------


def _catalog_with_lamp_and_time() -> ToolCatalog:
    catalog = ToolCatalog()
    catalog.register(_contract("get_current_time", "Get the current date and time.", domain="time"), _fn())
    catalog.sync("lamp_adapter", _lamp_tools())
    catalog.describe_domain("device_lamp", "Lampu gantung di ruang tamu")
    return catalog


def test_search_matches_tool_description():
    hits = _catalog_with_lamp_and_time().search("bright")

    assert _names(hits) == ["lamp_set_brightness"]
    assert hits[0].matched_via == "tool"
    assert hits[0].pinned is False


def test_search_matches_words_that_only_appear_in_examples():
    hits = _catalog_with_lamp_and_time().search("redupkan")

    assert _names(hits) == ["lamp_set_brightness"]


def test_search_matches_parameter_descriptions():
    assert _names(_catalog_with_lamp_and_time().search("percentage")) == ["lamp_set_brightness"]


def test_domain_summary_hit_expands_to_all_tools_of_that_domain():
    hits = _catalog_with_lamp_and_time().search("ruang tamu")

    assert sorted(_names(hits)) == ["lamp_set_brightness", "lamp_set_power"]
    assert {hit.matched_via for hit in hits} == {"domain"}


def test_domain_filter_restricts_results():
    catalog = _catalog_with_lamp_and_time()

    assert _names(catalog.search("time", domain="time")) == ["get_current_time"]
    assert catalog.search("time", domain="device_lamp") == []


def test_search_prefers_all_terms_then_falls_back_to_any_term():
    catalog = _catalog_with_lamp_and_time()

    assert _names(catalog.search("lamp bright")) == ["lamp_set_brightness"]
    assert _names(catalog.search("bright zzzunknown")) == ["lamp_set_brightness"]


@pytest.mark.parametrize("query", ["", "   ", "***", "--"])
def test_search_with_no_word_tokens_returns_empty(query):
    assert _catalog_with_lamp_and_time().search(query) == []


@pytest.mark.parametrize("query", ['lamp" OR *', "NOT lamp", "(lamp", "lamp:power"])
def test_search_treats_fts_syntax_as_literal_words(query):
    # Must not raise sqlite3.OperationalError; operators become plain words.
    _catalog_with_lamp_and_time().search(query)


def test_search_respects_limit_and_rejects_non_positive_limit():
    catalog = _catalog_with_lamp_and_time()

    assert len(catalog.search("lamp", limit=1)) == 1
    with pytest.raises(ValueError):
        catalog.search("lamp", limit=0)


def test_search_sees_tools_synced_after_a_previous_search():
    catalog = _catalog_with_lamp_and_time()
    assert catalog.search("fan") == []

    catalog.sync("fan_adapter", [(_contract("fan_set_speed", "Set the fan speed.", domain="device_fan"), _fn())])

    assert _names(catalog.search("fan")) == ["fan_set_speed"]


def test_discoverable_domains_lists_only_domains_with_discoverable_tools():
    catalog = _catalog_with_lamp_and_time()

    assert catalog.discoverable_domains() == [("device_lamp", "Lampu gantung di ruang tamu")]


def test_describe_domain_rejects_blank_summary_and_bad_domain():
    catalog = ToolCatalog()
    with pytest.raises(ValueError):
        catalog.describe_domain("device_lamp", "  ")
    with pytest.raises(ValueError):
        catalog.describe_domain("Device Lamp", "Lamp.")

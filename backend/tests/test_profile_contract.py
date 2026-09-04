import pytest
from pydantic import ValidationError

from backend.schemas import PROFILE_SCHEMA_VERSION, ProfileFact, ProfileRecord


def test_profile_fact_defaults_to_active_status():
    fact = ProfileFact(
        id="fact_0001",
        text="Allergic to peanuts.",
        category="health",
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )

    assert fact.status == "active"
    assert fact.supersedes is None
    assert fact.superseded_by is None
    assert fact.deleted_reason is None


def test_profile_fact_rejects_invalid_status():
    with pytest.raises(ValidationError):
        ProfileFact(
            id="fact_0001",
            text="x",
            category="misc",
            status="archived",  # not one of active/superseded/deleted
            created_at="2026-01-01T00:00:00+00:00",
            updated_at="2026-01-01T00:00:00+00:00",
        )


def test_profile_record_defaults():
    record = ProfileRecord(
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )

    assert record.schema_version == PROFILE_SCHEMA_VERSION
    assert record.user_id == "primary"
    assert record.facts == []
    assert record.next_fact_seq == 0


def test_profile_record_requires_timestamps():
    with pytest.raises(ValidationError):
        ProfileRecord()

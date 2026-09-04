import pytest

from backend.memory.profile import Profile
from backend.memory.profile_errors import ProfileFactNotFoundError


def test_new_profile_is_not_dirty():
    profile = Profile.new()

    assert profile.dirty is False
    assert profile.facts == []


def test_remember_fact_assigns_sequential_ids():
    profile = Profile.new()

    first = profile.remember_fact("Name is Ernold.", category="identity")
    second = profile.remember_fact("Likes cats.", category="preference")

    assert first.id == "fact_0001"
    assert second.id == "fact_0002"
    assert profile.dirty is True


def test_remember_fact_without_supersedes_just_adds():
    profile = Profile.new()

    fact = profile.remember_fact("Lives in Bandung.", category="location")

    assert fact.status == "active"
    assert profile.active_facts() == [fact]


def test_remember_fact_with_supersedes_flips_old_status_and_links_both_ways():
    profile = Profile.new()
    old = profile.remember_fact("Lives in Bandung.", category="location")

    new = profile.remember_fact("Lives in Jakarta.", category="location", supersedes=old.id)

    assert new.status == "active"
    assert new.supersedes == old.id
    assert old.status == "superseded"
    assert old.superseded_by == new.id
    assert profile.active_facts() == [new]


def test_remember_fact_supersedes_unknown_id_raises():
    profile = Profile.new()

    with pytest.raises(ProfileFactNotFoundError):
        profile.remember_fact("Lives in Jakarta.", category="location", supersedes="fact_9999")


def test_remember_fact_supersedes_already_superseded_fact_raises():
    profile = Profile.new()
    old = profile.remember_fact("Lives in Bandung.", category="location")
    mid = profile.remember_fact("Lives in Jakarta.", category="location", supersedes=old.id)

    with pytest.raises(ProfileFactNotFoundError):
        profile.remember_fact("Lives in Surabaya.", category="location", supersedes=old.id)

    # superseding the currently-active one instead is fine
    latest = profile.remember_fact("Lives in Surabaya.", category="location", supersedes=mid.id)
    assert profile.active_facts() == [latest]


def test_forget_fact_marks_deleted():
    profile = Profile.new()
    fact = profile.remember_fact("Allergic to peanuts.", category="health")
    profile.dirty = False  # reset to isolate forget_fact's own effect

    result = profile.forget_fact(fact.id, reason="no longer true")

    assert result.status == "deleted"
    assert result.deleted_reason == "no longer true"
    assert profile.active_facts() == []
    assert profile.dirty is True


def test_forget_fact_is_idempotent_on_already_deleted():
    profile = Profile.new()
    fact = profile.remember_fact("Allergic to peanuts.", category="health")
    profile.forget_fact(fact.id)
    profile.dirty = False

    result = profile.forget_fact(fact.id)  # second forget, same fact

    assert result.status == "deleted"
    assert profile.dirty is False  # no-op didn't mark dirty again


def test_forget_fact_unknown_id_raises():
    profile = Profile.new()

    with pytest.raises(ProfileFactNotFoundError):
        profile.forget_fact("fact_9999")


def test_to_context_block_empty_when_no_active_facts():
    profile = Profile.new()

    assert profile.to_context_block() == ""


def test_to_context_block_excludes_superseded_and_deleted():
    profile = Profile.new()
    old = profile.remember_fact("Lives in Bandung.", category="location")
    profile.remember_fact("Lives in Jakarta.", category="location", supersedes=old.id)
    other = profile.remember_fact("Allergic to peanuts.", category="health")
    profile.forget_fact(other.id)

    block = profile.to_context_block()

    assert "Jakarta" in block
    assert "Bandung" not in block
    assert "peanuts" not in block


def test_to_record_and_from_record_round_trip():
    profile = Profile.new()
    old = profile.remember_fact("Lives in Bandung.", category="location")
    profile.remember_fact("Lives in Jakarta.", category="location", supersedes=old.id)

    restored = Profile.from_record(profile.to_record())

    assert restored.user_id == profile.user_id
    assert restored.next_fact_seq == profile.next_fact_seq
    assert [f.model_dump() for f in restored.facts] == [f.model_dump() for f in profile.facts]
    assert restored.dirty is False  # dirty is runtime-only, never persisted

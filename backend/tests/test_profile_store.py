import json
import stat
import sys

import pytest

from backend.memory.profile import Profile
from backend.memory.profile_errors import ProfileLoadError, UnsupportedProfileSchemaError
from backend.memory.profile_store import ProfileStore
from backend.schemas import PROFILE_SCHEMA_VERSION


def _sample_profile() -> Profile:
    profile = Profile.new()
    old = profile.remember_fact("Lives in Bandung.", category="location")
    profile.remember_fact("Lives in Jakarta.", category="location", supersedes=old.id)
    profile.remember_fact("Allergic to peanuts.", category="health")
    return profile


def test_save_then_load_round_trips_all_fields(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    original = _sample_profile()

    store.save(original)
    loaded = store.load()

    assert loaded is not None
    assert loaded.user_id == original.user_id
    assert loaded.next_fact_seq == original.next_fact_seq
    assert [f.model_dump() for f in loaded.facts] == [f.model_dump() for f in original.facts]


def test_save_persists_the_refreshed_updated_at(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    profile = _sample_profile()

    store.save(profile)
    loaded = store.load()

    assert profile.updated_at  # save() populated it
    assert loaded.updated_at == profile.updated_at


def test_load_missing_profile_returns_none(tmp_path):
    store = ProfileStore(base_dir=tmp_path)

    assert store.load() is None


def test_load_corrupt_json_raises_profile_load_error_not_silently_none(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "profile.json").write_text("{not valid json", encoding="utf-8")

    with pytest.raises(ProfileLoadError):
        store.load()


def test_load_unsupported_schema_version_raises_specific_error(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "999.0.0",
        "user_id": "primary",
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "facts": [],
        "next_fact_seq": 0,
    }
    (tmp_path / "profile.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(UnsupportedProfileSchemaError):
        store.load()


def test_load_missing_required_field_raises_rather_than_silently_defaulting(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    # "text" is required on every fact — a file missing it must not be
    # silently accepted with a made-up default.
    payload = {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "user_id": "primary",
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "facts": [
            {
                "id": "fact_0001",
                "category": "misc",
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:00+00:00",
            }
        ],
        "next_fact_seq": 1,
    }
    (tmp_path / "profile.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ProfileLoadError):
        store.load()


def test_save_never_leaves_a_temp_file_treated_as_the_profile(tmp_path):
    store = ProfileStore(base_dir=tmp_path)

    store.save(Profile.new())

    files = sorted(p.name for p in tmp_path.iterdir())
    assert files == ["profile.json"]  # no leftover .tmp-* file
    assert store.load() is not None


def test_save_unicode_and_emoji_content_round_trips_exactly(tmp_path):
    store = ProfileStore(base_dir=tmp_path)
    profile = Profile.new()
    profile.remember_fact("こんにちは、猫が好きです 🐱", category="preference")

    store.save(profile)
    loaded = store.load()

    assert loaded.facts[0].text == profile.facts[0].text


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX permission bits aren't meaningful on Windows")
def test_save_restricts_file_permissions_to_owner_on_posix(tmp_path):
    store = ProfileStore(base_dir=tmp_path)

    store.save(Profile.new())

    mode = (tmp_path / "profile.json").stat().st_mode
    assert stat.S_IMODE(mode) == stat.S_IRUSR | stat.S_IWUSR

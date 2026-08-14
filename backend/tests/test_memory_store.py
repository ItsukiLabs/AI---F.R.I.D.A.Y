import json
import stat
import sys

import pytest

from backend.memory.errors import SessionLoadError, UnsupportedSessionSchemaError
from backend.memory.session import Session
from backend.memory.store import SessionStore
from backend.schemas import MEMORY_SCHEMA_VERSION


def _sample_session() -> Session:
    session = Session.new("test-session")
    session.messages = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello!"},
    ]
    session.summary = "User greeted the assistant."
    session.archived_turns = [{"role": "user", "content": "an old turn"}]
    session.compaction_count = 1
    session.last_input_tokens = 42
    session.last_output_tokens = 7
    return session


def test_save_then_load_round_trips_all_fields(tmp_path):
    store = SessionStore(base_dir=tmp_path)
    original = _sample_session()

    store.save(original)
    loaded = store.load("test-session")

    assert loaded is not None
    assert loaded.session_id == original.session_id
    assert loaded.created_at == original.created_at
    assert loaded.messages == original.messages
    assert loaded.summary == original.summary
    assert loaded.archived_turns == original.archived_turns
    assert loaded.compaction_count == original.compaction_count
    assert loaded.last_input_tokens == original.last_input_tokens
    assert loaded.last_output_tokens == original.last_output_tokens


def test_save_persists_the_refreshed_updated_at(tmp_path):
    store = SessionStore(base_dir=tmp_path)
    session = _sample_session()

    store.save(session)
    loaded = store.load("test-session")

    assert session.updated_at  # save() populated it
    assert loaded.updated_at == session.updated_at


def test_load_missing_session_returns_none(tmp_path):
    store = SessionStore(base_dir=tmp_path)

    assert store.load("does-not-exist") is None


def test_rejects_unsafe_session_id(tmp_path):
    store = SessionStore(base_dir=tmp_path)

    with pytest.raises(ValueError):
        store.save(Session.new("../escape"))


def test_load_corrupt_json_raises_session_load_error_not_silently_none(tmp_path):
    store = SessionStore(base_dir=tmp_path)
    (tmp_path / "broken.json").write_text("{not valid json", encoding="utf-8")

    with pytest.raises(SessionLoadError):
        store.load("broken")


def test_load_unsupported_schema_version_raises_specific_error(tmp_path):
    store = SessionStore(base_dir=tmp_path)
    payload = {
        "schema_version": "999.0.0",
        "session_id": "future",
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "messages": [],
    }
    (tmp_path / "future.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(UnsupportedSessionSchemaError):
        store.load("future")


def test_load_missing_required_field_raises_rather_than_silently_defaulting(tmp_path):
    store = SessionStore(base_dir=tmp_path)
    # "role" is required on every message — a file missing it must not be
    # silently accepted with a made-up default.
    payload = {
        "schema_version": MEMORY_SCHEMA_VERSION,
        "session_id": "malformed",
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "messages": [{"content": "hi, no role field"}],
    }
    (tmp_path / "malformed.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SessionLoadError):
        store.load("malformed")


def test_save_never_leaves_a_temp_file_treated_as_a_session(tmp_path):
    store = SessionStore(base_dir=tmp_path)

    store.save(Session.new("s1"))

    files = sorted(p.name for p in tmp_path.iterdir())
    assert files == ["s1.json"]  # no leftover .tmp-* file
    assert store.load("s1") is not None


def test_save_unicode_and_emoji_content_round_trips_exactly(tmp_path):
    store = SessionStore(base_dir=tmp_path)
    session = Session.new("s1")
    session.messages = [
        {"role": "user", "content": "こんにちは、元気ですか？ 🐱 café naïve"},
        {"role": "assistant", "content": "Здравствуйте! 😺 — नमस्ते"},
    ]
    session.summary = "User greeted in Japanese and mentioned cats 🐱."

    store.save(session)
    loaded = store.load("s1")

    assert loaded.messages == session.messages
    assert loaded.summary == session.summary


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX permission bits aren't meaningful on Windows")
def test_save_restricts_file_permissions_to_owner_on_posix(tmp_path):
    store = SessionStore(base_dir=tmp_path)

    store.save(Session.new("s1"))

    mode = (tmp_path / "s1.json").stat().st_mode
    assert stat.S_IMODE(mode) == stat.S_IRUSR | stat.S_IWUSR

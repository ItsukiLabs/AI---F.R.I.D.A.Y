import pytest

from backend.memory.session import Session
from backend.memory.store import SessionStore


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

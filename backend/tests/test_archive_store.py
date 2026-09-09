import json
import sqlite3
import stat
import sys

import pytest

from backend.memory.archive_errors import (
    ArchiveLoadError,
    ArchiveSaveError,
    UnsupportedArchiveSchemaError,
)
from backend.memory.archive_store import ArchiveStore, _render_text
from backend.memory.session import Session


def _session(session_id: str, texts: list[str], created_at: str | None = None) -> Session:
    """Alternating user/assistant plain-text turns."""
    session = Session.new(session_id)
    if created_at is not None:
        session.created_at = created_at
    for i, text in enumerate(texts):
        session.messages.append({"role": "user" if i % 2 == 0 else "assistant", "content": text})
    return session


def _raw(store: ArchiveStore, sql: str, params=()):
    conn = sqlite3.connect(str(store.db_path))
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


# --- ingest --------------------------------------------------------------


def test_ingest_then_search_round_trips_hit_fields(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    session = _session("s1", ["aku alergi kacang tanah", "Baik, dicatat."])

    assert store.ingest(session) == 2

    hits = store.search("kacang")
    assert len(hits) == 1
    hit = hits[0]
    assert hit.session_id == "s1"
    assert hit.ordinal == 0
    assert hit.role == "user"
    assert hit.text == "aku alergi kacang tanah"
    assert hit.session_started_at == session.created_at
    assert hit.indexed_at


def test_content_json_is_verbatim_for_block_content(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    content = [
        {"type": "text", "text": "Let me check."},
        {"type": "tool_use", "id": "call_1", "name": "get_current_time", "input": {"tz": "UTC"}},
    ]
    session = Session.new("s1")
    session.messages.append({"role": "user", "content": "what time is it"})
    session.messages.append({"role": "assistant", "content": content})
    store.ingest(session)

    rows = _raw(store, "SELECT content_json FROM turns WHERE ordinal = 1")
    assert json.loads(rows[0][0]) == content


def test_block_content_is_searchable_by_tool_name_and_tool_result_text(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    session = Session.new("s1")
    session.messages.append({"role": "user", "content": "what time is it"})
    session.messages.append(
        {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "id": "c1", "name": "get_current_time", "input": {}},
            ],
        }
    )
    session.messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "c1",
                    "content": "2026-09-09T10:00:00 Asia/Jakarta",
                    "is_error": False,
                }
            ],
        }
    )
    store.ingest(session)

    assert [h.ordinal for h in store.search("get_current_time")] == [1]
    assert [h.ordinal for h in store.search("Jakarta")] == [2]


def test_render_text_labels_tool_blocks():
    assert _render_text("plain") == "plain"
    rendered = _render_text(
        [
            {"type": "text", "text": "hi"},
            {"type": "tool_use", "id": "c", "name": "add", "input": {"a": 1}},
            {"type": "tool_result", "tool_use_id": "c", "content": "boom", "is_error": True},
        ]
    )
    assert rendered.splitlines() == ["hi", '[tool_use add] {"a": 1}', "[tool_result: error] boom"]


def test_ingest_is_idempotent(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    session = _session("s1", ["satu", "dua"])

    assert store.ingest(session) == 2
    assert store.ingest(session) == 0
    assert store.count_turns() == 2


def test_ingest_is_incremental_with_continuous_ordinals(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    session = _session("s1", ["satu", "dua"])
    store.ingest(session)

    session.messages.append({"role": "user", "content": "tiga"})
    session.messages.append({"role": "assistant", "content": "empat"})
    assert store.ingest(session) == 2

    rows = _raw(store, "SELECT ordinal, text FROM turns ORDER BY ordinal")
    assert rows == [(0, "satu"), (1, "dua"), (2, "tiga"), (3, "empat")]


def test_ingest_after_compaction_does_not_duplicate(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    session = _session("s1", ["satu", "dua", "tiga", "empat"])
    store.ingest(session)

    # exactly what compact() does: move the oldest turns out of the live window
    session.archived_turns.extend(session.messages[:2])
    session.messages = session.messages[2:]
    session.messages.append({"role": "user", "content": "lima"})
    session.messages.append({"role": "assistant", "content": "enam"})

    assert store.ingest(session) == 2
    rows = _raw(store, "SELECT ordinal, text FROM turns ORDER BY ordinal")
    assert rows == [
        (0, "satu"),
        (1, "dua"),
        (2, "tiga"),
        (3, "empat"),
        (4, "lima"),
        (5, "enam"),
    ]


def test_pre_m2b_session_is_fully_backfilled_on_first_ingest(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    session = _session("old", ["a", "b", "c"])
    session.archived_turns = session.messages[:2]
    session.messages = session.messages[2:]

    assert store.ingest(session) == 3
    assert store.count_turns("old") == 3


def test_recreated_session_with_same_id_gets_its_own_generation(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    first = _session("s1", ["percakapan lama", "ok"], created_at="2026-01-01T00:00:00+00:00")
    store.ingest(first)

    second = _session("s1", ["percakapan baru"], created_at="2026-02-01T00:00:00+00:00")
    assert store.ingest(second) == 1  # no IntegrityError on (s1, ordinal 0)

    assert store.count_turns("s1") == 3
    assert {h.text for h in store.search("percakapan")} == {"percakapan lama", "percakapan baru"}


def test_history_shorter_than_ingested_count_raises_archive_save_error(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    session = _session("s1", ["satu", "dua", "tiga"])
    store.ingest(session)

    session.messages = session.messages[:1]  # only possible via manual file edit
    with pytest.raises(ArchiveSaveError):
        store.ingest(session)
    assert store.count_turns("s1") == 3  # nothing was renumbered or dropped


# --- search --------------------------------------------------------------


def test_search_matches_indonesian_and_english_case_insensitively(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    store.ingest(_session("s1", ["Aku punya KUCING bernama Mochi", "I also have a Dog"]))

    assert [h.ordinal for h in store.search("kucing")] == [0]
    assert [h.ordinal for h in store.search("DOG")] == [1]


def test_search_folds_diacritics(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    store.ingest(_session("s1", ["aku suka café di bandung"]))

    assert len(store.search("cafe")) == 1


def test_search_prefers_all_terms_then_falls_back_to_any_term(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    store.ingest(_session("s1", ["aku alergi kacang tanah", "kucing peliharaan"]))

    assert [h.ordinal for h in store.search("alergi kacang")] == [0]  # AND satisfied
    assert {h.ordinal for h in store.search("kacang kucing")} == {0, 1}  # AND empty → OR


def test_search_sanitizes_fts_syntax(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    store.ingest(_session("s1", ["aku alergi kacang tanah"]))

    hits = store.search('kacang "AND" (x) -y *')
    assert [h.ordinal for h in hits] == [0]


@pytest.mark.parametrize("query", ["", "   ", "___ *** ((", '"'])
def test_search_with_no_word_tokens_returns_empty(tmp_path, query):
    store = ArchiveStore(base_dir=tmp_path)
    store.ingest(_session("s1", ["apa saja"]))

    assert store.search(query) == []


def test_search_respects_limit(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    store.ingest(_session("s1", [f"kacang nomor {i}" for i in range(6)]))

    assert len(store.search("kacang", limit=2)) == 2
    assert len(store.search("kacang", limit=10)) == 6


def test_search_exclude_hides_live_window_but_keeps_archived_turns(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    session = _session("s1", ["rahasia lama", "ok", "rahasia baru", "ok"])
    session.archived_turns = session.messages[:2]
    session.messages = session.messages[2:]
    store.ingest(session)

    exclude = ("s1", len(session.archived_turns))
    assert [h.ordinal for h in store.search("rahasia", exclude=exclude)] == [0]
    assert {h.ordinal for h in store.search("rahasia")} == {0, 2}


# --- fail loud -----------------------------------------------------------


def test_unsupported_schema_version_raises_specific_error(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    store.ingest(_session("s1", ["x"]))

    conn = sqlite3.connect(str(store.db_path))
    with conn:
        conn.execute("UPDATE meta SET value = '999.0.0' WHERE key = 'schema_version'")
    conn.close()

    with pytest.raises(UnsupportedArchiveSchemaError):
        store.search("x")
    with pytest.raises(ArchiveLoadError):  # it's also a load error
        store.ingest(_session("s2", ["y"]))


def test_corrupt_db_file_raises_archive_load_error_not_silently_empty(tmp_path):
    (tmp_path / "memory.db").write_bytes(b"not a database, definitely not")
    store = ArchiveStore(base_dir=tmp_path)

    with pytest.raises(ArchiveLoadError):
        store.search("apa")
    with pytest.raises(ArchiveLoadError):
        store.ingest(_session("s1", ["x"]))


def test_sqlite_file_without_meta_table_raises_archive_load_error(tmp_path):
    conn = sqlite3.connect(str(tmp_path / "memory.db"))
    with conn:
        conn.execute("CREATE TABLE something_else (x TEXT)")
    conn.close()

    with pytest.raises(ArchiveLoadError):
        ArchiveStore(base_dir=tmp_path).search("apa")


def test_missing_db_is_created_on_first_use(tmp_path):
    store = ArchiveStore(base_dir=tmp_path / "nested" / "dir")
    assert not store.db_path.exists()

    assert store.search("apa") == []
    assert store.db_path.exists()
    assert _raw(store, "SELECT value FROM meta WHERE key = 'schema_version'") == [("1.0.0",)]


@pytest.mark.skipif(sys.platform == "win32", reason="chmod is a no-op for access control on Windows")
def test_db_permissions_restricted_on_posix(tmp_path):
    store = ArchiveStore(base_dir=tmp_path)
    store.ingest(_session("s1", ["x"]))

    assert stat.S_IMODE(store.db_path.stat().st_mode) == 0o600

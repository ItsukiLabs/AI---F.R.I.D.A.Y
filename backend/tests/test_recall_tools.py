from backend.agent_core.tools.recall_tools import (
    RECALL_MAX_LIMIT,
    RECALL_MAX_TEXT_CHARS,
    RECALL_MEMORY_CONTRACT,
    make_recall_tools,
)
from backend.memory.archive_store import ArchiveStore
from backend.memory.session import Session
from backend.schemas import PermissionTier


def _session(session_id: str, texts: list[str]) -> Session:
    session = Session.new(session_id)
    for i, text in enumerate(texts):
        session.messages.append({"role": "user" if i % 2 == 0 else "assistant", "content": text})
    return session


def _recall_fn(archive: ArchiveStore, current_session: Session | None = None):
    tools = make_recall_tools(archive, current_session=current_session)
    assert [contract.name for contract, _ in tools] == ["recall_memory"]
    return tools[0][1]


def test_contract_is_read_only_and_validates():
    contract = RECALL_MEMORY_CONTRACT
    assert contract.name == "recall_memory"
    assert contract.permission_tier == PermissionTier.READ_ONLY
    assert contract.annotations.read_only_hint is True
    assert contract.annotations.destructive_hint is False
    assert contract.annotations.idempotent_hint is True
    assert contract.input_schema["required"] == ["query"]
    assert contract.input_schema["additionalProperties"] is False
    assert contract.input_schema["properties"]["limit"]["maximum"] == RECALL_MAX_LIMIT


def test_recall_returns_hits_with_count(tmp_path):
    archive = ArchiveStore(base_dir=tmp_path)
    archive.ingest(_session("s-old", ["aku alergi kacang tanah", "Dicatat."]))
    recall = _recall_fn(archive)

    result = recall(query="alergi kacang")

    assert result["query"] == "alergi kacang"
    assert result["count"] == 1
    hit = result["hits"][0]
    assert hit["session_id"] == "s-old"
    assert hit["ordinal"] == 0
    assert hit["role"] == "user"
    assert hit["text"] == "aku alergi kacang tanah"
    assert hit["truncated"] is False
    assert hit["session_started_at"] and hit["indexed_at"]
    assert "note" not in result


def test_recall_no_match_shape(tmp_path):
    archive = ArchiveStore(base_dir=tmp_path)
    archive.ingest(_session("s-old", ["sesuatu yang lain"]))

    result = _recall_fn(archive)(query="zebra")

    assert result == {
        "query": "zebra",
        "count": 0,
        "hits": [],
        "note": "No past conversation turns matched. Try fewer or different keywords.",
    }


def test_recall_uses_config_default_limit_when_omitted(tmp_path, monkeypatch):
    monkeypatch.setenv("MEMORY_RECALL_DEFAULT_LIMIT", "1")
    archive = ArchiveStore(base_dir=tmp_path)
    archive.ingest(_session("s-old", ["kacang satu", "kacang dua", "kacang tiga"]))

    assert _recall_fn(archive)(query="kacang")["count"] == 1
    assert _recall_fn(archive)(query="kacang", limit=3)["count"] == 3


def test_recall_caps_limit_at_max(tmp_path):
    archive = ArchiveStore(base_dir=tmp_path)
    archive.ingest(_session("s-old", [f"kacang {i}" for i in range(RECALL_MAX_LIMIT + 5)]))

    assert _recall_fn(archive)(query="kacang", limit=999)["count"] == RECALL_MAX_LIMIT


def test_recall_truncates_long_text_and_flags_it(tmp_path):
    archive = ArchiveStore(base_dir=tmp_path)
    long_text = "kacang " + ("x" * (RECALL_MAX_TEXT_CHARS + 200))
    archive.ingest(_session("s-old", [long_text]))

    hit = _recall_fn(archive)(query="kacang")["hits"][0]

    assert hit["truncated"] is True
    assert hit["text"].endswith(" …")
    assert len(hit["text"]) == RECALL_MAX_TEXT_CHARS + 2


def test_recall_reads_current_session_cutoff_lazily(tmp_path):
    archive = ArchiveStore(base_dir=tmp_path)
    session = _session("live", ["kata rahasia", "ok"])
    archive.ingest(session)
    recall = _recall_fn(archive, current_session=session)  # built BEFORE compaction

    # both turns are still in the live window → hidden
    assert recall(query="rahasia")["count"] == 0

    # simulate compact(): the turns leave the live window
    session.archived_turns.extend(session.messages)
    session.messages = []

    assert recall(query="rahasia")["count"] == 1


def test_recall_without_current_session_excludes_nothing(tmp_path):
    archive = ArchiveStore(base_dir=tmp_path)
    archive.ingest(_session("live", ["kata rahasia"]))

    assert _recall_fn(archive)(query="rahasia")["count"] == 1

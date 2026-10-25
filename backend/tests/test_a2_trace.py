"""M2 v2 A2 trace: what the stores and the home say after a turn that fails part-way.

These started (2026-09-17) as *characterization* tests of the behavior
before A2 was decided. A2 was decided on 2026-10-23 and the scenarios it
changes (S3, S4, S6, S7, S8) now assert the new behavior; S5 is the known
gap left for the M11 action/audit log. The scenario table lives in Memory Think/M2_memory.md
("M2 v2 A2: trace konkret").

Every scenario uses the mock home (one lamp, off) and real on-disk stores
under ``tmp_path``. "World" = the home; "session" / "profile" / "archive"
= what a fresh load from disk returns after the turn.
"""

import pytest

from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.devices import FailureMode, MockHomeAdapter, default_home
from backend.memory.archive_store import ArchiveStore
from backend.memory.profile_store import ProfileStore
from backend.memory.store import SessionStore
from backend.orchestrator import Orchestrator
from backend.registry import ToolCatalog

LAMP = "lampu_ruang_tamu"


class ApiDown(RuntimeError):
    pass


class FakeLLMClient:
    """Scripted responses; an Exception instance in the script is raised instead."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def send(self, messages, tools, system):
        self.calls.append({"messages": [dict(m) for m in messages], "system": system})
        response = self._responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


def _calls(*calls):
    return LLMResponse(
        text=None,
        tool_calls=[ToolCallRequest(id=i, name=n, arguments=a) for i, n, a in calls],
        stop_reason="tool_use",
    )


def _lamp_on(call_id="c1"):
    return _calls((call_id, "home_set_power", {"device_id": LAMP, "on": True}))


def _text(text):
    return LLMResponse(text=text, tool_calls=[])


class FailingSessionStore(SessionStore):
    def save(self, session):
        raise OSError("disk full")


class FailingProfileStore(ProfileStore):
    def save(self, profile):
        raise OSError("disk full")


class FailingArchiveStore(ArchiveStore):
    def ingest(self, session):
        raise OSError("database is locked")


class World:
    def __init__(self, tmp_path, llm, *, session_store=None, profile_store=None,
                 archive_store=None, max_iterations=6):
        self.home = default_home()
        catalog = ToolCatalog()
        MockHomeAdapter(self.home).sync_into(catalog, pinned=True)
        self.session_store = session_store or SessionStore(base_dir=tmp_path / "sessions")
        self.profile_store = profile_store or ProfileStore(base_dir=tmp_path / "profile")
        self.archive_store = archive_store or ArchiveStore(base_dir=tmp_path / "archive")
        self.tmp_path = tmp_path
        self.orch = Orchestrator(
            llm,
            catalog=catalog,
            session_store=self.session_store,
            profile_store=self.profile_store,
            archive_store=self.archive_store,
            max_iterations=max_iterations,
        )

    def lamp_on(self):
        return self.home.snapshot()[LAMP]["on"]

    def saved_messages(self):
        session = SessionStore(base_dir=self.tmp_path / "sessions").load("s1")
        return None if session is None else session.messages

    def saved_facts(self):
        profile = ProfileStore(base_dir=self.tmp_path / "profile").load()
        return [] if profile is None else [f.text for f in profile.active_facts()]

    def archived_turns(self):
        return ArchiveStore(base_dir=self.tmp_path / "archive").count_turns("s1")


def _tool_results(messages):
    return [
        block
        for m in messages
        if m["role"] == "user" and isinstance(m["content"], list)
        for block in m["content"]
        if block.get("type") == "tool_result"
    ]


# S1 -------------------------------------------------------------------------


def test_s1_happy_path_everything_agrees(tmp_path):
    w = World(tmp_path, FakeLLMClient([_lamp_on(), _text("Lampu sudah nyala.")]))

    w.orch.run_turn("nyalakan lampu", "s1")

    assert w.lamp_on() is True
    assert w.saved_messages()[-1]["content"][0]["text"] == "Lampu sudah nyala."
    assert w.archived_turns() >= 1


# S2 -------------------------------------------------------------------------


def test_s2_device_offline_is_an_observation_and_everything_agrees(tmp_path):
    w = World(tmp_path, FakeLLMClient([_lamp_on(), _text("Maaf, lampunya tidak merespons.")]))
    w.home.fail_next(LAMP, FailureMode.OFFLINE)

    w.orch.run_turn("nyalakan lampu", "s1")

    assert w.lamp_on() is False
    [result] = _tool_results(w.saved_messages())
    assert result["is_error"] is True and "offline" in result["content"]


# S3 -------------------------------------------------------------------------


def test_s3_lost_ack_is_resolved_by_reading_the_state_back(tmp_path):
    """A2 (c): the adapter reads the lamp back, so the tool result tells the truth."""
    llm = FakeLLMClient([_lamp_on(), _text("Lampu sudah nyala.")])
    w = World(tmp_path, llm)
    w.home.fail_next(LAMP, FailureMode.LOST_ACK)

    w.orch.run_turn("nyalakan lampu", "s1")

    assert w.lamp_on() is True
    [result] = _tool_results(w.saved_messages())
    assert result["is_error"] is False
    assert "did not confirm" in result["content"] and "took effect" in result["content"]
    assert '"on": true' in result["content"]


def test_s3_offline_error_carries_the_actual_state(tmp_path):
    llm = FakeLLMClient([_lamp_on(), _text("Maaf, lampunya tidak merespons.")])
    w = World(tmp_path, llm)
    w.home.fail_next(LAMP, FailureMode.OFFLINE)

    w.orch.run_turn("nyalakan lampu", "s1")

    [result] = _tool_results(w.saved_messages())
    assert result["is_error"] is True
    assert "offline" in result["content"] and "Actual state read back" in result["content"]


def test_s3_system_prompt_tells_the_model_to_check_state_not_history(tmp_path):
    llm = FakeLLMClient([_text("Halo!")])
    w = World(tmp_path, llm)

    w.orch.run_turn("halo", "s1")

    assert "read it with a tool instead of answering from" in llm.calls[0]["system"]


# S4 -------------------------------------------------------------------------


def test_s4_llm_fails_after_the_device_acted_turn_is_kept_with_a_marker(tmp_path):
    """A2 (a): the partial turn is saved, marked interrupted, and the error still propagates."""
    llm = FakeLLMClient([_lamp_on(), ApiDown("503"), _text("Halo!")])
    w = World(tmp_path, llm)

    with pytest.raises(ApiDown):
        w.orch.run_turn("nyalakan lampu", "s1")

    assert w.lamp_on() is True
    saved = w.saved_messages()
    assert [m["role"] for m in saved] == ["user", "assistant", "user", "assistant"]
    assert "Turn interrupted" in saved[-1]["content"][0]["text"]
    assert "ApiDown" in saved[-1]["content"][0]["text"]
    assert w.archived_turns() >= 1

    w.orch.run_turn("halo", "s1")
    next_turn_history = llm.calls[-1]["messages"]
    assert [m["role"] for m in next_turn_history] == [
        "user", "assistant", "user", "assistant", "user"
    ]


def test_s4_failure_on_the_first_call_still_records_the_question(tmp_path):
    llm = FakeLLMClient([ApiDown("503")])
    w = World(tmp_path, llm)

    with pytest.raises(ApiDown):
        w.orch.run_turn("nyalakan lampu", "s1")

    assert [m["role"] for m in w.saved_messages()] == ["user", "assistant"]


def test_s4_save_failure_while_keeping_the_partial_turn_does_not_mask_the_cause(tmp_path):
    llm = FakeLLMClient([_lamp_on(), ApiDown("503")])
    w = World(tmp_path, llm, session_store=FailingSessionStore(base_dir=tmp_path / "sessions"))

    with pytest.raises(ApiDown) as info:
        w.orch.run_turn("nyalakan lampu", "s1")

    assert any("disk full" in note for note in info.value.__notes__)


# S5 -------------------------------------------------------------------------


def test_s5_session_save_fails_after_the_device_acted(tmp_path):
    """KNOWN GAP until the M11 action/audit log (A2 decision 3): lamp on, no session record.

    The caller gets the exception, not the model's "Lampu sudah nyala.", and
    A2 (c) means a later "is the lamp on?" is answered from the device, not
    from history.
    """
    llm = FakeLLMClient([_lamp_on(), _text("Lampu sudah nyala.")])
    w = World(tmp_path, llm, session_store=FailingSessionStore(base_dir=tmp_path / "sessions"))

    with pytest.raises(OSError, match="disk full"):
        w.orch.run_turn("nyalakan lampu", "s1")

    assert w.lamp_on() is True
    assert w.saved_messages() is None
    assert w.archived_turns() == 0


# S6 -------------------------------------------------------------------------


def _remember_script():
    return [
        _calls(("c1", "remember_user_fact",
                {"fact": "Aku suka lampu redup", "category": "preference", "supersedes": None})),
        _text("Siap, saya ingat."),
    ]


def test_s6_profile_save_fails_session_is_kept_with_a_correction(tmp_path):
    """A2: no false "I'll remember" survives; the claim is corrected in the same assistant turn."""
    w = World(tmp_path, FakeLLMClient(_remember_script()),
              profile_store=FailingProfileStore(base_dir=tmp_path / "profile"))

    with pytest.raises(OSError, match="disk full"):
        w.orch.run_turn("inget ya, aku suka lampu redup", "s1")

    assert w.saved_facts() == []
    saved = w.saved_messages()
    assert [m["role"] for m in saved] == ["user", "assistant", "user", "assistant"]
    reply = [block["text"] for block in saved[-1]["content"]]
    assert reply[0] == "Siap, saya ingat."
    assert "NOT saved" in reply[1]
    assert w.archived_turns() == 0  # skipped; catches up on the next turn


def test_s6_profile_failure_does_not_lose_a_device_action_in_the_same_turn(tmp_path):
    llm = FakeLLMClient(
        [
            _calls(
                ("c1", "home_set_power", {"device_id": LAMP, "on": True}),
                ("c2", "remember_user_fact",
                 {"fact": "Aku suka lampu redup", "category": "preference", "supersedes": None}),
            ),
            _text("Lampu nyala, dan saya ingat."),
        ]
    )
    w = World(tmp_path, llm, profile_store=FailingProfileStore(base_dir=tmp_path / "profile"))

    with pytest.raises(OSError, match="disk full"):
        w.orch.run_turn("nyalakan lampu, dan inget aku suka lampu redup", "s1")

    assert w.lamp_on() is True
    results = _tool_results(w.saved_messages())
    assert [r["is_error"] for r in results] == [False, False]
    assert '"on": true' in results[0]["content"]


def test_s6_interrupted_turn_with_profile_failure_keeps_both_notes(tmp_path):
    llm = FakeLLMClient(
        [
            _calls(("c1", "remember_user_fact",
                    {"fact": "Aku suka lampu redup", "category": "preference", "supersedes": None})),
            ApiDown("503"),
        ]
    )
    w = World(tmp_path, llm, profile_store=FailingProfileStore(base_dir=tmp_path / "profile"))

    with pytest.raises(ApiDown) as info:
        w.orch.run_turn("inget ya, aku suka lampu redup", "s1")

    assert any("disk full" in note for note in info.value.__notes__)
    texts = [block["text"] for block in w.saved_messages()[-1]["content"]]
    assert "Turn interrupted" in texts[0] and "NOT saved" in texts[1]


def test_s6_session_save_fails_after_profile_saved_the_fact_is_kept(tmp_path):
    """The other half of the new order: a true fact without its conversation is harmless."""
    w = World(tmp_path, FakeLLMClient(_remember_script()),
              session_store=FailingSessionStore(base_dir=tmp_path / "sessions"))

    with pytest.raises(OSError, match="disk full"):
        w.orch.run_turn("inget ya, aku suka lampu redup", "s1")

    assert w.saved_facts() == ["Aku suka lampu redup"]
    assert w.saved_messages() is None


# S7 -------------------------------------------------------------------------


class FlakyArchiveStore(ArchiveStore):
    """Fails the first ingest only."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.failed = False

    def ingest(self, session):
        if not self.failed:
            self.failed = True
            raise OSError("database is locked")
        return super().ingest(session)


def test_s7_archive_failure_is_a_warning_not_an_error(tmp_path):
    """A2 decision 4: the reply is returned, the failure is reported, the archive self-heals."""
    llm = FakeLLMClient([_lamp_on(), _text("Lampu sudah nyala."), _text("Halo!")])
    w = World(tmp_path, llm, archive_store=FlakyArchiveStore(base_dir=tmp_path / "archive"))

    result = w.orch.run_turn("nyalakan lampu", "s1")

    assert result.text == "Lampu sudah nyala."
    assert len(result.warnings) == 1 and "locked" in result.warnings[0]
    assert w.saved_messages()[-1]["content"][0]["text"] == "Lampu sudah nyala."
    assert w.archived_turns() == 0

    second = w.orch.run_turn("halo", "s1")
    assert second.warnings == []
    assert w.archived_turns() == len(w.saved_messages())  # turn 1 backfilled + turn 2


# S8 -------------------------------------------------------------------------


def test_s8_max_iterations_reply_is_saved(tmp_path):
    """A2 (a): the 'couldn't finish' reply the user saw is stored, roles keep alternating."""
    llm = FakeLLMClient(
        [
            _lamp_on("c1"),
            _calls(("c2", "home_get_state", {"device_id": LAMP})),
            _text("Halo!"),
        ]
    )
    w = World(tmp_path, llm, max_iterations=2)

    result = w.orch.run_turn("nyalakan lampu lalu cek", "s1")
    w.orch.run_turn("halo", "s1")

    assert result.exceeded_max_iterations is True
    assert w.lamp_on() is True
    history = llm.calls[-1]["messages"]
    roles = [m["role"] for m in history]
    assert all(a != b for a, b in zip(roles, roles[1:]))
    assert "wasn't able to finish" in history[-2]["content"][0]["text"]


# S9 -------------------------------------------------------------------------


def test_s9_partial_success_within_one_step_is_recorded_per_call(tmp_path):
    llm = FakeLLMClient(
        [
            _calls(
                ("c1", "home_set_power", {"device_id": LAMP, "on": True}),
                ("c2", "home_set_power", {"device_id": "ac_kamar", "on": True}),
            ),
            _text("Lampu nyala, tapi AC tidak merespons."),
        ]
    )
    w = World(tmp_path, llm)
    w.home.fail_next("ac_kamar", FailureMode.OFFLINE)

    w.orch.run_turn("nyalakan lampu dan AC", "s1")

    assert w.home.snapshot() == {
        LAMP: {"on": True, "brightness": 100},
        "ac_kamar": {"on": False, "target_temperature": 24, "current_temperature": 29.0},
    }
    assert [r["is_error"] for r in _tool_results(w.saved_messages())] == [False, True]


# Compaction ---------------------------------------------------------------
#
# Compaction runs before the user message is appended. A failure there must
# not add an "interrupted" note to the previous, complete turn; a failure
# after a successful compaction must still be marked.


def _big(text):
    return LLMResponse(text=text, tool_calls=[], input_tokens=500)


@pytest.fixture
def compact_early(monkeypatch):
    monkeypatch.setenv("MEMORY_COMPACTION_THRESHOLD_TOKENS", "100")
    monkeypatch.setenv("MEMORY_COMPACTION_SAFETY_MARGIN_TOKENS", "0")
    monkeypatch.setenv("MEMORY_KEEP_RECENT_MESSAGES", "2")


def test_compaction_failure_saves_nothing_and_adds_no_marker(tmp_path, compact_early):
    llm = FakeLLMClient([_big("Satu."), _big("Dua."), ApiDown("503")])
    w = World(tmp_path, llm)
    w.orch.run_turn("satu", "s1")
    w.orch.run_turn("dua", "s1")
    before = w.saved_messages()

    with pytest.raises(ApiDown):
        w.orch.run_turn("tiga", "s1")

    assert len(llm.calls) == 3  # the third call was the summarization request
    assert w.saved_messages() == before
    assert all("Turn interrupted" not in str(m["content"]) for m in before)


def test_failure_after_successful_compaction_is_still_marked(tmp_path, compact_early):
    llm = FakeLLMClient([_big("Satu."), _big("Dua."), _text("ringkasan"), ApiDown("503")])
    w = World(tmp_path, llm)
    w.orch.run_turn("satu", "s1")
    w.orch.run_turn("dua", "s1")

    with pytest.raises(ApiDown):
        w.orch.run_turn("tiga", "s1")

    saved = w.saved_messages()
    assert [m["role"] for m in saved] == ["user", "assistant", "user", "assistant"]
    assert saved[0]["content"] == "dua"  # "satu" was folded into the summary
    assert saved[2]["content"] == "tiga"
    assert "Turn interrupted" in saved[-1]["content"][0]["text"]
    session = SessionStore(base_dir=tmp_path / "sessions").load("s1")
    assert session.summary == "ringkasan"

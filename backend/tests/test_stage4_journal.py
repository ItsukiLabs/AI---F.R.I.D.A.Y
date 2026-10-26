"""Sprint 4 stage 4: the action journal, pending timeout, and the CLI around them.

The journal closes S5: a device command is written down *before* the device
is touched and its outcome after, so a failed session save (or a crash) can
no longer erase the trace of a lamp that moved.
"""

import sqlite3
import stat
import sys

import pytest

from backend.agent_core.config import DEFAULT_PERMISSIONS_FILE
from backend.agent_core.llm_client import LLMResponse, ToolCallRequest
from backend.cli import Cli, build_orchestrator
from backend.devices import DeviceError, DeviceService, FailureMode, default_home
from backend.journal import ActionContext, ActionJournal, JournalError, current_action
from backend.memory.archive_store import ArchiveStore
from backend.memory.profile_store import ProfileStore
from backend.memory.store import SessionStore
from backend.schemas.device_contract import CommandStatus
from backend.security import PermissionGate, load_permission_policy

LAMP = "lampu_ruang_tamu"
AC = "ac_kamar"


class FakeLLMClient:
    def __init__(self, responses):
        self._responses = list(responses)

    def send(self, messages, tools, system):
        return self._responses.pop(0)


def _call(name, arguments):
    return LLMResponse(
        text=None,
        tool_calls=[ToolCallRequest(id="c1", name=name, arguments=arguments)],
        stop_reason="tool_use",
    )


def _text(text):
    return LLMResponse(text=text, tool_calls=[])


class Ticker:
    """A monotonic clock the test moves by hand."""

    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


@pytest.fixture
def journal(tmp_path):
    return ActionJournal(tmp_path / "journal" / "actions.db")


# -- the journal on its own --------------------------------------------------


def test_successful_command_is_prepared_then_succeeded(journal):
    service = DeviceService(default_home(), journal=journal)
    token = current_action.set(ActionContext("home_set_power", "s1", "auto"))
    try:
        outcome = service.apply(LAMP, {"on": True})
    finally:
        current_action.reset(token)

    entry = journal.get(outcome.operation_id)
    assert entry.status == "succeeded"
    assert entry.device_id == LAMP and entry.requested == {"on": True}
    assert entry.reported["on"] is True
    assert (entry.tool_name, entry.session_id, entry.approval) == ("home_set_power", "s1", "auto")


def test_failed_outcome_is_journaled(journal):
    home = default_home()
    service = DeviceService(home, journal=journal)
    home.fail_next(LAMP, FailureMode.OFFLINE)
    failed = service.apply(LAMP, {"on": True})
    assert journal.get(failed.operation_id).status == "failed"


class BrokenPrepare(ActionJournal):
    def prepare(self, *args, **kwargs):
        raise JournalError("disk full")


def test_command_is_not_sent_when_it_cannot_be_journaled(tmp_path):
    home = default_home()
    service = DeviceService(home, journal=BrokenPrepare(tmp_path / "a.db"))

    with pytest.raises(DeviceError, match="not sent"):
        service.apply(LAMP, {"on": True})

    assert home.actions == [] and home.device(LAMP).state["on"] is False


class BrokenFinish(ActionJournal):
    def finish(self, *args, **kwargs):
        raise JournalError("disk full")


def test_outcome_write_failure_keeps_the_result_and_is_recovered_as_unknown(tmp_path):
    path = tmp_path / "a.db"
    service = DeviceService(default_home(), journal=BrokenFinish(path))

    outcome = service.apply(LAMP, {"on": True})

    assert outcome.status is CommandStatus.SUCCEEDED  # the lamp did turn on
    restarted = ActionJournal(path)
    assert restarted.get(outcome.operation_id).status == "prepared"
    [uncertain] = restarted.recover()
    assert uncertain.operation_id == outcome.operation_id and uncertain.status == "unknown"


def test_pending_command_is_journaled_and_settles(journal):
    home = default_home()
    home.make_slow(LAMP, 1)
    service = DeviceService(home, journal=journal)

    outcome = service.apply(LAMP, {"on": True})
    assert journal.get(outcome.operation_id).status == "pending"

    service.read_state(LAMP)
    assert journal.get(outcome.operation_id).status == "succeeded"


def test_recover_marks_unsettled_entries_unknown_once_and_ack_clears_them(journal):
    journal.prepare("op1", LAMP, {"on": True})
    journal.prepare("op2", AC, {"on": True})
    journal.finish("op2", "pending")
    journal.prepare("op3", LAMP, {"on": False})
    journal.finish("op3", "succeeded", {"on": False})

    uncertain = journal.recover()

    assert [e.operation_id for e in uncertain] == ["op1", "op2"]
    assert all("stopped before the outcome was known" in e.message for e in uncertain)
    assert journal.get("op3").status == "succeeded"
    assert journal.mark_reviewed() == 2
    assert journal.recover() == []


def test_recent_is_newest_first(journal):
    for i in range(3):
        journal.prepare(f"op{i}", LAMP, {"on": True})
    assert [e.operation_id for e in journal.recent(2)] == ["op2", "op1"]


def test_finish_for_an_unknown_operation_raises(journal):
    with pytest.raises(JournalError):
        journal.finish("nope", "succeeded")


def test_foreign_database_is_rejected(tmp_path):
    path = tmp_path / "other.db"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE something (x)")
    with pytest.raises(JournalError, match="not an action journal"):
        ActionJournal(path)


def test_non_sqlite_file_is_rejected(tmp_path):
    path = tmp_path / "junk.db"
    path.write_bytes(b"this is not sqlite at all, just text" * 10)
    with pytest.raises(JournalError):
        ActionJournal(path)


# -- pending timeout ---------------------------------------------------------


def test_pending_command_becomes_unknown_after_the_timeout(journal):
    home = default_home()
    home.make_slow(LAMP, 5)
    ticker = Ticker()
    service = DeviceService(home, journal=journal, pending_timeout_seconds=60, monotonic=ticker)
    outcome = service.apply(LAMP, {"on": True})

    ticker.now += 59
    assert service.get_operation(outcome.operation_id).status is CommandStatus.PENDING

    ticker.now += 1
    expired = service.get_operation(outcome.operation_id)
    assert expired.status is CommandStatus.UNKNOWN and "60 s" in expired.message
    assert journal.get(outcome.operation_id).status == "unknown"
    assert service.read_state(LAMP).pending_operations == []


def test_without_a_timeout_pending_waits_as_before():
    home = default_home()
    home.make_slow(LAMP, 5)
    ticker = Ticker()
    service = DeviceService(home, monotonic=ticker)
    outcome = service.apply(LAMP, {"on": True})
    ticker.now += 10_000
    assert service.get_operation(outcome.operation_id).status is CommandStatus.PENDING


# -- through the orchestrator (S5) and the CLI -------------------------------


class FailingSessionStore(SessionStore):
    def save(self, session):
        raise OSError("disk full")


def _orch(tmp_path, home, journal, responses, session_store=None):
    return build_orchestrator(
        FakeLLMClient(responses),
        home,
        pin_home_tools=True,
        journal=journal,
        session_store=session_store or SessionStore(base_dir=tmp_path / "sessions"),
        profile_store=ProfileStore(base_dir=tmp_path / "profile"),
        archive_store=ArchiveStore(base_dir=tmp_path / "archive"),
        gate=PermissionGate(load_permission_policy(DEFAULT_PERMISSIONS_FILE)),
    )


def test_s5_device_action_survives_a_failed_session_save(tmp_path, journal):
    home = default_home()
    orch = _orch(
        tmp_path,
        home,
        journal,
        [_call("home_set_power", {"device_id": LAMP, "on": True}), _text("Sudah nyala.")],
        session_store=FailingSessionStore(base_dir=tmp_path / "sessions"),
    )

    with pytest.raises(OSError):
        orch.run_turn("nyalakan lampu", "s1")

    assert home.device(LAMP).state["on"] is True
    [entry] = journal.recent()
    assert entry.status == "succeeded" and entry.device_id == LAMP
    assert (entry.tool_name, entry.session_id, entry.approval) == ("home_set_power", "s1", "auto")


def _cli(tmp_path, home, journal, responses=()):
    out = []
    cli = Cli(_orch(tmp_path, home, journal, list(responses)), home, write=out.append, journal=journal)
    return cli, out


def test_cli_startup_lists_uncertain_commands_and_ack_clears_them(tmp_path, journal):
    journal.prepare("op1", LAMP, {"on": True})
    cli, out = _cli(tmp_path, default_home(), journal)

    cli.startup_report()
    assert "1 device command(s)" in out[0] and "not retried" in out[0]
    assert LAMP in out[1] and "unknown" in out[1]

    cli.handle("/journal ack")
    assert "1 uncertain" in out[-1]
    out.clear()
    cli.startup_report()
    assert out == []


def test_cli_journal_lists_recent_commands(tmp_path, journal):
    home = default_home()
    cli, out = _cli(
        tmp_path,
        home,
        journal,
        [_call("home_set_power", {"device_id": LAMP, "on": True}), _text("Sudah nyala.")],
    )
    cli.trace = False
    cli.handle("nyalakan lampu")
    out.clear()

    cli.handle("/journal")

    assert len(out) == 1
    assert LAMP in out[0] and "-> succeeded" in out[0] and "approved: auto" in out[0]


def test_cli_journal_when_empty_or_missing(tmp_path, journal):
    cli, out = _cli(tmp_path, default_home(), journal)
    cli.handle("/journal")
    assert out == ["the action journal is empty"]

    cli.journal = None
    cli.handle("/journal")
    assert out[-1] == "no action journal in this run"


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX permission bits aren't meaningful on Windows")
def test_journal_file_is_restricted_to_its_owner_on_posix(journal):
    assert stat.S_IMODE(journal.path.stat().st_mode) == stat.S_IRUSR | stat.S_IWUSR

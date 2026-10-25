"""Talk to F.R.I.D.A.Y in a terminal: ``python -m backend.cli``.

The first way to use F.R.I.D.A.Y outside the tests (Sprint 3). It wires the
real ``Orchestrator`` (all memory layers, the M4 catalog) to the real LLM
client and the M5 mock home, so every message costs API credits. The home
tools are *discoverable*, not pinned, so a conversation exercises
``find_tools``, auto-loading and tool retention the way production will.

The mock home lives in memory and starts with everything off on every run,
while the conversation is stored on disk. After a restart the history may
say "the lamp is on" while the lamp is off; the system prompt tells the
model to read device state rather than trust history (A2), so that mismatch
is a useful check rather than a bug.

Slash commands control the harness, never the model; see ``HELP``.
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime
from typing import Any, Callable

from backend.agent_core.llm_client import LLMClient, get_llm_client
from backend.agent_core.tool_registry import ToolRegistry
from backend.agent_core.tools.time_tool import TIME_TOOL_CONTRACT, get_current_time
from backend.devices import (
    DeviceError,
    FailureMode,
    MockHome,
    MockHomeAdapter,
    default_home,
    two_lamp_home,
)
from backend.memory.session import Session
from backend.memory.store import SessionStore
from backend.orchestrator import Orchestrator
from backend.registry import ToolCatalog

DEFAULT_SESSION_ID = "cli"

# --home choices: the standard home, or one with two lamps in the living room
# (to try "which lamp?" disambiguation).
HOMES: dict[str, Callable[[], MockHome]] = {"default": default_home, "dua-lampu": two_lamp_home}

HELP = """Commands:
  /state                         show the mock home's devices and state
  /fail <device_id> <mode>       next command to that device fails once
                                 (mode: offline | lost_ack)
  /slow <device_id> <reads>      commands to that device take effect only after
                                 <reads> later state reads (0 = normal again)
  /trace on|off                  show the tool calls of each turn (default on)
  /new                           start a new session
  /session                       show the current session id
  /help                          this text
  /quit                          exit
Anything else is sent to F.R.I.D.A.Y."""


def build_orchestrator(
    llm: LLMClient,
    home: MockHome,
    *,
    pin_home_tools: bool = False,
    **orchestrator_kwargs: Any,
) -> Orchestrator:
    """The production wiring: time tool always installed, home tools in the catalog."""
    registry = ToolRegistry()
    registry.register(TIME_TOOL_CONTRACT, get_current_time)
    catalog = ToolCatalog()
    MockHomeAdapter(home).sync_into(catalog, pinned=pin_home_tools)
    return Orchestrator(llm, registry=registry, catalog=catalog, **orchestrator_kwargs)


def _last_turn(session: Session | None) -> list[dict[str, Any]]:
    """Messages of the most recent turn: from the last plain user message on."""
    if session is None:
        return []
    messages = session.messages
    for i in range(len(messages) - 1, -1, -1):
        if messages[i]["role"] == "user" and isinstance(messages[i]["content"], str):
            return messages[i + 1 :]
    return []


def format_trace(turn: list[dict[str, Any]]) -> list[str]:
    """One line per tool call and per tool result of a turn."""
    lines = []
    for message in turn:
        if not isinstance(message["content"], list):
            continue
        for block in message["content"]:
            if block.get("type") == "tool_use":
                args = json.dumps(block.get("input", {}), ensure_ascii=False)
                lines.append(f"  -> {block['name']}({args})")
            elif block.get("type") == "tool_result":
                status = "error" if block.get("is_error") else "ok"
                content = str(block.get("content", ""))
                if len(content) > 160:
                    content = content[:157] + "..."
                lines.append(f"  <- [{status}] {content}")
    return lines


def format_state(home: MockHome) -> list[str]:
    rows = [
        f"  {d.device_id} ({d.name}, {d.room}): {json.dumps(d.state)}" for d in home.devices()
    ]
    for device_id, items in home.queued().items():
        for item in items:
            rows.append(
                f"  pending {device_id}: {json.dumps(item['changes'])} "
                f"(applies after {item['reads_left']} more read(s))"
            )
    return rows


class Cli:
    def __init__(
        self,
        orchestrator: Orchestrator,
        home: MockHome,
        session_id: str = DEFAULT_SESSION_ID,
        write: Callable[[str], None] = print,
    ) -> None:
        self.orch = orchestrator
        self.home = home
        self.session_id = session_id
        self.write = write
        self.trace = True

    def handle(self, line: str) -> bool:
        """Process one input line. Returns False when the CLI should exit."""
        line = line.strip()
        if not line:
            return True
        if line.startswith("/"):
            return self._command(line)
        self._turn(line)
        return True

    def _turn(self, text: str) -> None:
        try:
            result = self.orch.run_turn(text, self.session_id)
        except Exception as exc:  # keep the session alive; the turn was saved if it could be
            self._show_trace()
            self.write(f"[error] {type(exc).__name__}: {exc}")
            for note in getattr(exc, "__notes__", []):
                self.write(f"[error] {note}")
            return
        except KeyboardInterrupt as exc:
            self._show_trace()
            self.write("[interrupted] turn stopped; what happened so far was saved if it could be")
            for note in getattr(exc, "__notes__", []):
                self.write(f"[error] {note}")
            return
        self._show_trace()
        self.write(f"F.R.I.D.A.Y: {result.text}")
        if result.exceeded_max_iterations:
            self.write("[note] stopped at the step limit")
        for warning in result.warnings:
            self.write(f"[warning] {warning}")

    def _show_trace(self) -> None:
        if not self.trace:
            return
        session = self.orch.session_store.load(self.session_id)
        for line in format_trace(_last_turn(session)):
            self.write(line)

    def _command(self, line: str) -> bool:
        parts = line.split()
        name, args = parts[0].lower(), parts[1:]
        if name in ("/quit", "/exit"):
            return False
        if name == "/help":
            self.write(HELP)
        elif name == "/state":
            for row in format_state(self.home):
                self.write(row)
        elif name == "/fail":
            self._fail(args)
        elif name == "/slow":
            self._slow(args)
        elif name == "/trace" and args in (["on"], ["off"]):
            self.trace = args[0] == "on"
            self.write(f"trace {args[0]}")
        elif name == "/new":
            self.session_id = f"cli-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            self.write(f"new session: {self.session_id}")
        elif name == "/session":
            self.write(f"session: {self.session_id}")
        else:
            self.write(f"unknown command {line!r}; /help lists them")
        return True

    def _fail(self, args: list[str]) -> None:
        if len(args) != 2:
            self.write("usage: /fail <device_id> offline|lost_ack")
            return
        device_id, mode = args
        try:
            self.home.fail_next(device_id, FailureMode(mode.lower()))
        except ValueError:
            self.write(f"unknown mode {mode!r}; use offline or lost_ack")
            return
        except DeviceError as exc:
            self.write(f"{exc}; /state lists the device ids")
            return
        self.write(f"next command to {device_id} will fail: {mode.lower()}")

    def _slow(self, args: list[str]) -> None:
        if len(args) != 2 or not args[1].isdigit():
            self.write("usage: /slow <device_id> <reads>  (reads = 0 makes it normal again)")
            return
        device_id, reads = args[0], int(args[1])
        try:
            self.home.make_slow(device_id, reads)
        except DeviceError as exc:
            self.write(f"{exc}; /state lists the device ids")
            return
        if reads:
            self.write(f"{device_id} is slow: commands apply after {reads} later read(s)")
        else:
            self.write(f"{device_id} is normal again")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m backend.cli", description=__doc__.split("\n")[0])
    parser.add_argument("--session", default=DEFAULT_SESSION_ID, help="session id to continue")
    parser.add_argument("--pin-home", action="store_true", help="install home tools every turn")
    parser.add_argument(
        "--home", choices=sorted(HOMES), default="default", help="which mock home to start with"
    )
    parser.add_argument("--debug", action="store_true", help="show debug logging")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.ERROR)
    home = HOMES[args.home]()
    orchestrator = build_orchestrator(get_llm_client(), home, pin_home_tools=args.pin_home)
    cli = Cli(orchestrator, home, args.session)

    print(f"F.R.I.D.A.Y CLI - session '{cli.session_id}'. Mock home, real LLM (uses API credits).")
    print("/help for commands, /quit to exit.")
    while True:
        try:
            line = input("you> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not cli.handle(line):
            break


if __name__ == "__main__":
    main()

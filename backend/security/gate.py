"""The permission gate: the one place that decides whether a tool call may run.

``loop._execute_tool_call`` runs every call in this order: find the tool ->
validate its arguments -> **ask the gate** -> run it -> record the result.
The gate decides from the owner's settings (``permissions.py``), never from
what the tool or the model says about itself.

Confirmation (decided 2026-10-26): the model can only *propose* an action;
it never approves one. When a tool needs the owner's "yes", the gate asks a
``Confirmer`` directly, outside the conversation, so nothing the model
writes can pass for approval. A confirmer turns whatever the owner did into
``yes`` / ``no`` / ``unclear``:

- ``TerminalConfirmer`` (now): the owner types y/n in the CLI;
- a voice confirmer (Sprint 5): speech-to-text, then the same yes/no match;
- a camera confirmer (an idea for later): who is it, and what gesture.

The gate treats them all alike: ``unclear`` counts as no, an answer must be
for the exact request it was asked for (``request_id``), and an answer that
arrives after ``confirmation_ttl_seconds`` is refused.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Protocol

from backend.schemas import PermissionTier
from backend.security.permissions import PermissionPolicy


class Verdict(str, Enum):
    YES = "yes"
    NO = "no"
    UNCLEAR = "unclear"  # treated as no


@dataclass(frozen=True)
class ConfirmationRequest:
    request_id: str
    tool_name: str
    arguments: dict[str, Any]
    tier: PermissionTier
    asked_at: datetime
    expires_at: datetime

    def describe(self) -> str:
        return f"{self.tool_name}({json.dumps(self.arguments, ensure_ascii=False)})"


@dataclass(frozen=True)
class ConfirmationAnswer:
    request_id: str
    verdict: Verdict
    source: str  # how the owner answered: "terminal", later "voice", "camera"
    detail: str | None = None


class Confirmer(Protocol):
    def confirm(self, request: ConfirmationRequest) -> ConfirmationAnswer: ...


@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    tier: PermissionTier | None = None
    # How the call was approved, for the action journal: "auto" or the
    # confirmer's source ("terminal", ...).
    approval: str | None = None
    # For the model when the call is refused.
    message: str | None = None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PermissionGate:
    def __init__(
        self,
        policy: PermissionPolicy,
        confirmer: Confirmer | None = None,
        clock: Callable[[], datetime] = _utcnow,
    ) -> None:
        self.policy = policy
        self.confirmer = confirmer
        self._clock = clock

    def is_read_only(self, tool_name: str) -> bool:
        return self.policy.is_read_only(tool_name)

    def check(self, tool_name: str, arguments: dict[str, Any]) -> GateDecision:
        """Decide one call. May block while the owner is asked; never raises for a refusal."""
        rule = self.policy.rule(tool_name)
        if rule is None:
            return GateDecision(
                allowed=False,
                message=(
                    f"Tool '{tool_name}' is not allowed: the owner has not classified it in "
                    "the permission settings, so it cannot be used. Tell the user; do not "
                    "try another tool as a stand-in."
                ),
            )
        if not rule.needs_confirmation:
            return GateDecision(allowed=True, tier=rule.tier, approval="auto")
        return self._ask_owner(tool_name, arguments, rule.tier)

    def _ask_owner(
        self, tool_name: str, arguments: dict[str, Any], tier: PermissionTier
    ) -> GateDecision:
        if self.confirmer is None:
            return GateDecision(
                allowed=False,
                tier=tier,
                message=(
                    f"Tool '{tool_name}' needs the owner's confirmation, and there is no way "
                    "to ask for it right now. It was not run; tell the user."
                ),
            )
        asked_at = self._clock()
        request = ConfirmationRequest(
            request_id=uuid.uuid4().hex,
            tool_name=tool_name,
            arguments=dict(arguments),
            tier=tier,
            asked_at=asked_at,
            expires_at=asked_at + timedelta(seconds=self.policy.confirmation_ttl_seconds),
        )
        try:
            answer = self.confirmer.confirm(request)
        except Exception as exc:  # a broken confirmer must fail closed
            return self._refused(tier, f"asking the owner failed ({type(exc).__name__})")

        if answer.request_id != request.request_id:
            return self._refused(tier, "the answer was for a different request")
        if self._clock() > request.expires_at:
            return self._refused(tier, "the owner's answer came after the confirmation expired")
        if answer.verdict is Verdict.YES:
            return GateDecision(allowed=True, tier=tier, approval=answer.source)
        if answer.verdict is Verdict.NO:
            return GateDecision(
                allowed=False,
                tier=tier,
                message=(
                    f"The owner (the user you are talking to) was asked to confirm "
                    f"'{tool_name}' and answered no, so it was not run. Tell them it was "
                    "cancelled at their answer; do not retry unless they ask again."
                ),
            )
        return self._refused(tier, "the owner's answer was unclear, which counts as no")

    @staticmethod
    def _refused(tier: PermissionTier, reason: str) -> GateDecision:
        return GateDecision(
            allowed=False,
            tier=tier,
            message=f"Not confirmed: {reason}. The action was not run; tell the user.",
        )


# Typed answers the terminal accepts (Indonesian and English).
_YES = {"y", "ya", "yes", "iya"}
_NO = {"n", "no", "tidak", "nggak", "gak", "enggak"}


class TerminalConfirmer:
    """Asks the owner in the terminal: the y/n answer goes straight to the gate."""

    source = "terminal"

    def __init__(
        self,
        read: Callable[[str], str] = input,
        write: Callable[[str], None] = print,
    ) -> None:
        self._read = read
        self._write = write

    def confirm(self, request: ConfirmationRequest) -> ConfirmationAnswer:
        self._write(
            f"[konfirmasi] F.R.I.D.A.Y mau menjalankan {request.describe()} "
            f"(tingkat: {request.tier.value})."
        )
        reply = self._read("Jalankan? (y/n) ").strip().lower()
        if reply in _YES:
            verdict = Verdict.YES
        elif reply in _NO:
            verdict = Verdict.NO
        else:
            verdict = Verdict.UNCLEAR
        return ConfirmationAnswer(request.request_id, verdict, self.source, detail=reply or None)

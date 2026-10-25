"""Environment configuration for M1 Agent Core.

Loads ``.env`` once at import time and exposes the handful of variables
M1 needs. Kept as plain functions rather than a settings framework — four
variables don't justify the dependency.
"""

import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_ANTHROPIC_MODEL = "claude-haiku-4-5"
DEFAULT_MEMORY_COMPACTION_THRESHOLD_TOKENS = 6000
DEFAULT_MEMORY_COMPACTION_SAFETY_MARGIN_TOKENS = 500
DEFAULT_MEMORY_KEEP_RECENT_MESSAGES = 6
DEFAULT_MEMORY_RECALL_LIMIT = 5
# Safety cap, not a tuned value: ~2k tokens per tool result. Real device
# state, file listings or API payloads must not flood the context in the
# middle of a turn, where compaction can't run.
DEFAULT_TOOL_RESULT_MAX_CHARS = 8000

# NOTE: context_limit / reserved_output_tokens / model-specific token
# budgets are deliberately NOT implemented here. F.R.I.D.A.Y only has one
# provider/model wired up right now (claude-haiku-4-5, Anthropic) — a
# per-model capability abstraction would be premature until multi-model /
# local inference / model routing actually lands (Sprint 8, M12-M13) and
# different models genuinely need different budgets. Revisit then.


def get_llm_provider() -> str:
    return os.environ.get("LLM_PROVIDER", "anthropic")


def get_anthropic_api_key() -> str | None:
    return os.environ.get("ANTHROPIC_API_KEY") or None


def get_anthropic_model() -> str:
    return os.environ.get("ANTHROPIC_MODEL") or DEFAULT_ANTHROPIC_MODEL


def get_openai_api_key() -> str | None:
    return os.environ.get("OPENAI_API_KEY") or None


def get_memory_compaction_threshold_tokens() -> int:
    return int(
        os.environ.get("MEMORY_COMPACTION_THRESHOLD_TOKENS")
        or DEFAULT_MEMORY_COMPACTION_THRESHOLD_TOKENS
    )


def get_memory_compaction_safety_margin_tokens() -> int:
    """Buffer added to the last known usage before comparing against the threshold.

    ``last_input_tokens`` is exact but one turn stale (it's the usage from
    the *previous* call, not an estimate of this one) — this margin makes
    the check trigger a bit earlier to compensate, without resorting to a
    character-count/tokenizer estimate of the upcoming turn.
    """
    return int(
        os.environ.get("MEMORY_COMPACTION_SAFETY_MARGIN_TOKENS")
        or DEFAULT_MEMORY_COMPACTION_SAFETY_MARGIN_TOKENS
    )


def get_memory_keep_recent_messages() -> int:
    return int(
        os.environ.get("MEMORY_KEEP_RECENT_MESSAGES") or DEFAULT_MEMORY_KEEP_RECENT_MESSAGES
    )


def get_memory_recall_default_limit() -> int:
    """How many past turns ``recall_memory`` returns when the model omits ``limit``."""
    return int(os.environ.get("MEMORY_RECALL_DEFAULT_LIMIT") or DEFAULT_MEMORY_RECALL_LIMIT)


def get_tool_result_max_chars() -> int:
    """Longest tool result (serialized) the loop puts into the conversation."""
    return int(os.environ.get("TOOL_RESULT_MAX_CHARS") or DEFAULT_TOOL_RESULT_MAX_CHARS)


def get_timezone_name() -> str | None:
    """IANA time zone of the home (e.g. ``Asia/Jakarta``); None = the OS local zone.

    A runtime setting, not a profile fact: the home's zone is fixed, and a
    temporary travel override can come later without changing this default.
    """
    return os.environ.get("FRIDAY_TIMEZONE") or None

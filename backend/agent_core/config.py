"""Environment configuration for M1 Agent Core.

Loads ``.env`` once at import time and exposes the handful of variables
M1 needs. Kept as plain functions rather than a settings framework — four
variables don't justify the dependency.
"""

import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_ANTHROPIC_MODEL = "claude-haiku-4-5"


def get_llm_provider() -> str:
    return os.environ.get("LLM_PROVIDER", "anthropic")


def get_anthropic_api_key() -> str | None:
    return os.environ.get("ANTHROPIC_API_KEY") or None


def get_anthropic_model() -> str:
    return os.environ.get("ANTHROPIC_MODEL") or DEFAULT_ANTHROPIC_MODEL


def get_openai_api_key() -> str | None:
    return os.environ.get("OPENAI_API_KEY") or None

"""Shared SQLite FTS5 query helpers.

Used by M2b's archive (``backend/memory/archive_store.py``) and M4's tool
catalog (``backend/registry/catalog.py``). Both search user- or
model-written free text with FTS5, and both must never let that text reach
FTS5 as query *syntax* — so the tokenizing and quoting live in one place.

``TOKENIZER`` is the FTS5 tokenizer spec both indexes are created with;
``TOKEN_PATTERN`` mirrors what that tokenizer treats as a word.
"""

from __future__ import annotations

import re

TOKENIZER = "unicode61 remove_diacritics 2"

# Word tokens as FTS5's unicode61 tokenizer would see them. Anything else in a
# query (quotes, parentheses, '*', '-', operator keywords) is syntax to FTS5
# and can never reach it through this pattern — each token is then quoted as
# a phrase, so even "AND"/"OR"/"NOT" become plain literals. Underscore is a
# separator for unicode61 too, so ``set_brightness`` is two words.
TOKEN_PATTERN = re.compile(r"[^\W_]+")


def tokens(query: str) -> list[str]:
    return TOKEN_PATTERN.findall(query)


def fts_query(query_tokens: list[str], operator: str) -> str:
    """Join tokens into a MATCH expression, each quoted as a literal phrase.

    ``operator`` is ``" "`` (implicit AND) or ``" OR "``.
    """
    # Tokens can't contain '"' (see TOKEN_PATTERN) — doubling is defensive.
    quoted = ['"' + token.replace('"', '""') + '"' for token in query_tokens]
    return operator.join(quoted)

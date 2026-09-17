"""M4 tool catalog: every tool F.R.I.D.A.Y knows about, grouped and searchable.

Tool registration is split in two on purpose (MCP-Zero):

- ``ToolCatalog`` (this module) — every tool that *exists*, grouped by
  domain, fingerprinted, searchable. Built once at startup and kept in sync
  with whatever provides the tools.
- ``ToolRegistry`` (``backend/agent_core/tool_registry.py``) — the tools
  *installed* for one turn, i.e. what the model is shown. The orchestrator
  builds it per turn from the catalog's pinned tools; ``find_tools``
  (``discovery_tool.py``) binds more into it mid-turn.

A tool is **pinned** (installed on every turn — the pre-M4 behavior) or
**discoverable** (only reachable through ``find_tools``). That is a policy
of this catalog, not a property of the tool, so it is not a contract field.

**Sync (ScaleMCP, Algorithm 1).** A *provider* — today the app itself, from
M5 on one per device adapter — is the single source of truth for its own
tools. ``sync(provider, tools)`` compares each tool's ``content_hash`` with
what the catalog holds for that provider and adds, updates or removes to
match, without a restart. Nothing is persisted: the catalog is derived
data, rebuilt from its providers on every start.

**Search (Tool-to-Agent Retrieval).** One in-memory SQLite FTS5 index holds
tool documents (name, description, example scenarios, parameter names and
descriptions) *and* domain documents (domain name + summary). A hit on a
domain expands to that domain's tools, so a query that only matches the
device ("lampu ruang tamu") still surfaces its tools, while a query that
matches one operation surfaces just that tool. Keyword search, not
embeddings: the catalog holds tens of tools, and M2b's archive already
showed FTS5 is enough at this size — revisit past a few hundred tools
(PAPER_NOTES.md #4, MCP-Zero/ScaleMCP notes).

Single-writer assumption, like every other store in the project: ``sync``
and ``describe_domain`` are not safe to run concurrently with ``search``.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from backend.dal.fts import TOKENIZER, fts_query, tokens
from backend.schemas import ToolContract
from backend.schemas.tool_contract import validate_identifier

APP_PROVIDER = "app"

_INDEX_DDL = f"""
CREATE VIRTUAL TABLE catalog_fts USING fts5(
    kind UNINDEXED,
    key UNINDEXED,
    domain UNINDEXED,
    text,
    tokenize='{TOKENIZER}'
);
"""

# ``kind DESC`` puts a tool ahead of a domain on an exact score tie ('tool' >
# 'domain'); ``key`` makes the order fully deterministic.
_SEARCH_SQL = """
SELECT kind, key
FROM catalog_fts
WHERE catalog_fts MATCH ?
{domain_clause}
ORDER BY bm25(catalog_fts), kind DESC, key
"""


@dataclass(frozen=True)
class CatalogEntry:
    contract: ToolContract
    fn: Callable[..., Any]
    provider: str
    pinned: bool

    @property
    def name(self) -> str:
        return self.contract.name


@dataclass(frozen=True)
class CatalogHit:
    contract: ToolContract
    fn: Callable[..., Any]
    pinned: bool
    matched_via: str  # "tool": the tool's own text matched; "domain": its domain did


@dataclass(frozen=True)
class SyncReport:
    provider: str
    added: tuple[str, ...] = ()
    updated: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()
    unchanged: tuple[str, ...] = ()

    @property
    def changed(self) -> bool:
        return bool(self.added or self.updated or self.removed)


def _tool_document(contract: ToolContract) -> str:
    parts = [contract.name, contract.description]
    parts.extend(example.scenario for example in contract.examples)
    properties = contract.input_schema.get("properties")
    if isinstance(properties, dict):
        for param, spec in properties.items():
            parts.append(param)
            if isinstance(spec, dict) and isinstance(spec.get("description"), str):
                parts.append(spec["description"])
    return "\n".join(parts)


def _domain_document(domain: str, summary: str | None) -> str:
    return domain if summary is None else f"{domain}\n{summary}"


class ToolCatalog:
    def __init__(self) -> None:
        self._entries: dict[str, CatalogEntry] = {}
        self._summaries: dict[str, str] = {}
        self._index: sqlite3.Connection | None = None

    # -- registration -----------------------------------------------------

    def register(
        self,
        contract: ToolContract,
        fn: Callable[..., Any],
        *,
        pinned: bool = True,
        provider: str = APP_PROVIDER,
    ) -> None:
        """Add one tool. A name already in the catalog raises, like ToolRegistry.register().

        For a provider that owns a whole set of tools and may change them at
        runtime (a device adapter), use ``sync()`` instead.
        """
        validate_identifier(provider, "provider")
        if contract.name in self._entries:
            raise ValueError(f"Tool {contract.name!r} is already in the catalog")
        self._entries[contract.name] = CatalogEntry(contract, fn, provider, pinned)
        self._invalidate_index()

    def sync(
        self,
        provider: str,
        tools: Iterable[tuple[ToolContract, Callable[..., Any]]],
        *,
        pinned: bool = False,
    ) -> SyncReport:
        """Make the catalog hold exactly ``tools`` for ``provider``.

        A tool whose ``content_hash`` (or pinned policy) differs from the
        stored one is *updated*; a stored tool of this provider that is no
        longer offered is *removed*. Validation happens before any change,
        so a rejected sync leaves the catalog untouched.
        """
        validate_identifier(provider, "provider")
        incoming: dict[str, tuple[ToolContract, Callable[..., Any]]] = {}
        for contract, fn in tools:
            if contract.name in incoming:
                raise ValueError(f"Provider {provider!r} offered tool {contract.name!r} twice")
            owner = self._entries.get(contract.name)
            if owner is not None and owner.provider != provider:
                raise ValueError(
                    f"Tool {contract.name!r} from provider {provider!r} collides with "
                    f"the tool of the same name from provider {owner.provider!r}"
                )
            incoming[contract.name] = (contract, fn)

        current = {name: e for name, e in self._entries.items() if e.provider == provider}
        added: list[str] = []
        updated: list[str] = []
        unchanged: list[str] = []
        for name, (contract, fn) in incoming.items():
            previous = current.get(name)
            if previous is None:
                added.append(name)
            elif previous.contract.content_hash != contract.content_hash or previous.pinned != pinned:
                updated.append(name)
            else:
                unchanged.append(name)
            # Always keep the newest callable, even for an unchanged tool: an
            # adapter that reconnected hands over fresh closures, and the old
            # ones may be bound to a dead connection.
            self._entries[name] = CatalogEntry(contract, fn, provider, pinned)

        removed = sorted(name for name in current if name not in incoming)
        for name in removed:
            del self._entries[name]

        report = SyncReport(
            provider=provider,
            added=tuple(sorted(added)),
            updated=tuple(sorted(updated)),
            removed=tuple(removed),
            unchanged=tuple(sorted(unchanged)),
        )
        if report.changed:
            self._invalidate_index()
        return report

    def describe_domain(self, domain: str, summary: str) -> None:
        """One-sentence summary of a domain (MCP-Zero's server summary).

        Indexed next to the tools and listed in find_tools' description, so
        the model can tell what kind of thing a domain covers without seeing
        its tools.
        """
        validate_identifier(domain, "domain")
        if not summary.strip():
            raise ValueError("domain summary must not be empty")
        self._summaries[domain] = summary.strip()
        self._invalidate_index()

    # -- lookup -----------------------------------------------------------

    def has(self, name: str) -> bool:
        return name in self._entries

    def get(self, name: str) -> CatalogEntry:
        try:
            return self._entries[name]
        except KeyError:
            raise KeyError(f"No tool named {name!r} in the catalog") from None

    def entries(self) -> list[CatalogEntry]:
        return list(self._entries.values())

    def pinned_tools(self) -> list[CatalogEntry]:
        return [entry for entry in self._entries.values() if entry.pinned]

    def has_discoverable_tools(self) -> bool:
        return any(not entry.pinned for entry in self._entries.values())

    def discoverable_domains(self) -> list[tuple[str, str | None]]:
        """``(domain, summary)`` for every domain holding at least one discoverable tool."""
        domains = sorted({e.contract.domain for e in self._entries.values() if not e.pinned})
        return [(domain, self._summaries.get(domain)) for domain in domains]

    # -- search -----------------------------------------------------------

    def search(
        self,
        query: str,
        *,
        domain: str | None = None,
        limit: int = 5,
    ) -> list[CatalogHit]:
        """Keyword search over tools and domains, best match first.

        All terms first (precision); only if nothing matches, any term
        (recall) — same strategy as the M2b archive. Pinned tools are
        searchable too: the caller decides what "already available" means.
        """
        if limit < 1:
            raise ValueError("limit must be at least 1")
        query_tokens = tokens(query)
        if not query_tokens:
            return []

        domain_clause = "AND domain = ?" if domain is not None else ""
        extra: tuple[Any, ...] = (domain,) if domain is not None else ()
        sql = _SEARCH_SQL.format(domain_clause=domain_clause)

        conn = self._ensure_index()
        rows = conn.execute(sql, (fts_query(query_tokens, " "), *extra)).fetchall()
        if not rows and len(query_tokens) > 1:
            rows = conn.execute(sql, (fts_query(query_tokens, " OR "), *extra)).fetchall()

        hits: list[CatalogHit] = []
        seen: set[str] = set()
        for kind, key in rows:
            if kind == "tool":
                candidates = [(self._entries[key], "tool")]
            else:
                candidates = [(entry, "domain") for entry in self._tools_in_domain(key)]
            for entry, matched_via in candidates:
                if entry.name in seen:
                    continue
                seen.add(entry.name)
                hits.append(CatalogHit(entry.contract, entry.fn, entry.pinned, matched_via))
                if len(hits) >= limit:
                    return hits
        return hits

    def _tools_in_domain(self, domain: str) -> list[CatalogEntry]:
        members = [e for e in self._entries.values() if e.contract.domain == domain]
        # Discoverable tools first: pinned ones are already installed every turn.
        return sorted(members, key=lambda e: (e.pinned, e.name))

    # -- index ------------------------------------------------------------

    def _invalidate_index(self) -> None:
        if self._index is not None:
            self._index.close()
        self._index = None

    def _ensure_index(self) -> sqlite3.Connection:
        """Build the FTS5 index on first search after any change.

        Rebuilt in full rather than patched: at tens of tools this is cheap,
        and it can never drift from ``_entries``.
        """
        if self._index is None:
            # check_same_thread=False: the catalog is built once at startup and
            # may be searched from whichever thread runs a turn.
            conn = sqlite3.connect(":memory:", check_same_thread=False)
            conn.executescript(_INDEX_DDL)
            rows = [
                ("tool", entry.name, entry.contract.domain, _tool_document(entry.contract))
                for entry in self._entries.values()
            ]
            for domain in sorted({e.contract.domain for e in self._entries.values()}):
                rows.append(
                    ("domain", domain, domain, _domain_document(domain, self._summaries.get(domain)))
                )
            conn.executemany(
                "INSERT INTO catalog_fts (kind, key, domain, text) VALUES (?, ?, ?, ?)", rows
            )
            self._index = conn
        return self._index

"""Contract format versioning.

CONTRACT_VERSION tracks the *shape* of contract schemas themselves (e.g.
ToolContract's field set), separate from an individual tool's own
``version``. Bump this when a schema change would break an existing
contract instance — analogous to AgentOS's versioned plugin/driver ABI:
old contracts must keep loading under a compatible CONTRACT_VERSION.

History:
- 1.0.0 (Sprint 1, M0) — name, version, description, input/output schema,
  annotations, permission_tier.
- 1.1.0 (Sprint 3, M4) — additive: ``domain`` and ``examples`` (both with
  defaults, so every 1.0.0 contract still validates) plus the derived
  ``content_hash``.
"""

CONTRACT_VERSION = "1.1.0"

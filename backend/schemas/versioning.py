"""Contract format versioning.

CONTRACT_VERSION tracks the *shape* of contract schemas themselves (e.g.
ToolContract's field set), separate from an individual tool's own
``version``. Bump this when a schema change would break an existing
contract instance — analogous to AgentOS's versioned plugin/driver ABI:
old contracts must keep loading under a compatible CONTRACT_VERSION.
"""

CONTRACT_VERSION = "1.0.0"

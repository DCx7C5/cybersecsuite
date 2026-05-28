import msgspec
from typing import Any

from .frontmatter_header import BaseFrontmatterHeader
from .protocols import BaseCommunicator


# ── Entity-specific header types ──────────────────────────────────────────────
# Each inherits from BaseFrontmatterHeader (the canonical header type) so that
# entities can later inherit from their headers directly.


class BaseAgentHeader(BaseFrontmatterHeader, frozen=True):
    """Metadata header for agents entities.

    Inherits ``name``, ``description``, ``hash``, ``signature``, ``body``
    from ``BaseFrontmatterHeader``.  Fields mirror .claude/agents/*.md YAML
    frontmatter and A2A AgentCard metadata.

    ``__post_init__`` is overridden to skip SecureMD field enforcement —
    entity metadata is not a signed document.
    """

    def __post_init__(self) -> None:
        pass

    model: str = "sonnet"
    role: str = ""
    max_turns: int = 25
    effort: str = "medium"
    version: str = "0.1.0"
    alias: str | None = None
    tools: list[str] = msgspec.field(default_factory=list)
    disallowed_tools: list[str] = msgspec.field(default_factory=list)
    base_url: str | None = None
    streaming: bool = False
    push_notifications: bool = False


class BaseSkillHeader(BaseFrontmatterHeader, frozen=True):
    """Metadata header for skills entities.

    Fields mirror SKILL.md YAML frontmatter and marketplace ProviderMeta fields.
    """

    def __post_init__(self) -> None:
        pass

    version: str = "0.1.0"
    domain: str | None = None
    tags: list[str] = msgspec.field(default_factory=list)
    allowed_tools: list[str] = msgspec.field(default_factory=list)
    source_url: str | None = None
    marketplace_id: str | None = None
    install_path: str | None = None


class BaseAccountHeader(BaseFrontmatterHeader, frozen=True):
    """Metadata header for account entities.

    Represents credentials and authentication state for an external provider.
    """

    def __post_init__(self) -> None:
        pass

    provider_id: str = ""
    auth_method: str = "api_key"
    active: bool = False


class BaseToolHeader(BaseFrontmatterHeader, frozen=True):
    """Catalog and access-control metadata for tools entities.

    This is the base layer — all tools headers inherit from here.
    ``ToolHeader`` (in ``headers/tools.py``) extends this with the
    execution-facing parameter schema and examples.
    """

    def __post_init__(self) -> None:
        pass

    version: str = "0.1.0"
    tags: list[str] = msgspec.field(default_factory=list)
    min_tier: str = "free"
    category: str = "general"
    agent_source: str | None = None
    deprecated: bool = False
    deprecated_at: str | None = None


class BaseRoleHeader(BaseFrontmatterHeader, frozen=True):
    """Metadata header for role entities with path-based permissions.

    ``role_id`` mirrors the canonical string used in agents frontmatter
    (e.g. ``"orchestrator"``, ``"team-mode"``).

    ``scopes`` constrains where this role applies:
    ``"global"`` | ``"team"`` | ``"agent"``.

    Path-based permissions control filesystem access:
    - ``read_paths``: glob patterns allowed for read (e.g., "project/**", "~/.css/plans/*")
    - ``write_paths``: glob patterns allowed for write/modify
    - ``base_permissions``: foundational permissions (action strings like "task:execute")
    """

    def __post_init__(self) -> None:
        pass

    role_id: str = ""
    scope: str = "global"
    permissions: list[str] = msgspec.field(default_factory=list)
    read_paths: list[str] = msgspec.field(default_factory=list)
    write_paths: list[str] = msgspec.field(default_factory=list)
    base_permissions: dict[str, bool] = msgspec.field(default_factory=dict)

    def has_path_permission(self, path: str, action: str) -> bool:
        """Check if role has permission for filesystem action on path."""
        from fnmatch import fnmatch

        allowed_paths = self.read_paths if action == "read" else self.write_paths
        for pattern in allowed_paths:
            if fnmatch(path, pattern) or fnmatch(path, pattern + "/*"):
                return True
        return False


# ── Entity classes ────────────────────────────────────────────────────────────


class BaseEntity(msgspec.Struct, frozen=True, kw_only=True):
    """Root domain entity — identity + descriptive metadata + arbitrary metadata bag.

    The canonical ``name`` / ``description`` fields mirror those on
    ``BaseFrontmatterHeader`` (``base_frontmatter_header.py``), the
    source of truth for the header concept.  They default to ``""`` so
    that subclasses may set them in ``__post_init__``.
    """

    name: str = ""
    description: str = ""
    id: str = ""
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)
    _communicator: BaseCommunicator | None = None

    @property
    def communicator(self) -> BaseCommunicator | None:
        """Get the communicator for this entity (if set)."""
        return self._communicator

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return msgspec.to_builtins(self)


class BaseTool(BaseEntity, frozen=True):
    """A callable tool exposed by an MCP server, SDK, or agent definition."""

    header: BaseToolHeader | None = None
    tool_name: str = ""
    display_name: str = ""
    tool_type: str = "mcp_cybersec"
    mcp_server: str | None = None
    required_beta: str | None = None
    sdk_type_string: str | None = None
    required_provider: str | None = None
    enabled_by_default: bool = True
    tags: list[str] = msgspec.field(default_factory=list)
    input_schema: dict[str, Any] = msgspec.field(default_factory=dict)

    @property
    def mcp_tool_name(self) -> str:
        """Full namespace MCP tool name used in API calls."""
        if self.mcp_server:
            return f"mcp__{self.mcp_server}__{self.tool_name}"
        return self.tool_name

    @property
    def is_mcp(self) -> bool:
        return self.tool_type.startswith("mcp_")

    @property
    def is_beta(self) -> bool:
        return self.tool_type == "sdk_beta"


class BaseAgent(BaseEntity, frozen=True):
    """A registered agent entity with its A2A endpoint and exposed skills references."""

    header: BaseAgentHeader | None = None
    skill_ids: list[str] = msgspec.field(default_factory=list)
    tools: list[BaseTool] = msgspec.field(default_factory=list)

    @property
    def is_orchestrator(self) -> bool:
        return bool(self.header and getattr(self.header, 'role', None) == "orchestrator")

    @property
    def is_default(self) -> bool:
        return bool(self.metadata.get("default", False))


class BaseSkill(BaseEntity, frozen=True):
    """An installed skill entity with its source location and provider origin."""

    header: BaseSkillHeader | None = None
    kind: str = "skills"
    provider: str = "universal"
    source_path: str | None = None
    tools: list[BaseTool] = msgspec.field(default_factory=list)


class BaseRole(BaseEntity, frozen=True):
    """A role that can be assigned to an agent — governs capabilities and routing."""

    header: BaseRoleHeader | None = None
    role_id: str = ""
    can_orchestrate: bool = False
    can_broadcast: bool = False
    can_spawn_subagents: bool = False
    allowed_tool_types: list[str] = msgspec.field(default_factory=list)

    def can_use_tool_type(self, tool_type: str) -> bool:
        if not self.allowed_tool_types:
            return True
        return tool_type in self.allowed_tool_types

    def has_permission(self, token: str) -> bool:
        if self.header:
            return token in getattr(self.header, 'permissions', [])
        return False

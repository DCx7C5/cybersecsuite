"""Entity metadata headers — msgspec.Struct (Phase 6 P1).

Replaces @dataclass with msgspec.Struct for 10-40× faster serialization.
All headers are frozen (immutable) value types.
"""

import msgspec

class BaseHeader(msgspec.Struct, frozen=True):
    """Base metadata header for all entities."""

    name: str
    description: str
    version: str = "0.1.0"

class BaseAgentHeader(BaseHeader, frozen=True):
    """Metadata header for agents entities.
    
    Fields mirror .claude/agents/*.md YAML frontmatter and A2A AgentCard metadata.
    """
    
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

class BaseSkillHeader(BaseHeader, frozen=True):
    """Metadata header for skills entities.
    
    Fields mirror SKILL.md YAML frontmatter and marketplace ProviderMeta fields.
    """
    
    version: str = "0.1.0"
    domain: str | None = None
    tags: list[str] = msgspec.field(default_factory=list)
    allowed_tools: list[str] = msgspec.field(default_factory=list)
    source_url: str | None = None
    marketplace_id: str | None = None
    install_path: str | None = None

class BaseAccountHeader(BaseHeader, frozen=True):
    """Metadata header for account entities.
    
    Represents credentials and authentication state for an external provider.
    """
    
    provider_id: str = ""
    auth_method: str = "api_key"
    active: bool = False

class BaseToolHeader(BaseHeader, frozen=True):
    """Catalog and access-control metadata for tools entities.
    
    This is the base layer — all tools headers inherit from here.
    ``ToolHeader`` (in ``headers/tools.py``) extends this with the
    execution-facing parameter schema and examples.
    
    Fields are modeled directly from ``ToolRegistry`` (DB model):
    """
    
    version: str = "0.1.0"
    tags: list[str] = msgspec.field(default_factory=list)
    min_tier: str = "free"
    category: str = "general"
    agent_source: str | None = None
    deprecated: bool = False
    deprecated_at: str | None = None

class BaseRoleHeader(BaseHeader, frozen=True):
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
    
    role_id: str = ""
    scope: str = "global"
    permissions: list[str] = msgspec.field(default_factory=list)
    read_paths: list[str] = msgspec.field(default_factory=list)
    write_paths: list[str] = msgspec.field(default_factory=list)
    base_permissions: dict[str, bool] = msgspec.field(default_factory=dict)
    
    def has_path_permission(self, path: str, action: str) -> bool:
        """Check if role has permission for filesystem action on path.
        
        Args:
            path: Filesystem path to check (absolute or relative)
            action: "read" or "write"
        
        Returns:
            True if path matches allowed patterns for action, False otherwise
        """
        from fnmatch import fnmatch
        
        allowed_paths = self.read_paths if action == "read" else self.write_paths
        
        # Check if path matches any allowed pattern
        for pattern in allowed_paths:
            if fnmatch(path, pattern) or fnmatch(path, pattern + "/*"):
                return True
        
        return False

__all__ = [
    "BaseHeader",
    "BaseAgentHeader",
    "BaseSkillHeader",
    "BaseAccountHeader",
    "BaseToolHeader",
    "BaseRoleHeader",
]

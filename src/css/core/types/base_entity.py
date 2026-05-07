import msgspec
from typing import Any, List

from .base_protocols import BaseCommunicator
from .base_headers import (
    BaseHeader,
    BaseAgentHeader,
    BaseRoleHeader,
    BaseSkillHeader,
    BaseToolHeader,
)


class BaseEntity(BaseHeader):
    """Root domain entity — identity + descriptive header + arbitrary metadata bag."""
    
    id: str = ""
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize non-Struct communicator after instantiation."""
        self._communicator: BaseCommunicator | None = None
    
    @property
    def communicator(self) -> BaseCommunicator | None:
        """Get the communicator for this entity (if set)."""
        return self._communicator
    
    @communicator.setter
    def communicator(self, value: Any) -> BaseCommunicator | None:
        """Set the communicator for this entity."""
        self._communicator = value
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return msgspec.to_builtin(self)  # type: ignore[no-any-return]


class BaseTool(BaseEntity):
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
    tags: List[str] = msgspec.field(default_factory=list)
    input_schema: dict[str, Any] = msgspec.field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize tool-specific fields."""
        super().__post_init__()
    
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


class BaseAgent(BaseEntity):
    """A registered agent entity with its A2A endpoint and exposed skills references."""
    
    header: BaseAgentHeader | None = None
    skill_ids: List[str] = msgspec.field(default_factory=list)
    tools: List[BaseTool] = msgspec.field(default_factory=list)
    
    def __post_init__(self):
        """Initialize agent-specific fields."""
        super().__post_init__()
    
    @property
    def is_orchestrator(self) -> bool:
        return bool(self.header and getattr(self.header, 'role', None) == "orchestrator")
    
    @property
    def is_default(self) -> bool:
        return bool(self.metadata.get("default", False))


class BaseSkill(BaseEntity):
    """An installed skill entity with its source location and provider origin."""
    
    header: BaseSkillHeader | None = None
    kind: str = "skills"
    provider: str = "universal"
    source_path: str | None = None
    tools: List[BaseTool] = msgspec.field(default_factory=list)
    
    def __post_init__(self):
        """Initialize skill-specific fields."""
        super().__post_init__()


class BaseRole(BaseEntity):
    """A role that can be assigned to an agent — governs capabilities and routing."""
    
    header: BaseRoleHeader | None = None
    role_id: str = ""
    can_orchestrate: bool = False
    can_broadcast: bool = False
    can_spawn_subagents: bool = False
    allowed_tool_types: List[str] = msgspec.field(default_factory=list)
    
    def __post_init__(self):
        """Initialize role-specific fields."""
        super().__post_init__()
    
    def can_use_tool_type(self, tool_type: str) -> bool:
        if not self.allowed_tool_types:
            return True
        return tool_type in self.allowed_tool_types
    
    def has_permission(self, token: str) -> bool:
        if self.header:
            return token in getattr(self.header, 'permissions', [])
        return False


__all__ = [
    "BaseEntity",
    "BaseTool",
    "BaseAgent",
    "BaseSkill",
    "BaseRole",
]

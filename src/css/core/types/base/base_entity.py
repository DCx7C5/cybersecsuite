from abc import ABC
from dataclasses import asdict, dataclass, field
from typing import Any, Dict

from ..base import BaseCommunicator
from ..headers import (

    BaseAgentHeader,
    BaseHeader,
    BaseRoleHeader,
    BaseSkillHeader,
    BaseToolHeader,
)


class BaseEntity(BaseHeader, ABC):
    """Root domain entity — identity + descriptive header + arbitrary metadata bag."""

    def __init__(self, id: str, name: str, description: str, metadata: Dict[str, Any] | None = None):
        self.id = id
        self.name = name
        self.description = description
        self.metadata = metadata or {}

    def __post_init__(self) -> None:
        """Initialize non-dataclass communicator after instantiation."""
        self._communicator: BaseCommunicator | None = None

    @property
    def communicator(self) -> BaseCommunicator | None:
        """Get the communicator for this entity (if set)."""
        return self._communicator

    @communicator.setter
    def communicator(self, value: BaseCommunicator | None) -> None:
        """Set the communicator for this entity."""
        self._communicator = value

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BaseTool(BaseEntity):
    """A callable tools exposed by an MCP server, SDK, or agents definition.

    ``tool_name`` is the canonical snake_case identifier (e.g. ``vault_scaffold``,
    ``canvas_create``). Matches the key in ToolRegistry.

    ``tool_type`` categorises the source:
      ``mcp_cybersec`` | ``mcp_dystopian`` | ``sdk_builtin`` |
      ``sdk_beta`` | ``agent_sdk`` | ``external``

    ``input_schema`` is the JSON Schema dict for the tools's parameters, matching
    the ``input_schema`` / ``parameters`` field accepted by the Anthropic API.

    ``mcp_server`` is the MCP server name when ``tool_type`` starts with ``mcp_``
    (e.g. ``"cybersec"``).

    ``required_beta`` is the beta header string needed to activate beta SDK tools
    (e.g. ``"memory-2025-08-18"``).

    ``sdk_type_string`` is the raw ``type`` value passed to the Anthropic API when
    constructing the tools block for ``sdk_builtin`` / ``sdk_beta`` tools.

    ``required_provider`` constrains which AI provider can use this tools
    (e.g. ``"anthropic"``).
    """

    header: BaseToolHeader | None = None
    tool_name: str = ""
    display_name: str = ""
    tool_type: str = "mcp_cybersec"
    mcp_server: str | None = None
    required_beta: str | None = None
    sdk_type_string: str | None = None
    required_provider: str | None = None
    enabled_by_default: bool = True
    tags: list[str] = field(default_factory=list)
    input_schema: dict[str, Any] = field(default_factory=dict)

    @property
    def mcp_tool_name(self) -> str:
        """Full namespaced MCP tools name used in API calls (e.g. ``mcp__cybersec__vault_scaffold``)."""
        if self.mcp_server:
            return f"mcp__{self.mcp_server}__{self.tool_name}"
        return self.tool_name

    @property
    def is_mcp(self) -> bool:
        return self.tool_type.startswith("mcp_")

    @property
    def is_beta(self) -> bool:
        return self.tool_type == "sdk_beta"


@dataclass
class BaseAgent(BaseEntity):
    """A registered agents entity with its A2A endpoint and exposed skills references.

    ``skill_ids`` lists the skills IDs the agents exposes (resolved from its AgentCard).
    ``tools`` are the BaseTool instances this agents is permitted to call.
    """

    header: BaseAgentHeader | None = None
    skill_ids: list[str] = field(default_factory=list)
    tools: list[BaseTool] = field(default_factory=list)

    @property
    def is_orchestrator(self) -> bool:
        return bool(self.header and self.header.role == "orchestrator")

    @property
    def is_default(self) -> bool:
        return bool(self.metadata.get("default", False))




@dataclass
class BaseSkill(BaseEntity):
    """An installed skills entity with its source location and provider origin.

    ``kind`` matches the marketplace vocabulary: "skills" | "combo" | "template".
    ``provider`` identifies the AI provider this skills targets.
    ``source_path`` is the filesystem path to the SKILL.md (or equivalent) file.
    ``tools`` holds resolved tools objects (populated from header.allowed_tools).
    """

    header: BaseSkillHeader | None = None
    kind: str = "skills"
    provider: str = "universal"
    source_path: str | None = None
    tools: list[BaseTool] = field(default_factory=list)


@dataclass
class BaseRole(BaseEntity):
    """A role that can be assigned to an agents — governs capabilities and routing.

    ``role_id`` is the canonical identifier used in agents frontmatter
    (e.g. ``"orchestrator"``, ``"team-mode"``, ``"researcher"``).

    ``can_orchestrate`` — may coordinate multi-step plans and direct sub-agents.
    ``can_broadcast`` — may publish broadcast messages across teams.
    ``can_spawn_subagents`` — may issue Task tools calls or equivalent.

    ``allowed_tool_types`` — restricts which ``tool_type`` values this role may
    invoke. Empty list = unrestricted.
    """

    header: BaseRoleHeader | None = None
    role_id: str = ""
    can_orchestrate: bool = False
    can_broadcast: bool = False
    can_spawn_subagents: bool = False
    allowed_tool_types: list[str] = field(default_factory=list)

    def can_use_tool_type(self, tool_type: str) -> bool:
        if not self.allowed_tool_types:
            return True
        return tool_type in self.allowed_tool_types

    def has_permission(self, token: str) -> bool:
        if self.header:
            return token in self.header.permissions
        return False
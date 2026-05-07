"""Runtime-checkable Protocols for domain entities (Phase 6 P1).

Replaces @dataclass+ABC BaseEntity hierarchy with Protocol classes.
Uses @runtime_checkable for isinstance() checks.

Usage::
    from css.core.types.protocols import AgentLike, SkillLike, ToolLike
    
    def process_agent(agent: AgentLike) -> None:
        print(agent.communicator)
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class AgentLike(Protocol):
    """Protocol for agent-like entities.

    Any class implementing this protocol can be treated as an agent.
    Used for isinstance() checks and type hints.
    """

    @property
    def header(self) -> object:
        """Entity header with identity."""
        ...

    @property
    def communicator(self) -> object | None:
        """Message communicator for this entity."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        ...

    @property
    def skill_ids(self) -> list[str]:
        """Skills this agent exposes."""
        ...

    @property
    def tools(self) -> list[object]:
        """Tools this agent can call."""
        ...

    @property
    def is_orchestrator(self) -> bool:
        """Check if this is an orchestrator agent."""
        ...

    @property
    def is_default(self) -> bool:
        """Check if this is the default agent."""
        ...


@runtime_checkable
class SkillLike(Protocol):
    """Protocol for skill-like entities.

    Any class implementing this protocol can be treated as a skill.
    """

    @property
    def header(self) -> object:
        """Entity header with identity."""
        ...

    @property
    def communicator(self) -> object | None:
        """Message communicator for this entity."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        ...

    @property
    def kind(self) -> str:
        """Skill kind: 'skills' | 'combo' | 'template'."""
        ...

    @property
    def provider(self) -> str:
        """Provider this skill targets."""
        ...

    @property
    def source_path(self) -> str | None:
        """Filesystem path to SKILL.md."""
        ...

    @property
    def tools(self) -> list[object]:
        """Tools resolved from this skill."""
        ...


@runtime_checkable
class ToolLike(Protocol):
    """Protocol for tool-like entities.

    Any class implementing this protocol can be treated as a tool.
    """

    @property
    def header(self) -> object:
        """Entity header with identity."""
        ...

    @property
    def communicator(self) -> object | None:
        """Message communicator for this entity."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        ...

    @property
    def tool_name(self) -> str:
        """Canonical tool name (e.g., 'vault_scaffold')."""
        ...

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        ...

    @property
    def tool_type(self) -> str:
        """Tool type: 'mcp_cybersec' | 'sdk_builtin' | etc."""
        ...

    @property
    def input_schema(self) -> dict[str, Any]:
        """JSON Schema for tool parameters."""
        ...

    @property
    def is_mcp(self) -> bool:
        """Check if this is an MCP tool."""
        ...

    def is_available(self) -> bool:
        """Check if tool is available for use."""
        ...


@runtime_checkable
class TeamMemberLike(Protocol):
    """Protocol for team member entities.

    Any class implementing this protocol can be treated as a team member.
    """

    @property
    def header(self) -> object:
        """Entity header with identity."""
        ...

    @property
    def communicator(self) -> object | None:
        """Message communicator for this entity."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        ...

    @property
    def agent_id(self) -> str:
        """Agent ID of this team member."""
        ...

    @property
    def team_id(self) -> str:
        """Team this member belongs to."""
        ...

    @property
    def is_active(self) -> bool:
        """Check if member is active."""
        ...


__all__ = ["AgentLike", "SkillLike", "ToolLike", "TeamMemberLike"]

"""Entity metadata headers — foundational data models for domain entities."""

from dataclasses import dataclass, field

from .base import BaseHeader


@dataclass
class BaseAgentHeader(BaseHeader):
    """Metadata header for agent entities.

    Fields mirror .claude/agents/*.md YAML frontmatter and A2A AgentCard metadata.
    """

    model: str = "sonnet"
    role: str = ""
    max_turns: int = 25
    effort: str = "medium"
    version: str = "0.1.0"
    alias: str | None = None
    tools: list[str] = field(default_factory=list)
    disallowed_tools: list[str] = field(default_factory=list)
    base_url: str | None = None
    streaming: bool = False
    push_notifications: bool = False


@dataclass
class BaseSkillHeader(BaseHeader):
    """Metadata header for skill entities.

    Fields mirror SKILL.md YAML frontmatter and marketplace ProviderMeta fields.
    """

    version: str = "0.1.0"
    domain: str | None = None
    tags: list[str] = field(default_factory=list)
    allowed_tools: list[str] = field(default_factory=list)
    source_url: str | None = None
    marketplace_id: str | None = None
    install_path: str | None = None


@dataclass
class BaseAccountHeader(BaseHeader):
    """Metadata header for account entities.

    Represents credentials and authentication state for an external provider.
    """

    provider_id: str = ""
    auth_method: str = "api_key"
    active: bool = False


@dataclass
class BaseToolHeader(BaseHeader):
    """Catalog and access-control metadata for tool entities.

    This is the base layer — all tool headers inherit from here.
    ``ToolHeader`` (in ``headers/tool.py``) extends this with the
    execution-facing parameter schema and examples.

    Fields are modelled directly from ``ToolRegistry`` (DB model):

    ``version``        — schema/catalog version (e.g. ``"1"``, ``"2025-03-05"``).
    ``tags``           — discovery tags (e.g. ``["forensics", "vault"]``).
    ``min_tier``       — minimum account tier needed (``"free"`` | ``"pro"`` | ``"enterprise"``).
    ``category``       — display grouping (e.g. ``"memory"``, ``"network"``, ``"core"``).
    ``agent_source``   — for ``agent_sdk`` tools: dotted path to the owning agent definition.
    ``deprecated``     — True when this tool is scheduled for removal.
    ``deprecated_at``  — ISO-8601 timestamp of when deprecation was announced.
    """

    version: str = "0.1.0"
    tags: list[str] = field(default_factory=list)
    min_tier: str = "free"
    category: str = "general"
    agent_source: str | None = None
    deprecated: bool = False
    deprecated_at: str | None = None


@dataclass
class BaseRoleHeader(BaseHeader):
    """Metadata header for role entities.

    ``role_id`` mirrors the canonical string used in agent frontmatter
    (e.g. ``"orchestrator"``, ``"team-mode"``).

    ``scope`` constrains where this role applies:
    ``"global"`` | ``"team"`` | ``"agent"``.
    """

    role_id: str = ""
    scope: str = "global"
    permissions: list[str] = field(default_factory=list)


__all__ = [
    "BaseHeader",
    "BaseAgentHeader",
    "BaseSkillHeader",
    "BaseAccountHeader",
    "BaseToolHeader",
    "BaseRoleHeader",
]


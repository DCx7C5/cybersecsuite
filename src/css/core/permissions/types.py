"""Type definitions for permissions module."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from pathlib import Path

from .enums import ScopeLevel, Permission
from css.core.types.base_entity import BaseRole
from css.core.types.base_headers import BaseRoleHeader


@dataclass
class PermissionPolicy:
    """Permission policy for a role at a scope level."""

    path_permissions: set[Permission] = field(default_factory=set)
    tool_permissions: set[str] = field(default_factory=set)
    allow_all_tools: bool = False

    def has_permission(self, permission: Permission) -> bool:
        """Check if path permission is granted."""
        return permission in self.path_permissions

    def has_tool_permission(self, tool_id: str) -> bool:
        """Check if tool permission is granted."""
        if self.allow_all_tools:
            return True
        return tool_id in self.tool_permissions


@dataclass
class ScopeContext:
    """Encapsulates permission context for current operation."""

    role: Role
    scope_level: ScopeLevel
    scope_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    token: Optional[str] = None
    parent_scope: Optional["ScopeContext"] = None

    def get_filesystem_path(self) -> Path:
        """Get filesystem path for this scope."""
        if self.scope_level == ScopeLevel.GLOBAL:
            return Path("/var/cache/css")
        elif self.scope_level == ScopeLevel.APP:
            return Path.home() / ".cybersec" / "app"
        elif self.scope_level == ScopeLevel.PROJECT:
            return Path.home() / ".cybersec" / "app" / "projects" / self.scope_id
        elif self.scope_level == ScopeLevel.RUNTIME:
            return Path("/tmp/cybersec") / f"runtime_{self.scope_id}"
        elif self.scope_level == ScopeLevel.SESSION:
            runtime_id = self.parent_scope.scope_id if self.parent_scope else "default"
            return Path("/tmp/cybersec") / f"runtime_{runtime_id}" / "sessions" / self.scope_id
        return Path("/tmp/cybersec")

    def get_parent_scope(self) -> Optional["ScopeContext"]:
        """Get parent scope context."""
        return self.parent_scope

    def has_permission(self, permission: Permission, level: Optional[ScopeLevel] = None) -> bool:
        """Check if role has permission at scope level."""
        check_level = level or self.scope_level
        if check_level == self.scope_level:
            return True
        return False

    def has_tool_permission(self, tool_id: str) -> bool:
        """Check if role can access tool."""
        return True  # TODO: Implement tool permission checks


@dataclass
class TokenPayload:
    """JWT token payload for scope context."""

    scope_context: ScopeContext
    issued_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if token is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


@dataclass
class Role(BaseRole):
    """Concrete role entity with display metadata and a permission set.

    Extends ``BaseRole`` (capability flags, allowed_tool_types) with a
    human-readable ``display_name`` that is auto-derived from ``role_id``
    when not provided.

    Built-in singletons (``ORCHESTRATOR``, ``TEAM_MODE``, ``WORKER``) cover
    the common cases. Use ``get(role_id)`` to look up by string or receive a
    default zero-capability role for unknown IDs.
    """

    def __post_init__(self) -> None:
        if self.header is None:
            self.header = BaseRoleHeader(
                name=self.role_id,
                description="",
            )
        if not self.id:
            self.id = self.role_id
        # Auto-title the header name if it matches the bare role_id
        if self.header.name == self.role_id:
            self.header.name = self.role_id.replace("-", " ").replace("_", " ").title()

    @property
    def display_name(self) -> str:
        return self.header.name if self.header else self.role_id


# ── Built-in role singletons ──────────────────────────────────────────────────

ORCHESTRATOR = Role(
    role_id="orchestrator",
    id="orchestrator",
    name="Orchestrator",
    description="Top-level coordinator — spawns sub-agents and synthesises results.",
    header=BaseRoleHeader(
        name="Orchestrator",
        description="Top-level coordinator — spawns sub-agents and synthesises results.",
        permissions=["tools:write", "agents:spawn", "broadcast:global"],
    ),
    can_orchestrate=True,
    can_broadcast=True,
    can_spawn_subagents=True,
)

TEAM_MODE = Role(
    role_id="team-mode",
    id="team-mode",
    name="Team Lead",
    description="Leads a team of agents; can delegate within the team.",
    header=BaseRoleHeader(
        name="Team Lead",
        description="Leads a team of agents; can delegate within the team.",
        permissions=["tools:write", "agents:spawn", "broadcast:team"],
    ),
    can_orchestrate=True,
    can_broadcast=True,
    can_spawn_subagents=True,
)

WORKER = Role(
    role_id="worker",
    id="worker",
    name="Worker",
    description="Executes tasks assigned by an orchestrator; no spawn rights.",
    header=BaseRoleHeader(
        name="Worker",
        description="Executes tasks assigned by an orchestrator; no spawn rights.",
        permissions=["tools:read"],
    ),
    can_orchestrate=False,
    can_broadcast=False,
    can_spawn_subagents=False,
)

#: Maps role_id → Role for quick lookup
REGISTRY: dict[str, Role] = {r.role_id: r for r in (ORCHESTRATOR, TEAM_MODE, WORKER)}


def get(role_id: str) -> Role:
    """Return a built-in Role by ID, or a default zero-capability Role for unknown IDs."""
    return REGISTRY.get(role_id, Role(role_id=role_id))

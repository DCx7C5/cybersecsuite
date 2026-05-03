"""Type definitions for permissions module."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from pathlib import Path

from .enums import Role, ScopeLevel, Permission


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

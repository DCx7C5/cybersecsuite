"""Permission grant, session scope, and cache ORM models."""

from datetime import UTC, datetime, timedelta
from fnmatch import fnmatch
from typing import Any

import msgspec
from tortoise import fields, models
from tortoise.expressions import Q

from .base import BaseModel
from .mixins import TimestampMixin


class PermissionGrantInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for one persisted permission grant."""

    id: int
    role: str
    scope_level: str
    scope_id: str
    path_permissions: list[str]
    tool_permissions: list[str]
    allow_all_tools: bool
    read_paths: list[str]
    write_paths: list[str]
    base_permissions: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ScopeSessionInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for session-scope TTL state."""

    id: int
    session_id: str
    scope_level: str
    parent_scope_id: str | None
    role: str
    expires_at: datetime | None
    auto_cleanup_at: datetime | None
    created_at: datetime
    updated_at: datetime


class RolePermissionCacheInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for cached resolved permissions."""

    id: int
    role: str
    scope_level: str
    cache_key: str
    permissions: dict[str, Any]
    expires_at: datetime
    created_at: datetime


class PermissionGrantManager:
    """Query helpers for ``PermissionGrant``."""

    async def for_role(self, role: str) -> list["PermissionGrant"]:
        return await PermissionGrant.filter(role=role).order_by("scope_level", "scope_id", "id")

    async def by_scope(self, scope_level: str, scope_id: str) -> list["PermissionGrant"]:
        return await PermissionGrant.filter(
            scope_level=scope_level,
            scope_id=scope_id,
        ).order_by("role", "id")

    async def get_grant(
        self,
        *,
        role: str,
        scope_level: str,
        scope_id: str,
    ) -> "PermissionGrant | None":
        return await PermissionGrant.get_or_none(
            role=role,
            scope_level=scope_level,
            scope_id=scope_id,
        )


class ScopeSessionManager:
    """Query helpers for ``ScopeSession``."""

    async def active(self) -> list["ScopeSession"]:
        now = datetime.now(UTC)
        return await ScopeSession.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gte=now),
        ).order_by("session_id", "id")

    async def for_role(self, role: str) -> list["ScopeSession"]:
        return await ScopeSession.filter(role=role).order_by("session_id", "id")

    async def expiring_before(self, when: datetime) -> list["ScopeSession"]:
        return await ScopeSession.filter(
            expires_at__not_isnull=True,
            expires_at__lte=when,
        ).order_by("expires_at", "id")


class RolePermissionCacheManager:
    """Query helpers for ``RolePermissionCache``."""

    async def by_key(self, cache_key: str) -> "RolePermissionCache | None":
        return await RolePermissionCache.get_or_none(cache_key=cache_key)

    async def valid(self, *, role: str, scope_level: str) -> list["RolePermissionCache"]:
        now = datetime.now(UTC)
        return await RolePermissionCache.filter(
            role=role,
            scope_level=scope_level,
            expires_at__gt=now,
        ).order_by("expires_at", "id")


class PermissionGrant(BaseModel, TimestampMixin):
    """Permission grant mapping role to tool and path permissions at one scope."""

    role = fields.CharField(max_length=64, db_index=True)
    scope_level = fields.CharField(max_length=32, db_index=True)
    scope_id = fields.CharField(max_length=255, db_index=True)
    path_permissions = fields.JSONField(default=list)
    tool_permissions = fields.JSONField(default=list)
    allow_all_tools = fields.BooleanField(default=False)
    read_paths = fields.JSONField(default=list)
    write_paths = fields.JSONField(default=list)
    base_permissions = fields.JSONField(default=dict)

    manager = PermissionGrantManager()

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "permission_grants"
        ordering = ["scope_level", "scope_id", "role", "id"]
        unique_together = (("role", "scope_level", "scope_id"),)
        indexes = [
            models.Index(fields=["role", "scope_level"]),
            models.Index(fields=["scope_level", "scope_id"]),
        ]

    def to_domain(self) -> PermissionGrantInfo:
        return PermissionGrantInfo(
            id=self.id,
            role=self.role,
            scope_level=self.scope_level,
            scope_id=self.scope_id,
            path_permissions=list(self.path_permissions or []),
            tool_permissions=list(self.tool_permissions or []),
            allow_all_tools=self.allow_all_tools,
            read_paths=list(self.read_paths or []),
            write_paths=list(self.write_paths or []),
            base_permissions=dict(self.base_permissions or {}),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: PermissionGrantInfo) -> "PermissionGrant":
        return cls(
            role=info.role,
            scope_level=info.scope_level,
            scope_id=info.scope_id,
            path_permissions=list(info.path_permissions),
            tool_permissions=list(info.tool_permissions),
            allow_all_tools=info.allow_all_tools,
            read_paths=list(info.read_paths),
            write_paths=list(info.write_paths),
            base_permissions=dict(info.base_permissions),
        )

    def allows_tool(self, tool_id: str) -> bool:
        if self.allow_all_tools:
            return True
        return tool_id in set(str(tool) for tool in self.tool_permissions or [])

    def grant_tool(self, tool_id: str) -> bool:
        tools = [str(tool) for tool in self.tool_permissions or []]
        if tool_id in tools:
            return False
        self.tool_permissions = [*tools, tool_id]
        return True

    def revoke_tool(self, tool_id: str) -> bool:
        tools = [str(tool) for tool in self.tool_permissions or []]
        if tool_id not in tools:
            return False
        self.tool_permissions = [tool for tool in tools if tool != tool_id]
        return True

    def has_path_permission(self, path: str, action: str) -> bool:
        """Check if grant allows filesystem action on path."""

        allowed_paths = self.read_paths if action == "read" else self.write_paths
        for pattern in allowed_paths or []:
            if fnmatch(path, pattern) or fnmatch(path, pattern + "/*"):
                return True
        return False

    def grant_path(self, path: str, action: str) -> bool:
        attr = "read_paths" if action == "read" else "write_paths"
        existing = [str(item) for item in getattr(self, attr) or []]
        if path in existing:
            return False
        setattr(self, attr, [*existing, path])
        return True

    def revoke_path(self, path: str, action: str) -> bool:
        attr = "read_paths" if action == "read" else "write_paths"
        existing = [str(item) for item in getattr(self, attr) or []]
        if path not in existing:
            return False
        setattr(self, attr, [item for item in existing if item != path])
        return True

    def has_base_permission(self, permission_name: str) -> bool:
        return bool((self.base_permissions or {}).get(permission_name))

    def set_base_permission(self, permission_name: str, value: Any) -> None:
        permissions = dict(self.base_permissions or {})
        permissions[permission_name] = value
        self.base_permissions = permissions


class ScopeSession(BaseModel, TimestampMixin):
    """Session scope tracking for TTL and auto-cleanup."""

    session_id = fields.CharField(max_length=255, unique=True, db_index=True)
    scope_level = fields.CharField(max_length=32, db_index=True)
    parent_scope_id = fields.CharField(max_length=255, null=True)
    role = fields.CharField(max_length=64, db_index=True)
    expires_at = fields.DatetimeField(null=True)
    auto_cleanup_at = fields.DatetimeField(null=True)

    manager = ScopeSessionManager()

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "scope_sessions"
        ordering = ["session_id", "id"]
        unique_together = (("session_id", "scope_level"),)
        indexes = [
            models.Index(fields=["role", "scope_level"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["auto_cleanup_at"]),
        ]

    def to_domain(self) -> ScopeSessionInfo:
        return ScopeSessionInfo(
            id=self.id,
            session_id=self.session_id,
            scope_level=self.scope_level,
            parent_scope_id=self.parent_scope_id,
            role=self.role,
            expires_at=self.expires_at,
            auto_cleanup_at=self.auto_cleanup_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: ScopeSessionInfo) -> "ScopeSession":
        return cls(
            session_id=info.session_id,
            scope_level=info.scope_level,
            parent_scope_id=info.parent_scope_id,
            role=info.role,
            expires_at=info.expires_at,
            auto_cleanup_at=info.auto_cleanup_at,
        )

    def is_expired(self, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        return self.expires_at <= (now or datetime.now(UTC))

    async def extend(self, ttl_seconds: int) -> None:
        now = datetime.now(UTC)
        current = self.expires_at if self.expires_at and self.expires_at > now else now
        await self.save_changes(
            expires_at=current + timedelta(seconds=max(0, ttl_seconds)),
            updated_at=now,
        )

    async def schedule_cleanup(self, ttl_seconds: int) -> None:
        now = datetime.now(UTC)
        await self.save_changes(
            auto_cleanup_at=now + timedelta(seconds=max(0, ttl_seconds)),
            updated_at=now,
        )


class RolePermissionCache(BaseModel):
    """Cache computed role permissions for performance."""

    role = fields.CharField(max_length=64, db_index=True)
    scope_level = fields.CharField(max_length=32, db_index=True)
    cache_key = fields.CharField(max_length=512, unique=True)
    permissions = fields.JSONField(default=dict)
    expires_at = fields.DatetimeField(db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    manager = RolePermissionCacheManager()

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "role_permission_cache"
        ordering = ["expires_at", "id"]
        unique_together = (("role", "scope_level", "cache_key"),)
        indexes = [
            models.Index(fields=["role", "scope_level"]),
            models.Index(fields=["expires_at"]),
        ]

    def to_domain(self) -> RolePermissionCacheInfo:
        return RolePermissionCacheInfo(
            id=self.id,
            role=self.role,
            scope_level=self.scope_level,
            cache_key=self.cache_key,
            permissions=dict(self.permissions or {}),
            expires_at=self.expires_at,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, info: RolePermissionCacheInfo) -> "RolePermissionCache":
        return cls(
            role=info.role,
            scope_level=info.scope_level,
            cache_key=info.cache_key,
            permissions=dict(info.permissions),
            expires_at=info.expires_at,
        )

    def is_expired(self, now: datetime | None = None) -> bool:
        return self.expires_at <= (now or datetime.now(UTC))

    async def refresh(self, permissions: dict[str, Any], ttl_seconds: int) -> None:
        now = datetime.now(UTC)
        await self.save_changes(
            permissions=dict(permissions),
            expires_at=now + timedelta(seconds=max(0, ttl_seconds)),
        )

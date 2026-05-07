"""Database models for permissions module."""

from tortoise import fields
from tortoise.models import Model


class PermissionGrant(Model):
    """Permission grant mapping role to permissions at scope level."""

    id = fields.BigIntField(primary_key=True)
    role = fields.CharField(max_length=32)
    scope_level = fields.CharField(max_length=32)
    scope_id = fields.CharField(max_length=255)
    path_permissions = fields.JSONField(default=list)
    tool_permissions = fields.JSONField(default=list)
    allow_all_tools = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "permission_grants"
        unique_together = (("role", "scope_level", "scope_id"),)


class ScopeSession(Model):
    """Session scope tracking for TTL and auto-cleanup."""

    id = fields.BigIntField(primary_key=True)
    session_id = fields.CharField(max_length=255, unique=True, db_index=True)
    scope_level = fields.CharField(max_length=32)
    parent_scope_id = fields.CharField(max_length=255, null=True)
    role = fields.CharField(max_length=32)
    created_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField(null=True)
    auto_cleanup_at = fields.DatetimeField(null=True)

    class Meta:
        table = "scope_sessions"


class RolePermissionCache(Model):
    """Cache computed role permissions for performance."""

    id = fields.BigIntField(primary_key=True)
    role = fields.CharField(max_length=32)
    scope_level = fields.CharField(max_length=32)
    cache_key = fields.CharField(max_length=512, unique=True)
    permissions = fields.JSONField()
    expires_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "role_permission_cache"


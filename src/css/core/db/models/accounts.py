"""Core accounts models — user, profile, organization management with RBAC.

Models:
- Account: User account with identity (email, username, created_at)
- UserProfile: Extended user info (name, avatar, preferences)
- Organization: Multi-tenant organization
- OrganizationMembership: User roles within org (owner, admin, member, viewer)
- RoleAssignment: Bind Account to Role at Organization scope

Integrated with core/roles for RBAC enforcement via path permissions.
"""

from datetime import datetime

import msgspec
from tortoise import fields, models

from css.core.db.models.base import BaseModel
from css.core.enums import Role
from .mixins import TimestampMixin
from fields import LabelField, NameField, UrlField, DescriptionField, SlugField


class AccountInfo(msgspec.Struct):
    """Domain value type for account data."""
    id: int
    username: str
    email: str
    is_active: bool
    is_verified: bool
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime


class Account(BaseModel, TimestampMixin):
    """User account — identity record for authentication."""

    username = NameField(max_length=128, unique=True, db_index=True)
    email = fields.CharField(max_length=255, unique=True, db_index=True)
    password_hash = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True, db_index=True)
    is_verified = fields.BooleanField(default=False)
    last_login = fields.DatetimeField(null=True)

    def to_domain(self) -> AccountInfo:
        return AccountInfo(
            id=self.id,
            username=self.username,
            email=self.email,
            is_active=self.is_active,
            is_verified=self.is_verified,
            last_login=self.last_login,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: AccountInfo) -> "Account":
        return cls(
            username=info.username,
            email=info.email,
            is_active=info.is_active,
            is_verified=info.is_verified,
            last_login=info.last_login,
        )

    class Meta:
        table = "account"
        table_verbose = "Account"
        table_verbose_plural = "Accounts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["username", "is_active"]),
            models.Index(fields=["email", "is_active"]),
        ]


class UserProfile(BaseModel, TimestampMixin):
    """Extended user profile information."""

    account: fields.ForeignKeyRelation[Account] = fields.ForeignKeyField(
        "css.Account",
        related_name="profile",
        on_delete=fields.CASCADE,
    )
    first_name = LabelField(null=True)
    last_name = LabelField(null=True)
    display_name = fields.CharField(max_length=255, null=True)
    avatar_url = UrlField(max_length=512, null=True)
    bio = DescriptionField(default="")
    phone = fields.CharField(max_length=20, null=True)
    timezone = fields.CharField(max_length=50, default="UTC")
    preferences = fields.JSONField(default=dict)  # UI theme, notifications, etc.

    class Meta:
        table = "user_profile"
        table_verbose = "User Profile"
        table_verbose_plural = "User Profiles"


class OrganizationInfo(msgspec.Struct):
    """Domain value type for organization data."""
    id: int
    name: str
    slug: str
    description: str
    logo_url: str | None
    max_members: int
    is_active: bool
    tier: str
    metadata: dict
    created_at: datetime
    updated_at: datetime


class Organization(BaseModel, TimestampMixin):
    """Multi-tenant organization container."""

    name = NameField(max_length=255, db_index=True)
    slug = SlugField(max_length=128, unique=True, db_index=True)
    description = DescriptionField(default="")
    logo_url = UrlField(max_length=512, null=True)

    # Org settings
    max_members = fields.IntField(default=100)
    is_active = fields.BooleanField(default=True, db_index=True)
    tier = fields.CharField(
        max_length=32,
        default="free",
        choices=["free", "pro", "enterprise"],
    )

    # Metadata
    metadata = fields.JSONField(default=dict)

    def to_domain(self) -> OrganizationInfo:
        return OrganizationInfo(
            id=self.id,
            name=self.name,
            slug=self.slug,
            description=self.description,
            logo_url=self.logo_url,
            max_members=self.max_members,
            is_active=self.is_active,
            tier=self.tier,
            metadata=self.metadata or {},
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: OrganizationInfo) -> "Organization":
        return cls(
            name=info.name,
            slug=info.slug,
            description=info.description,
            logo_url=info.logo_url,
            max_members=info.max_members,
            is_active=info.is_active,
            tier=info.tier,
            metadata=info.metadata,
        )

    class Meta:
        table = "organizations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug", "is_active"]),
        ]


class OrganizationMembership(BaseModel):
    """User membership in organization with role assignment."""

    organization: fields.ForeignKeyRelation[Organization] = fields.ForeignKeyField(
        "css.Organization",
        related_name="memberships",
        on_delete=fields.CASCADE,
    )
    account: fields.ForeignKeyRelation[Account] = fields.ForeignKeyField(
        "css.Account",
        related_name="org_memberships",
        on_delete=fields.CASCADE,
    )

    # Role assignment within org
    role = fields.CharEnumField(
        Role,
        max_length=32,
        default="member",
        db_index=True,
    )

    # Permissions at org scope (bound via core.roles module)
    permissions = fields.JSONField(default=list)

    # Metadata
    invited_by: fields.ForeignKeyRelation[Account] = fields.ForeignKeyField(
        "css.Account",
        related_name="invitations_sent",
        on_delete=fields.SET_NULL,
        null=True,
    )
    joined_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "organization_memberships"
        unique_together = (("organization", "account"),)
        indexes = [
            models.Index(fields=["organization", "role"]),
            models.Index(fields=["account", "role"]),
        ]


class RoleAssignment(BaseModel, TimestampMixin):
    """Bind Account to Role at Organization scope (for core.roles RBAC)."""

    account: fields.ForeignKeyRelation[Account] = fields.ForeignKeyField(
        "css.Account",
        related_name="role_assignments",
        on_delete=fields.CASCADE,
    )
    organization: fields.ForeignKeyRelation[Organization] = fields.ForeignKeyField(
        "css.Organization",
        related_name="role_assignments",
        on_delete=fields.CASCADE,
    )

    # Role from core.roles (e.g., "planner", "orchestrator", "team-mode")
    role_id = fields.CharField(max_length=64, db_index=True)

    # Scope level (global, team, agent)
    scope_level = fields.CharField(
        max_length=32,
        default="team",
        choices=["global", "team", "agent"],
    )
    scope_id = fields.CharField(max_length=255, null=True)  # Team/agent ID if applicable

    # Activation
    is_active = fields.BooleanField(default=True)
    activated_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField(null=True)  # Optional time-bound role

    class Meta:
        table = "role_assignments"
        unique_together = (("account", "organization", "role_id", "scope_level", "scope_id"),)
        indexes = [
            models.Index(fields=["account", "is_active"]),
            models.Index(fields=["organization", "role_id"]),
        ]


__all__ = [
    "Account",
    "UserProfile",
    "Organization",
    "OrganizationMembership",
    "RoleAssignment",
]

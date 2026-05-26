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
from tortoise import fields
from tortoise.indexes import Index

from css.core.db.models.base import BaseModel
from css.core.db.fields import (
    DescriptionField,
    LabelField,
    NameField,
    SlugField,
    UrlField,
)
from css.core.enums import Role

from .mixins import TimestampMixin


class AccountInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for account data."""
    id: int
    username: str
    email: str
    is_active: bool
    is_verified: bool
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime


class UserProfileInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for user profile data."""

    id: int
    account_id: int
    first_name: str | None
    last_name: str | None
    display_name: str | None
    avatar_url: str | None
    bio: str
    phone: str | None
    timezone: str
    preferences: dict
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

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "account"
        table_verbose = "Account"
        table_verbose_plural = "Accounts"
        ordering = ["-created_at"]
        indexes = [
            Index(fields=["username", "is_active"]),
            Index(fields=["email", "is_active"]),
        ]


class UserProfile(BaseModel, TimestampMixin):
    """Extended user profile information."""

    account: fields.ForeignKeyRelation[Account] = fields.ForeignKeyField(
        "models.Account",
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

    def to_domain(self) -> UserProfileInfo:
        return UserProfileInfo(
            id=self.id,
            account_id=self.account_id,
            first_name=self.first_name,
            last_name=self.last_name,
            display_name=self.display_name,
            avatar_url=self.avatar_url,
            bio=self.bio,
            phone=self.phone,
            timezone=self.timezone,
            preferences=dict(self.preferences or {}),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: UserProfileInfo) -> "UserProfile":
        return cls(
            account_id=info.account_id,
            first_name=info.first_name,
            last_name=info.last_name,
            display_name=info.display_name,
            avatar_url=info.avatar_url,
            bio=info.bio,
            phone=info.phone,
            timezone=info.timezone,
            preferences=dict(info.preferences),
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "user_profile"
        table_verbose = "User Profile"
        table_verbose_plural = "User Profiles"


class OrganizationInfo(msgspec.Struct, frozen=True, kw_only=True):
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


class OrganizationMembershipInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for organization membership data."""

    id: int
    organization_id: int
    account_id: int
    role: str
    permissions: list
    invited_by_id: int | None
    joined_at: datetime
    updated_at: datetime


class RoleAssignmentInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for role assignment data."""

    id: int
    account_id: int
    organization_id: int
    role_id: str
    scope_level: str
    scope_id: str | None
    is_active: bool
    activated_at: datetime
    expires_at: datetime | None
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

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "organizations"
        ordering = ["-created_at"]
        indexes = [
            Index(fields=["slug", "is_active"]),
        ]


class OrganizationMembership(BaseModel):
    """User membership in organization with role assignment."""

    organization: fields.ForeignKeyRelation[Organization] = fields.ForeignKeyField(
        "models.Organization",
        related_name="memberships",
        on_delete=fields.CASCADE,
    )
    account: fields.ForeignKeyRelation[Account] = fields.ForeignKeyField(
        "models.Account",
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
        "models.Account",
        related_name="invitations_sent",
        on_delete=fields.SET_NULL,
        null=True,
    )
    joined_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def to_domain(self) -> OrganizationMembershipInfo:
        return OrganizationMembershipInfo(
            id=self.id,
            organization_id=self.organization_id,
            account_id=self.account_id,
            role=self.role.value if hasattr(self.role, "value") else str(self.role),
            permissions=list(self.permissions or []),
            invited_by_id=self.invited_by_id,
            joined_at=self.joined_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: OrganizationMembershipInfo) -> "OrganizationMembership":
        return cls(
            organization_id=info.organization_id,
            account_id=info.account_id,
            role=info.role,
            permissions=list(info.permissions),
            invited_by_id=info.invited_by_id,
            joined_at=info.joined_at,
            updated_at=info.updated_at,
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "organization_memberships"
        unique_together = (("organization_id", "account_id"),)
        indexes = [
            Index(fields=["organization_id", "role"]),
            Index(fields=["account_id", "role"]),
        ]


class RoleAssignment(BaseModel, TimestampMixin):
    """Bind Account to Role at Organization scope (for core.roles RBAC)."""

    account: fields.ForeignKeyRelation[Account] = fields.ForeignKeyField(
        "models.Account",
        related_name="role_assignments",
        on_delete=fields.CASCADE,
    )
    organization: fields.ForeignKeyRelation[Organization] = fields.ForeignKeyField(
        "models.Organization",
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

    def to_domain(self) -> RoleAssignmentInfo:
        return RoleAssignmentInfo(
            id=self.id,
            account_id=self.account_id,
            organization_id=self.organization_id,
            role_id=self.role_id,
            scope_level=self.scope_level,
            scope_id=self.scope_id,
            is_active=self.is_active,
            activated_at=self.activated_at,
            expires_at=self.expires_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: RoleAssignmentInfo) -> "RoleAssignment":
        return cls(
            account_id=info.account_id,
            organization_id=info.organization_id,
            role_id=info.role_id,
            scope_level=info.scope_level,
            scope_id=info.scope_id,
            is_active=info.is_active,
            activated_at=info.activated_at,
            expires_at=info.expires_at,
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "role_assignments"
        unique_together = (("account_id", "organization_id", "role_id", "scope_level", "scope_id"),)
        indexes = [
            Index(fields=["account_id", "is_active"]),
            Index(fields=["organization_id", "role_id"]),
        ]


__all__ = [
    "Account",
    "UserProfile",
    "Organization",
    "OrganizationMembership",
    "RoleAssignment",
]

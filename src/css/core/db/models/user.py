"""Internal user/admin runtime identity ORM model and query helpers.

This surface is for internal/admin runtime identity and optional API-key helpers.
Tenant-facing registration/profile/organization flows remain on the Account surface.
"""

from typing import override
from datetime import UTC, datetime

import msgspec
from tortoise import fields
from tortoise.indexes import Index

from css.core.db.serializers import BaseModelSerializer
from .base import BaseUserModel
from .enums import UserRoles


class UserInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for user data."""

    id: int
    username: str
    roles: list[str]
    is_active: bool
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime


class UserManager:
    """Query helpers for ``User``."""

    async def active(self) -> list["User"]:
        return await User.filter(is_active=True).order_by("username", "id")

    async def by_username(self, username: str) -> "User | None":
        return await User.get_or_none(username=username)

    async def by_api_key_hash(self, api_key_hash: str) -> "User | None":
        return await User.get_or_none(api_key_hash=api_key_hash)

    async def by_role(self, role: UserRoles | str) -> list["User"]:
        role_value = role.value if isinstance(role, UserRoles) else str(role)
        users = await User.all().order_by("username", "id")
        return [user for user in users if user.has_role(role_value)]


class User(BaseUserModel):
    """Internal user/admin runtime identity with roles and optional API-key access."""

    hashed_password = fields.CharField(max_length=255)
    api_key_hash = fields.CharField(max_length=255, null=True, db_index=True)
    roles = fields.JSONField(default=list)
    is_active = fields.BooleanField(default=True, db_index=True)
    last_login = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    manager = UserManager()

    def to_domain(self) -> UserInfo:
        return UserInfo(
            id=self.id,
            username=self.username,
            roles=self.role_values,
            is_active=self.is_active,
            last_login=self.last_login,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: UserInfo) -> "User":
        return cls(
            username=info.username,
            roles=list(info.roles),
            is_active=info.is_active,
            last_login=info.last_login,
        )

    @property
    def role_values(self) -> list[str]:
        if not isinstance(self.roles, list):
            return []
        return [str(role) for role in self.roles]

    def has_role(self, role: UserRoles | str) -> bool:
        role_value = role.value if isinstance(role, UserRoles) else str(role)
        return role_value in self.role_values

    def set_roles(self, roles: list[UserRoles | str]) -> None:
        self.roles = [
            role.value if isinstance(role, UserRoles) else str(role)
            for role in roles
        ]

    def add_role(self, role: UserRoles | str) -> bool:
        role_value = role.value if isinstance(role, UserRoles) else str(role)
        if self.has_role(role_value):
            return False
        self.roles = [*self.role_values, role_value]
        return True

    def remove_role(self, role: UserRoles | str) -> bool:
        role_value = role.value if isinstance(role, UserRoles) else str(role)
        if not self.has_role(role_value):
            return False
        self.roles = [existing for existing in self.role_values if existing != role_value]
        return True

    async def mark_login(self, when: datetime | None = None) -> None:
        await self.save_changes(
            last_login=when or datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def activate(self) -> None:
        await self.save_changes(is_active=True, updated_at=datetime.now(UTC))

    async def deactivate(self) -> None:
        await self.save_changes(is_active=False, updated_at=datetime.now(UTC))

    async def set_api_key_hash(self, api_key_hash: str | None) -> None:
        await self.save_changes(api_key_hash=api_key_hash, updated_at=datetime.now(UTC))

    @property
    def has_api_key(self) -> bool:
        return bool(self.api_key_hash)

    @property
    def is_admin(self) -> bool:
        return self.has_role(UserRoles.ADMIN)

    @property
    def is_user(self) -> bool:
        return self.has_role(UserRoles.USER)

    @property
    def is_guest(self) -> bool:
        return self.has_role(UserRoles.GUEST)

    @property
    def is_authenticated(self) -> bool:
        return self.is_active and self.last_login is not None

    @property
    def is_anonymous(self) -> bool:
        return not self.is_authenticated

    @property
    def is_staff(self) -> bool:
        return self.is_admin

    @property
    def is_superuser(self) -> bool:
        return self.is_admin

    @override
    def __str__(self) -> str:
        return f"User({self.username})"

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "users"
        ordering = ["username", "id"]
        indexes = [
            Index(fields=["username"]),
            Index(fields=["is_active", "username"]),
            Index(fields=["api_key_hash"]),
        ]

class UserSerializer(BaseModelSerializer[User]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = User
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

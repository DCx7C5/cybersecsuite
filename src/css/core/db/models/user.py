"""Account ORM models — user accounts and authentication."""

from datetime import datetime

import msgspec
from tortoise import fields
from tortoise.indexes import Index

from css.core.db.models.base import BaseModel
from css.core.db.models.enums import UserRoles


class UserInfo(msgspec.Struct):
    """Domain value type for user data."""
    id: int
    username: str
    roles: list
    is_active: bool
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime


class User(BaseModel):
    """User account ORM model.
    
    Represents internal system users with authentication and authorization.
    
    Fields:
        id: Primary key (auto-generated BigInt)
        email: Unique email address
        hashed_password: Bcrypt-hashed password
        api_key_hash: SHA256 hash of API key (nullable, for programmatic access)
        roles: JSON array of role IDs/names
        is_active: Whether user account is enabled
        last_login: Last authentication timestamp
        created_at: Account creation timestamp
        updated_at: Last modification timestamp
    """

    username = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255)
    api_key_hash = fields.CharField(max_length=255, null=True)
    roles = fields.CharEnumField(enum_type=UserRoles, default=[])
    is_active = fields.BooleanField(default=True)
    last_login = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def to_domain(self) -> UserInfo:
        return UserInfo(
            id=self.id,
            username=self.username,
            roles=list(self.roles) if hasattr(self.roles, '__iter__') else [],
            is_active=self.is_active,
            last_login=self.last_login,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: UserInfo) -> "User":
        return cls(
            username=info.username,
            is_active=info.is_active,
            last_login=info.last_login,
        )

    class Meta:
        table = "users"
        indexes = (
            Index(fields=["username"]),
            Index(fields=["api_key_hash"]),
        )
        ordering = ["id"]
        unique_together = (
            ("username", "api_key_hash"),
            ("username", "is_active"),
            ("api_key_hash", "is_active"),
            ("username", "api_key_hash", "is_active"),
        )

    def __str__(self) -> str:
        return f"User({self.username})"

    @property
    def is_admin(self) -> bool:
        return UserRoles.ADMIN in self.roles

    @property
    def is_user(self) -> bool:
        return UserRoles.USER in self.roles

    @property
    def is_guest(self) -> bool:
        return UserRoles.GUEST in self.roles

    @property
    def is_authenticated(self) -> bool:
        return self.is_active and self.last_login is not None

    @property
    def is_anonymous(self) -> bool:
        return not self.is_active or self.last_login is None

    @property
    def is_superuser(self) -> bool:
        return self.is_admin or self.is_user or self.is_guest

    @property
    def is_staff(self) -> bool:
        return self.is_admin or self.is_user or self.is_guest

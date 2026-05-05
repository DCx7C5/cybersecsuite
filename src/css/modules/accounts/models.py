"""Account ORM models — user accounts and authentication."""

from tortoise import fields
from tortoise.models import Model


class User(Model):
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

    id = fields.BigIntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255)
    api_key_hash = fields.CharField(max_length=255, null=True)
    roles = fields.JSONField(default=list)
    is_active = fields.BooleanField(default=True)
    last_login = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"
        indexes = [
            ("email", "is_active"),  # Composite index for active user lookup
        ]

    def __str__(self) -> str:
        return f"User({self.email})"

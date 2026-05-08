"""Shared abstract base model for Tortoise ORM entities."""
from tortoise.fields import BigIntField, DatetimeField
from tortoise.models import Model

from css.core.db.fields import DescriptionField, NameField, SHA512SumField, VersionField


# MIXINS

class TimestampMixin:
    """Mixin for timestamps."""
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class VersionMixin:
    """Mixin for versioning."""
    version = VersionField(max_length=8, default="0.1.0")
    remote_hash = SHA512SumField(null=True)
    local_hash = SHA512SumField(null=True)

    class Meta:
        abstract = True


class BaseFrontmatterMixin:
    """Mixin for Frontmatter Objects"""

    name = NameField()
    description = DescriptionField(max_length=512)


# BASEMODEL

class BaseModel(Model):
    """Canonical ORM base class for the project."""

    id = BigIntField(primary_key=True)

    class Meta:
        abstract = True


class BaseItemModel(BaseModel):
    """Abstract base model for items with name and description."""

    name = NameField()
    description = DescriptionField(max_length=512)

    class Meta:
        abstract = True


class BaseUserModel(BaseModel):
    """Abstract base model for user-related entities."""

    username = NameField()

    class Meta:
        abstract = True

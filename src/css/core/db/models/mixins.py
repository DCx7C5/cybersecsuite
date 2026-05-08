from tortoise.fields import DatetimeField

from ..fields import DescriptionField, NameField, SHA512SumField, VersionField


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

    name = NameField(max_length=128)
    description = DescriptionField(max_length=512)

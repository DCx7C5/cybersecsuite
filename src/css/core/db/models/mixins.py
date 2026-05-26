from tortoise.fields import BooleanField, DatetimeField

from ..fields import (
    DescriptionField,
    NameField,
    SHA512SumField,
    VersionField,
)


class TimestampMixin:
    """Mixin for timestamps."""
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True


class VersionMixin:
    """Mixin for versioning."""
    version = VersionField(max_length=8, default="0.1.0")
    remote_hash = SHA512SumField(null=True)
    local_hash = SHA512SumField(null=True)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True


class SoftDeleteMixin:
    """Mixin for soft-delete support.

    Provides ``is_active`` boolean flag and nullable ``deleted_at`` timestamp.
    Call ``await instance.soft_delete()`` to mark a row as deleted without
    removing it from the database.
    """

    is_active = BooleanField(default=True, db_index=True)
    deleted_at = DatetimeField(null=True)

    async def soft_delete(self) -> None:
        """Mark this row as soft-deleted."""
        self.is_active = False
        self.deleted_at = DatetimeField.get_now()
        await self.save()

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True


class BaseFrontmatterMixin:
    """Mixin for Frontmatter Objects"""

    name = NameField(max_length=128)
    description = DescriptionField(max_length=512)

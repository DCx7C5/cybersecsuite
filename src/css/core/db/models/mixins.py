"""Reusable ORM mixins for cross-cutting concerns like timestamps, versioning, and deletion."""

from datetime import UTC, datetime

from tortoise import fields
from tortoise.fields import BooleanField, DatetimeField

from css.core.db.fields import DescriptionField, NameField, SHA512SumField, VersionField


class AuditTrailMixin:
    """Mixin for audit trail timestamps.

    Provides ``created_at`` and ``updated_at`` fields tracking record lifecycle.
    """

    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True


class TimestampMixin(AuditTrailMixin):
    """Compatibility alias for AuditTrailMixin.

    Use AuditTrailMixin for new code; this alias is kept for backward compatibility
    with existing model imports.
    """

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True


class VersionMixin:
    """Mixin for versioning and content hashing.

    Provides ``version`` (semantic version string), ``remote_hash`` and ``local_hash``
    (SHA512 checksums).
    """

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
        """Mark this row as soft-deleted.

        Sets is_active=False and deleted_at to current UTC time, persists deterministically.
        """
        self.is_active = False
        self.deleted_at = datetime.now(UTC)
        await self.save(update_fields=["is_active", "deleted_at"])  # type: ignore[reportAttributeAccessIssue]

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True


class BaseFrontmatterMixin:
    """Mixin for frontmatter metadata (name and description).

    Provides human-readable ``name`` and ``description`` fields for documentation
    and display purposes.
    """

    name = NameField(max_length=128)
    description = DescriptionField(max_length=512)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True


class TenantScopeMixin:
    """Mixin for scope binding (project/session/runtime).

    Extracted from ScopedEntry to provide reusable scope-binding fields and helpers.
    Allows records to be bound to project, session, or runtime scopes.

    Note: Concrete classes must inherit from BaseModel to access apply_updates/save_changes.
    """

    project = fields.ForeignKeyField(
        "models.ProjectScope",
        related_name=False,
        null=True,
        on_delete=fields.CASCADE,
        db_index=True,
    )
    session = fields.ForeignKeyField(
        "models.SessionScope",
        related_name=False,
        null=True,
        on_delete=fields.CASCADE,
        db_index=True,
    )
    runtime_id = fields.CharField(
        max_length=64,
        null=True,
        db_index=True,
        description="Container/pod runtime identity for runtime-bound scopes",
    )
    worktree_path = fields.CharField(
        max_length=1024,
        null=True,
        description="Absolute path to the runtime worktree for this record",
    )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True


class OwnershipMixin:
    """Mixin for ownership tracking.

    Abstract placeholder for future ownership/creator tracking across ORM models.
    Not yet integrated into concrete models; semantics vary by use case.
    """

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True


class LifecycleStatusMixin:
    """Mixin for lifecycle status tracking.

    Abstract placeholder for future lifecycle state machines (draft/published/archived/etc).
    Not yet integrated into concrete models; status enums and transitions vary by use case.
    """

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True


class OrderedTreeMixin:
    """Mixin for deterministic tree ordering.

    Provides helpers for ordered traversal within tree hierarchies.
    Used by concrete tree models (MenuItem, etc.) to maintain stable ordering.
    """

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True

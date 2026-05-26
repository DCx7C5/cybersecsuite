"""Tortoise ORM models for memory persistence."""

from tortoise import fields, models

from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin
from css.core.memory import (
    MemoryScope,
    MemoryTier,
    MemoryEntryKind,
    MemoryEntry,
    MemorySnapshot,
)


class MemoryEntryRecord(BaseModel, TimestampMixin):
    """Persisted memory entry."""

    entry_id = fields.CharField(max_length=128, unique=True, db_index=True)
    session_id = fields.CharField(max_length=128, db_index=True)
    agent_id = fields.CharField(max_length=128, null=True, db_index=True)
    scope = fields.CharEnumField(MemoryScope, default=MemoryScope.SESSION)
    tier = fields.CharEnumField(MemoryTier, default=MemoryTier.HOT)
    kind = fields.CharEnumField(MemoryEntryKind, default=MemoryEntryKind.NOTE)
    content = fields.TextField()
    metadata = fields.JSONField(default=dict)
    importance = fields.FloatField(default=0.5, db_index=True)
    persistent = fields.BooleanField(default=True, db_index=True)
    ttl_seconds = fields.IntField(null=True)
    expires_at = fields.DatetimeField(null=True, db_index=True)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "memory_entry"
        table_description = "Persistent memory entries across sessions and agents"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["session_id", "created_at"]),
            models.Index(fields=["agent_id", "created_at"]),
            models.Index(fields=["scope", "tier", "kind"]),
            models.Index(fields=["session_id", "persistent", "created_at"]),
            models.Index(fields=["session_id", "expires_at"]),
        ]

    def to_struct(self) -> MemoryEntry:
        """Convert ORM record to immutable memory value type."""
        return MemoryEntry(
            entry_id=self.entry_id,
            session_id=self.session_id,
            agent_id=self.agent_id,
            scope=self.scope,
            tier=self.tier,
            kind=self.kind,
            content=self.content,
            metadata=self.metadata or {},
            importance=self.importance,
            persistent=self.persistent,
            ttl_seconds=self.ttl_seconds,
            expires_at=self.expires_at.isoformat() if self.expires_at else None,
            created_at=self.created_at.isoformat() if self.created_at else "",
        )


class MemorySnapshotRecord(BaseModel, TimestampMixin):
    """Persisted snapshot for rollback and replay."""

    snapshot_id = fields.CharField(max_length=128, unique=True, db_index=True)
    session_id = fields.CharField(max_length=128, db_index=True)
    summary = fields.TextField()
    entries = fields.JSONField(default=list)
    metadata = fields.JSONField(default=dict)
    schema_version = fields.CharField(max_length=16, default="v2", db_index=True)
    entry_count = fields.IntField(default=0)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "memory_snapshot"
        table_description = "Session memory snapshots for rollback and replay"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["session_id", "created_at"])]

    def to_struct(self) -> MemorySnapshot:
        """Convert ORM record to immutable snapshot value type."""
        return MemorySnapshot(
            snapshot_id=self.snapshot_id,
            session_id=self.session_id,
            summary=self.summary,
            entries=self.entries or [],
            metadata=self.metadata or {},
            created_at=self.created_at.isoformat() if self.created_at else "",
        )

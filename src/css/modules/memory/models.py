"""Tortoise ORM models for memory persistence."""

from tortoise import fields, models
from tortoise.models import Model

from .enums import MemoryEntryKind, MemoryScope, MemoryTier
from .types import MemoryEntry, MemorySnapshot


class MemoryEntryRecord(Model):
    """Persisted memory entry."""

    id = fields.BigIntField(primary_key=True)
    entry_id = fields.CharField(max_length=128, unique=True, db_index=True)
    session_id = fields.CharField(max_length=128, db_index=True)
    agent_id = fields.CharField(max_length=128, null=True, db_index=True)
    scope = fields.CharEnumField(MemoryScope, default=MemoryScope.SESSION)
    tier = fields.CharEnumField(MemoryTier, default=MemoryTier.HOT)
    kind = fields.CharEnumField(MemoryEntryKind, default=MemoryEntryKind.NOTE)
    content = fields.TextField()
    metadata = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "memory_entry"
        table_description = "Persistent memory entries across sessions and agents"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["session_id", "created_at"]),
            models.Index(fields=["agent_id", "created_at"]),
            models.Index(fields=["scope", "tier", "kind"]),
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
            created_at=self.created_at.isoformat() if self.created_at else "",
        )


class MemorySnapshotRecord(Model):
    """Persisted snapshot for rollback and replay."""

    id = fields.BigIntField(primary_key=True)
    snapshot_id = fields.CharField(max_length=128, unique=True, db_index=True)
    session_id = fields.CharField(max_length=128, db_index=True)
    summary = fields.TextField()
    entries = fields.JSONField(default=list)
    metadata = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
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

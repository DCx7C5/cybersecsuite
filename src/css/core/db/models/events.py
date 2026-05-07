"""Tortoise ORM model for persisting DomainEvents."""

from tortoise import fields
from tortoise.models import Model
from datetime import datetime


class DomainEventRecord(Model):
    """Persistent domain event record in PostgreSQL.

    Denormalized from DomainEvent struct for efficient querying.
    """

    id = fields.TextField(pk=True)
    kind = fields.CharField(max_length=100, index=True)
    aggregate_type = fields.CharField(max_length=100, index=True)
    aggregate_id = fields.CharField(max_length=255, index=True)
    version = fields.IntField(default=1)
    timestamp = fields.DatetimeField(index=True)
    data = fields.JSONField(default=dict)
    metadata = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "domain_events"
        indexes = [
            ("aggregate_type", "aggregate_id"),
            ("kind", "timestamp"),
            ("timestamp",),
        ]

    @classmethod
    async def from_domain_event(cls, event) -> "DomainEventRecord":
        """Create ORM record from DomainEvent struct."""
        return cls(
            id=event.id,
            kind=event.kind,
            aggregate_type=event.aggregate_type,
            aggregate_id=event.aggregate_id,
            version=event.version,
            timestamp=event.timestamp,
            data=event.data,
            metadata=event.metadata,
        )

    async def append_to_store(self, store) -> None:
        """Save to DB and in-memory store."""
        await self.save()

        # Also append to in-memory store for current session
        from css.modules.events import DomainEvent

        event = DomainEvent(
            id=self.id,
            kind=self.kind,
            aggregate_type=self.aggregate_type,
            aggregate_id=self.aggregate_id,
            version=self.version,
            timestamp=self.timestamp,
            data=self.data,
            metadata=self.metadata,
        )
        store.append(event)


__all__ = ["DomainEventRecord"]

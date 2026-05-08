"""Tortoise ORM model for persisting DomainEvents."""

from tortoise import fields
from tortoise.indexes import Index

from css.core.db.models.base import BaseModel


class DomainEventRecord(BaseModel):
    """Persistent domain event record in PostgreSQL.

    Denormalized from DomainEvent struct for efficient querying.
    """

    kind = fields.CharField(max_length=100, index=True)
    aggregate_type = fields.CharField(max_length=100, index=True)
    aggregate_id = fields.CharField(max_length=255, index=True)
    version = fields.IntField(default=1)
    timestamp = fields.DatetimeField(index=True)
    data = fields.JSONField(default=dict)
    metadata = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "domain_event_record"
        table_verbose = "Domain Event Record"
        table_verbose_plural = "Domain Event Records"

        indexes = ([
            Index(fields=["kind", "aggregate_type", "aggregate_id"]),
            Index(fields=["version", "timestamp"]),
        ])
        unique_together = (
            ("kind", "aggregate_type", "aggregate_id"),
        )



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
        from css.core.events import DomainEvent

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

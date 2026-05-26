"""Persistent event-store records for DomainEvent values."""

from datetime import datetime
from typing import Any

import msgspec
from tortoise import fields, models

from css.core.events.domain_event import DomainEvent

from .base import BaseModel


class DomainEventRecordInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for one persisted event-store row."""

    id: int
    event_id: str
    kind: str
    aggregate_type: str
    aggregate_id: str
    version: int
    timestamp: datetime
    data: dict[str, Any]
    metadata: dict[str, Any]
    created_at: datetime


class DomainEventRecordManager:
    """Query helpers for ``DomainEventRecord``."""

    async def by_aggregate(
        self,
        *,
        aggregate_type: str,
        aggregate_id: str,
    ) -> list["DomainEventRecord"]:
        return await DomainEventRecord.filter(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
        ).order_by("timestamp", "id")

    async def by_kind(self, kind: str) -> list["DomainEventRecord"]:
        return await DomainEventRecord.filter(kind=kind).order_by("timestamp", "id")

    async def recent(self, limit: int = 100) -> list["DomainEventRecord"]:
        return await DomainEventRecord.all().order_by("-timestamp", "-id").limit(limit)

    async def by_event_id(self, event_id: str) -> "DomainEventRecord | None":
        return await DomainEventRecord.get_or_none(event_id=event_id)


class DomainEventRecord(BaseModel):
    """Persistent domain event record in PostgreSQL."""

    event_id = fields.CharField(max_length=64, unique=True, db_index=True)
    kind = fields.CharField(max_length=100, db_index=True)
    aggregate_type = fields.CharField(max_length=100, db_index=True)
    aggregate_id = fields.CharField(max_length=255, db_index=True)
    version = fields.IntField(default=1)
    timestamp = fields.DatetimeField(db_index=True)
    data = fields.JSONField(default=dict)
    metadata = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)

    manager = DomainEventRecordManager()

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "domain_event_record"
        table_description_singular = "Domain Event Record"
        table_description_plural = "Domain Event Records"
        ordering = ["timestamp", "id"]
        indexes = [
            models.Index(fields=["kind", "aggregate_type", "aggregate_id"]),
            models.Index(fields=["aggregate_type", "aggregate_id", "timestamp"]),
            models.Index(fields=["timestamp"]),
        ]

    @property
    def event_key(self) -> str:
        return f"{self.aggregate_type}:{self.aggregate_id}:{self.event_id}"

    def to_domain(self) -> DomainEventRecordInfo:
        return DomainEventRecordInfo(
            id=self.id,
            event_id=self.event_id,
            kind=self.kind,
            aggregate_type=self.aggregate_type,
            aggregate_id=self.aggregate_id,
            version=self.version,
            timestamp=self.timestamp,
            data=dict(self.data or {}),
            metadata=dict(self.metadata or {}),
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, info: DomainEventRecordInfo) -> "DomainEventRecord":
        return cls(
            event_id=info.event_id,
            kind=info.kind,
            aggregate_type=info.aggregate_type,
            aggregate_id=info.aggregate_id,
            version=info.version,
            timestamp=info.timestamp,
            data=dict(info.data),
            metadata=dict(info.metadata),
            created_at=info.created_at,
        )

    def to_domain_event(self) -> DomainEvent:
        """Rehydrate the immutable DomainEvent value."""

        metadata = dict(self.metadata or {})
        metadata.setdefault("persisted_record_id", self.id)
        return DomainEvent(
            kind=self.kind,
            aggregate_type=self.aggregate_type,
            aggregate_id=self.aggregate_id,
            id=self.event_id,
            data=dict(self.data or {}),
            metadata=metadata,
            timestamp=self.timestamp,
            version=self.version,
        )

    @classmethod
    async def from_domain_event(cls, event: DomainEvent) -> "DomainEventRecord":
        """Create an unsaved ORM record from a DomainEvent."""

        metadata = dict(event.metadata or {})
        return cls(
            event_id=event.id,
            kind=event.kind,
            aggregate_type=event.aggregate_type,
            aggregate_id=event.aggregate_id,
            version=event.version,
            timestamp=event.timestamp,
            data=dict(event.data or {}),
            metadata=metadata,
        )

    async def append_to_store(self, store) -> None:
        """Save to DB and append the corresponding DomainEvent to the store."""

        await self.save()
        store.append(self.to_domain_event())

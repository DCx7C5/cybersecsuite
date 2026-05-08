"""Runtime and ORM models for cache entries."""

from datetime import UTC, datetime, timedelta

import msgspec
from tortoise import fields, models

from css.core.db.models.base import BaseModel


class CacheEntry(msgspec.Struct):
    """Runtime cache entry used by in-memory cache layers."""

    key: str
    value: object
    ttl_seconds: int | None = None
    created_at: datetime = msgspec.field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_expired(self) -> bool:
        if self.ttl_seconds is None or self.ttl_seconds <= 0:
            return False
        return datetime.now(UTC) >= self.created_at + timedelta(seconds=self.ttl_seconds)


class CacheStats(msgspec.Struct):
    """Runtime cache metrics counters."""

    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total


class CacheEntryModel(BaseModel):
    """Persistent cache entry with TTL expiration support."""

    cache_key = fields.CharField(max_length=512, unique=True, db_index=True)
    cache_value = fields.JSONField(default=dict)
    namespace = fields.CharField(max_length=128, default="default", db_index=True)
    ttl_seconds = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    expires_at = fields.DatetimeField(null=True, db_index=True)

    class Meta:
        table = "cache_entries"
        indexes = [
            models.Index(fields=["namespace", "expires_at"]),
            models.Index(fields=["cache_key", "expires_at"]),
            models.Index(fields=["expires_at"]),
        ]

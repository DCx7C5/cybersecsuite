"""Cache data models and types (hybrid: dataclasses + Tortoise ORM)."""

from dataclasses import dataclass, field
from typing import Any, Optional, Dict
from datetime import datetime

from tortoise import fields
from tortoise.models import Model


# ─── TORTOISE ORM MODELS (Database schema) ────────────────────────────

class CacheEntryModel(Model):
    """Persisted cache entry in database."""
    id = fields.BigIntField(primary_key=True)
    key = fields.CharField(max_length=512, db_index=True)
    value = fields.JSONField()
    ttl_seconds = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    namespace = fields.CharField(max_length=256, default="default", db_index=True)
    
    class Meta:
        table = "cache_entry"
        table_description = "Cached entries with TTL"
        indexes = [("namespace", "key")]


class CacheStatsModel(Model):
    """Cache operation statistics (persisted)."""
    id = fields.BigIntField(primary_key=True)
    namespace = fields.CharField(max_length=256, db_index=True, unique=True)
    hits = fields.BigIntField(default=0)
    misses = fields.BigIntField(default=0)
    sets = fields.BigIntField(default=0)
    deletes = fields.BigIntField(default=0)
    errors = fields.BigIntField(default=0)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "cache_stats"
        table_description = "Cache performance metrics"


# ─── IN-MEMORY DATACLASSES (Runtime models) ──────────────────────────

@dataclass
class CacheEntry:
    """In-memory cache entry (maps to CacheEntryModel)."""
    key: str
    value: Any
    ttl_seconds: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl_seconds is None:
            return False
        elapsed = (datetime.utcnow() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds


@dataclass
class CacheStats:
    """In-memory cache statistics (maps to CacheStatsModel)."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

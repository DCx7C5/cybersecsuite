"""Cache data models and types."""

from dataclasses import dataclass, field
from typing import Any, Optional, Dict
from datetime import datetime


@dataclass
class CacheEntry:
    """Represents a single cache entry."""
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
    """Cache operation statistics."""
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

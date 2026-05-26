from typing import Any

from css.core.cache.base import CacheBackend
from .exceptions import CacheExecutionError
from .models import CacheEntry
from ..logger import getLogger

logger = getLogger(__name__)


class L1MemoryCache(CacheBackend):
    """L1: In-memory asyncio-based cache (orchestrator-local)."""

    def __init__(self, namespace: str = "default", max_size: int = 1000):
        """Initialize L1 memory cache."""
        super().__init__(namespace)
        self.max_size = max_size
        self._cache: dict[str, CacheEntry] = {}

    async def get(self, key: str) -> Any | None:
        """Get value from memory cache."""
        try:
            full_key = self._make_key(key)
            if full_key not in self._cache:
                self.stats.misses += 1
                return None

            entry = self._cache[full_key]
            if entry.is_expired:
                del self._cache[full_key]
                self.stats.misses += 1
                return None

            self.stats.hits += 1
            return entry.value
        except Exception as e:
            logger.error(f"L1 cache get error: {e}")
            self.stats.errors += 1
            raise CacheExecutionError(f"L1 get failed: {e}", operation="get")

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> bool:
        """Set value in memory cache."""
        try:
            if len(self._cache) >= self.max_size:
                # Simple eviction: remove oldest entry
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
                del self._cache[oldest_key]

            full_key = self._make_key(key)
            self._cache[full_key] = CacheEntry(full_key, value, ttl_seconds)
            self.stats.sets += 1
            return True
        except Exception as e:
            logger.error(f"L1 cache set error: {e}")
            self.stats.errors += 1
            raise CacheExecutionError(f"L1 set failed: {e}", operation="set")

    async def delete(self, key: str) -> bool:
        """Delete value from memory cache."""
        try:
            full_key = self._make_key(key)
            if full_key in self._cache:
                del self._cache[full_key]
                self.stats.deletes += 1
                return True
            return False
        except Exception as e:
            logger.error(f"L1 cache delete error: {e}")
            self.stats.errors += 1
            raise CacheExecutionError(f"L1 delete failed: {e}", operation="delete")

    async def clear(self) -> bool:
        """Clear all memory cache entries."""
        try:
            self._cache.clear()
            return True
        except Exception as e:
            logger.error(f"L1 cache clear error: {e}")
            self.stats.errors += 1
            raise CacheExecutionError(f"L1 clear failed: {e}", operation="clear")

    async def exists(self, key: str) -> bool:
        """Check if key exists in memory cache."""
        try:
            full_key = self._make_key(key)
            if full_key not in self._cache:
                return False

            entry = self._cache[full_key]
            if entry.is_expired:
                del self._cache[full_key]
                return False

            return True
        except Exception as e:
            logger.error(f"L1 cache exists error: {e}")
            self.stats.errors += 1
            return False

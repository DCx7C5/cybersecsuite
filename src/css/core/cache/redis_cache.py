from typing import Any

from css.core.cache.base import CacheBackend
from css.core.logger import getLogger

logger = getLogger(__name__)


class L2RedisCache(CacheBackend):
    """L2: Redis-backed distributed cache (1-10ms)."""

    def __init__(self, namespace: str = "default", redis_url: str = "redis://localhost:6379"):
        """Initialize L2 Redis cache."""
        super().__init__(namespace)
        self.redis_url = redis_url
        self._redis = None

    async def _get_redis(self):
        """Lazy-load Redis connection."""
        if self._redis is None:
            try:
                import redis.asyncio as redis_asyncio

                self._redis = redis_asyncio.from_url(self.redis_url)
            except ImportError:
                logger.warning("redis.asyncio not installed; L2 cache unavailable")
                return None
        return self._redis

    async def get(self, key: str) -> Any | None:
        """Get value from Redis."""
        try:
            redis = await self._get_redis()
            if redis is None:
                return None

            full_key = self._make_key(key)
            value = await redis.get(full_key)

            if value is None:
                self.stats.misses += 1
                return None

            self.stats.hits += 1
            return value.decode() if isinstance(value, bytes) else value
        except Exception as e:
            logger.warning(f"L2 cache get error: {e}")
            self.stats.errors += 1
            return None

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> bool:
        """Set value in Redis."""
        try:
            redis = await self._get_redis()
            if redis is None:
                return False

            full_key = self._make_key(key)
            serialized = str(value).encode() if not isinstance(value, bytes) else value

            if ttl_seconds:
                await redis.set(full_key, serialized, ex=ttl_seconds)
            else:
                await redis.set(full_key, serialized)

            self.stats.sets += 1
            return True
        except Exception as e:
            logger.warning(f"L2 cache set error: {e}")
            self.stats.errors += 1
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from Redis."""
        try:
            redis = await self._get_redis()
            if redis is None:
                return False

            full_key = self._make_key(key)
            result = await redis.delete(full_key)

            if result:
                self.stats.deletes += 1
            return bool(result)
        except Exception as e:
            logger.warning(f"L2 cache delete error: {e}")
            self.stats.errors += 1
            return False

    async def clear(self) -> bool:
        """Clear all Redis entries in namespace."""
        try:
            redis = await self._get_redis()
            if redis is None:
                return False

            pattern = f"{self.namespace}:*"
            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)
            return True
        except Exception as e:
            logger.warning(f"L2 cache clear error: {e}")
            self.stats.errors += 1
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            redis = await self._get_redis()
            if redis is None:
                return False

            full_key = self._make_key(key)
            result = await redis.exists(full_key)
            return bool(result)
        except Exception as e:
            logger.warning(f"L2 cache exists error: {e}")
            self.stats.errors += 1
            return False

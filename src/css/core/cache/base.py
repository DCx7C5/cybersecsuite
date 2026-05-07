"""Abstract cache backend interface and implementations."""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

from .exceptions import CacheExecutionError, CacheSerializationError
from .models import CacheEntry, CacheStats

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    def __init__(self, namespace: str = "default"):
        """Initialize cache backend."""
        self.namespace = namespace
        self.stats = CacheStats()
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
    
    def _make_key(self, key: str) -> str:
        """Create namespaced cache key."""
        return f"{self.namespace}:{key}"
    
    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "namespace": self.namespace,
            "hits": self.stats.hits,
            "misses": self.stats.misses,
            "sets": self.stats.sets,
            "deletes": self.stats.deletes,
            "errors": self.stats.errors,
            "hit_rate": self.stats.hit_rate,
        }


class L1MemoryCache(CacheBackend):
    """L1: In-memory asyncio-based cache (orchestrator-local)."""
    
    def __init__(self, namespace: str = "default", max_size: int = 1000):
        """Initialize L1 memory cache."""
        super().__init__(namespace)
        self.max_size = max_size
        self._cache: dict[str, CacheEntry] = {}
    
    async def get(self, key: str) -> Optional[Any]:
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
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in memory cache."""
        try:
            if len(self._cache) >= self.max_size:
                # Simple eviction: remove oldest entry
                oldest_key = min(self._cache.keys(), 
                               key=lambda k: self._cache[k].created_at)
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
                import aioredis
                self._redis = await aioredis.create_redis_pool(self.redis_url)
            except ImportError:
                logger.warning("aioredis not installed; L2 cache unavailable")
                return None
        return self._redis
    
    async def get(self, key: str) -> Optional[Any]:
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
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in Redis."""
        try:
            redis = await self._get_redis()
            if redis is None:
                return False
            
            full_key = self._make_key(key)
            serialized = str(value).encode() if not isinstance(value, bytes) else value
            
            if ttl_seconds:
                await redis.setex(full_key, ttl_seconds, serialized)
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


class L3PostgresCache(CacheBackend):
    """L3: PostgreSQL-backed persistent cache via Tortoise ORM."""

    @staticmethod
    def _is_expired(ttl_seconds: Optional[int], created_at: datetime) -> bool:
        if ttl_seconds is None:
            return False
        now = datetime.now(UTC)
        created = created_at.astimezone(UTC) if created_at.tzinfo else created_at.replace(tzinfo=UTC)
        return (now - created).total_seconds() > ttl_seconds

    async def get(self, key: str) -> Optional[Any]:
        """Get value from PostgreSQL cache."""
        try:
            from .models import CacheEntryModel

            entry = await CacheEntryModel.filter(namespace=self.namespace, key=key).first()
            if entry is None:
                self.stats.misses += 1
                return None
            if self._is_expired(entry.ttl_seconds, entry.created_at):
                await entry.delete()
                self.stats.misses += 1
                return None
            self.stats.hits += 1
            return entry.value
        except Exception as e:
            logger.error(f"L3 cache get error: {e}")
            self.stats.errors += 1
            raise CacheExecutionError(f"L3 get failed: {e}", operation="get")

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in PostgreSQL cache."""
        try:
            from .models import CacheEntryModel

            await CacheEntryModel.update_or_create(
                defaults={"value": value, "ttl_seconds": ttl_seconds},
                namespace=self.namespace,
                key=key,
            )
            self.stats.sets += 1
            return True
        except Exception as e:
            logger.error(f"L3 cache set error: {e}")
            self.stats.errors += 1
            raise CacheExecutionError(f"L3 set failed: {e}", operation="set")

    async def delete(self, key: str) -> bool:
        """Delete value from PostgreSQL cache."""
        try:
            from .models import CacheEntryModel

            deleted = await CacheEntryModel.filter(namespace=self.namespace, key=key).delete()
            if deleted:
                self.stats.deletes += 1
            return bool(deleted)
        except Exception as e:
            logger.error(f"L3 cache delete error: {e}")
            self.stats.errors += 1
            raise CacheExecutionError(f"L3 delete failed: {e}", operation="delete")

    async def clear(self) -> bool:
        """Clear all entries in namespace from PostgreSQL cache."""
        try:
            from .models import CacheEntryModel

            await CacheEntryModel.filter(namespace=self.namespace).delete()
            return True
        except Exception as e:
            logger.error(f"L3 cache clear error: {e}")
            self.stats.errors += 1
            raise CacheExecutionError(f"L3 clear failed: {e}", operation="clear")

    async def exists(self, key: str) -> bool:
        """Check if key exists in PostgreSQL cache."""
        try:
            from .models import CacheEntryModel

            entry = await CacheEntryModel.filter(namespace=self.namespace, key=key).first()
            if entry is None:
                return False
            if self._is_expired(entry.ttl_seconds, entry.created_at):
                await entry.delete()
                return False
            return True
        except Exception as e:
            logger.error(f"L3 cache exists error: {e}")
            self.stats.errors += 1
            return False


class L4SQLiteCache(CacheBackend):
    """L4: SQLite disk-backed archive cache for fallback durability."""

    def __init__(self, namespace: str = "default", sqlite_path: str = "/tmp/css-cache/archive.sqlite"):
        super().__init__(namespace)
        self.sqlite_path = sqlite_path
        self._lock = asyncio.Lock()
        self._initialized = False

    async def _ensure_table(self) -> None:
        if self._initialized:
            return
        async with self._lock:
            if self._initialized:
                return
            try:
                import aiosqlite

                Path(self.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
                async with aiosqlite.connect(self.sqlite_path) as db:
                    await db.execute(
                        """
                        CREATE TABLE IF NOT EXISTS cache_archive (
                            namespace TEXT NOT NULL,
                            key TEXT NOT NULL,
                            value TEXT NOT NULL,
                            ttl_seconds INTEGER NULL,
                            created_at REAL NOT NULL,
                            PRIMARY KEY(namespace, key)
                        )
                        """
                    )
                    await db.execute(
                        "CREATE INDEX IF NOT EXISTS idx_cache_archive_ns_key ON cache_archive(namespace, key)"
                    )
                    await db.commit()
                self._initialized = True
            except Exception as e:
                raise CacheExecutionError(f"L4 initialize failed: {e}", operation="initialize") from e

    @staticmethod
    def _is_expired(ttl_seconds: Optional[int], created_at: float) -> bool:
        return ttl_seconds is not None and (time.time() - created_at) > ttl_seconds

    @staticmethod
    def _serialize(value: Any) -> str:
        try:
            return json.dumps(value)
        except TypeError as e:
            raise CacheSerializationError(str(e), data_type=type(value).__name__) from e

    @staticmethod
    def _deserialize(raw: str) -> Any:
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise CacheSerializationError(str(e), data_type="json") from e

    async def get(self, key: str) -> Optional[Any]:
        """Get value from SQLite archive cache."""
        await self._ensure_table()
        try:
            import aiosqlite

            async with aiosqlite.connect(self.sqlite_path) as db:
                async with db.execute(
                    "SELECT value, ttl_seconds, created_at FROM cache_archive WHERE namespace=? AND key=?",
                    (self.namespace, key),
                ) as cursor:
                    row = await cursor.fetchone()
                if row is None:
                    self.stats.misses += 1
                    return None
                value, ttl_seconds, created_at = row
                if self._is_expired(ttl_seconds, created_at):
                    await db.execute(
                        "DELETE FROM cache_archive WHERE namespace=? AND key=?",
                        (self.namespace, key),
                    )
                    await db.commit()
                    self.stats.misses += 1
                    return None
                self.stats.hits += 1
                return self._deserialize(value)
        except CacheSerializationError:
            self.stats.errors += 1
            raise
        except Exception as e:
            self.stats.errors += 1
            raise CacheExecutionError(f"L4 get failed: {e}", operation="get") from e

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in SQLite archive cache."""
        await self._ensure_table()
        try:
            import aiosqlite

            payload = self._serialize(value)
            async with aiosqlite.connect(self.sqlite_path) as db:
                await db.execute(
                    """
                    INSERT INTO cache_archive(namespace, key, value, ttl_seconds, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(namespace, key) DO UPDATE SET
                        value=excluded.value,
                        ttl_seconds=excluded.ttl_seconds,
                        created_at=excluded.created_at
                    """,
                    (self.namespace, key, payload, ttl_seconds, time.time()),
                )
                await db.commit()
            self.stats.sets += 1
            return True
        except CacheSerializationError:
            self.stats.errors += 1
            raise
        except Exception as e:
            self.stats.errors += 1
            raise CacheExecutionError(f"L4 set failed: {e}", operation="set") from e

    async def delete(self, key: str) -> bool:
        """Delete value from SQLite archive cache."""
        await self._ensure_table()
        try:
            import aiosqlite

            async with aiosqlite.connect(self.sqlite_path) as db:
                cursor = await db.execute(
                    "DELETE FROM cache_archive WHERE namespace=? AND key=?",
                    (self.namespace, key),
                )
                await db.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                self.stats.deletes += 1
            return deleted
        except Exception as e:
            self.stats.errors += 1
            raise CacheExecutionError(f"L4 delete failed: {e}", operation="delete") from e

    async def clear(self) -> bool:
        """Clear all entries in namespace from SQLite archive cache."""
        await self._ensure_table()
        try:
            import aiosqlite

            async with aiosqlite.connect(self.sqlite_path) as db:
                await db.execute("DELETE FROM cache_archive WHERE namespace=?", (self.namespace,))
                await db.commit()
            return True
        except Exception as e:
            self.stats.errors += 1
            raise CacheExecutionError(f"L4 clear failed: {e}", operation="clear") from e

    async def exists(self, key: str) -> bool:
        """Check if key exists in SQLite archive cache."""
        await self._ensure_table()
        try:
            import aiosqlite

            async with aiosqlite.connect(self.sqlite_path) as db:
                async with db.execute(
                    "SELECT ttl_seconds, created_at FROM cache_archive WHERE namespace=? AND key=?",
                    (self.namespace, key),
                ) as cursor:
                    row = await cursor.fetchone()
                if row is None:
                    return False
                ttl_seconds, created_at = row
                if self._is_expired(ttl_seconds, created_at):
                    await db.execute(
                        "DELETE FROM cache_archive WHERE namespace=? AND key=?",
                        (self.namespace, key),
                    )
                    await db.commit()
                    return False
                return True
        except Exception as e:
            logger.warning(f"L4 cache exists error: {e}")
            self.stats.errors += 1
            return False


class CacheDecorator:
    """Decorator for caching function results."""
    
    def __init__(self, cache: CacheBackend, ttl_seconds: Optional[int] = None):
        """Initialize cache decorator."""
        self.cache = cache
        self.ttl_seconds = ttl_seconds
    
    def __call__(self, func):
        """Decorate async function with caching."""
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and args
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await self.cache.set(cache_key, result, self.ttl_seconds)
            return result
        
        return wrapper

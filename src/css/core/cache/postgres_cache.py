from typing import Any

from datetime import UTC, datetime, timedelta

from css.core.cache.base import CacheBackend
from css.core.cache.exceptions import CacheExecutionError
from css.core.logger import getLogger

logger = getLogger(__name__)


class L3PostgresCache(CacheBackend):
    """L3: PostgreSQL-backed persistent cache via Tortoise ORM."""

    @staticmethod
    def _is_expired(expires_at: datetime | None) -> bool:
        if expires_at is None:
            return False
        now = datetime.now(UTC)
        expiry = expires_at.astimezone(UTC) if expires_at.tzinfo else expires_at.replace(tzinfo=UTC)
        return now > expiry

    async def get(self, key: str) -> Any | None:
        """Get value from PostgreSQL cache."""
        try:
            from .models import CacheEntryModel

            entry = await CacheEntryModel.filter(namespace=self.namespace, cache_key=self._make_key(key)).first()
            if entry is None:
                self.stats.misses += 1
                return None
            if self._is_expired(entry.expires_at):
                await entry.delete()
                self.stats.misses += 1
                return None
            self.stats.hits += 1
            return entry.cache_value
        except Exception as e:
            logger.error(f"L3 cache get error: {e}")
            self.stats.errors += 1
            raise CacheExecutionError(f"L3 get failed: {e}", operation="get")

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> bool:
        """Set value in PostgreSQL cache."""
        try:
            from .models import CacheEntryModel

            expires_at = None
            if ttl_seconds is not None and ttl_seconds > 0:
                expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)

            await CacheEntryModel.update_or_create(
                defaults={
                    "cache_value": value,
                    "ttl_seconds": ttl_seconds or 0,
                    "expires_at": expires_at,
                },
                namespace=self.namespace,
                cache_key=self._make_key(key),
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

            deleted = await CacheEntryModel.filter(namespace=self.namespace, cache_key=self._make_key(key)).delete()
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

            entry = await CacheEntryModel.filter(namespace=self.namespace, cache_key=self._make_key(key)).first()
            if entry is None:
                return False
            if self._is_expired(entry.expires_at):
                await entry.delete()
                return False
            return True
        except Exception as e:
            logger.error(f"L3 cache exists error: {e}")
            self.stats.errors += 1
            return False

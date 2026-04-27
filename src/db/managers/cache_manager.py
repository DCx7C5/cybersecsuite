"""
Scope-aware cache manager with hierarchical invalidation.

Implements:
- Cache keys include scope level: {scope_level}:{resource_id}:{key}
- cache_metadata table tracks parent scope references
- Child scopes invalidated when parent changes
- No orphaned cache entries after parent deletion
- Scope-aware cache invalidation cascade
"""
from __future__ import annotations

import logging
from typing import Any, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class CacheScope(str, Enum):
    """Cache scope levels matching ScopeLevel."""
    GLOBAL = "global"
    APP = "app"
    PROJECT = "project"
    RUNTIME = "runtime"
    SESSION = "session"


class CacheManager:
    """Scope-aware cache manager with hierarchical invalidation.

    Manages cache with scope hierarchy:
    - Cache keys include scope_level: f"{scope_level}:{resource_id}:{key}"
    - cache_metadata tracks scope_level and parent references
    - Invalidation cascades from parent to children
    - Automatic cleanup of orphaned entries
    """

    # Scope hierarchy for cascade invalidation
    SCOPE_HIERARCHY: list[CacheScope] = [
        CacheScope.GLOBAL,
        CacheScope.APP,
        CacheScope.PROJECT,
        CacheScope.RUNTIME,
        CacheScope.SESSION,
    ]

    def __init__(self, redis_url: Optional[str] = None) -> None:
        """Initialize cache manager.

        Args:
            redis_url: Optional Redis connection URL
        """
        self.redis_url = redis_url
        self._redis_client: Any = None
        self._cache: dict[str, Any] = {}  # In-memory fallback
        self._metadata: dict[str, dict[str, Any]] = {}  # Track scope metadata

    async def connect(self) -> None:
        """Connect to Redis if configured."""
        if self.redis_url:
            try:
                import redis.asyncio as redis
                self._redis_client = await redis.from_url(self.redis_url)
                logger.info("Connected to Redis cache")
            except Exception as exc:
                logger.warning(f"Failed to connect to Redis: {exc}, using in-memory cache")
                self._redis_client = None
        else:
            logger.info("Using in-memory cache")

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._redis_client:
            try:
                await self._redis_client.close()
                logger.info("Disconnected from Redis")
            except Exception as exc:
                logger.error(f"Error disconnecting from Redis: {exc}")

    def _make_cache_key(
        self,
        scope_level: str | CacheScope,
        resource_id: str | int,
        key: str,
    ) -> str:
        """Build cache key with scope hierarchy.

        Args:
            scope_level: Scope level
            resource_id: Resource ID
            key: Cache key

        Returns:
            Full cache key: {scope_level}:{resource_id}:{key}
        """
        if isinstance(scope_level, CacheScope):
            scope_level = scope_level.value
        return f"{scope_level}:{resource_id}:{key}"

    async def set(
        self,
        scope_level: str | CacheScope,
        resource_id: str | int,
        key: str,
        value: Any,
        ttl_seconds: int = 3600,
        parent_scope_id: Optional[str | int] = None,
    ) -> None:
        """Cache a value with scope metadata.

        Args:
            scope_level: Scope level
            resource_id: Resource ID in this scope
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds
            parent_scope_id: Parent scope ID (for hierarchy tracking)
        """
        cache_key = self._make_cache_key(scope_level, resource_id, key)

        # Store metadata
        self._metadata[cache_key] = {
            "scope_level": scope_level if isinstance(scope_level, str) else scope_level.value,
            "resource_id": str(resource_id),
            "parent_scope_id": str(parent_scope_id) if parent_scope_id else None,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat(),
            "ttl_seconds": ttl_seconds,
        }

        # Store to persistent cache
        if self._redis_client:
            try:
                await self._redis_client.setex(
                    cache_key,
                    ttl_seconds,
                    str(value),  # Redis stores strings
                )
                logger.debug(f"Cached {cache_key} in Redis (TTL: {ttl_seconds}s)")
            except Exception as exc:
                logger.error(f"Error setting Redis cache: {exc}")
                self._cache[cache_key] = value
        else:
            self._cache[cache_key] = value
            logger.debug(f"Cached {cache_key} in memory")

    async def get(
        self,
        scope_level: str | CacheScope,
        resource_id: str | int,
        key: str,
    ) -> Optional[Any]:
        """Retrieve a cached value.

        Args:
            scope_level: Scope level
            resource_id: Resource ID
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        cache_key = self._make_cache_key(scope_level, resource_id, key)

        # Check metadata for expiration
        metadata = self._metadata.get(cache_key)
        if metadata:
            if datetime.fromisoformat(metadata["expires_at"]) < datetime.utcnow():
                # Expired, delete it
                await self.delete(scope_level, resource_id, key)
                return None

        # Retrieve from persistent cache
        if self._redis_client:
            try:
                value = await self._redis_client.get(cache_key)
                if value:
                    logger.debug(f"Cache hit: {cache_key} from Redis")
                    return value.decode() if isinstance(value, bytes) else value
            except Exception as exc:
                logger.error(f"Error getting Redis cache: {exc}")

        # Fall back to in-memory
        if cache_key in self._cache:
            logger.debug(f"Cache hit: {cache_key} from memory")
            return self._cache[cache_key]

        logger.debug(f"Cache miss: {cache_key}")
        return None

    async def delete(
        self,
        scope_level: str | CacheScope,
        resource_id: str | int,
        key: str,
    ) -> None:
        """Delete a cached value.

        Args:
            scope_level: Scope level
            resource_id: Resource ID
            key: Cache key
        """
        cache_key = self._make_cache_key(scope_level, resource_id, key)

        # Remove metadata
        self._metadata.pop(cache_key, None)

        # Delete from persistent cache
        if self._redis_client:
            try:
                await self._redis_client.delete(cache_key)
                logger.debug(f"Deleted cache key from Redis: {cache_key}")
            except Exception as exc:
                logger.error(f"Error deleting Redis cache: {exc}")

        # Delete from in-memory
        self._cache.pop(cache_key, None)

    async def invalidate_by_scope(
        self,
        scope_level: str | CacheScope,
        resource_id: Optional[str | int] = None,
    ) -> int:
        """Invalidate cache for a scope and its children.

        Cascade invalidation: invalidating parent scope invalidates all children.

        Args:
            scope_level: Scope level to invalidate
            resource_id: Optional specific resource to invalidate

        Returns:
            Number of cache entries invalidated
        """
        if isinstance(scope_level, CacheScope):
            scope_level = scope_level.value

        deleted_count = 0

        # Find all cache keys that match this scope
        keys_to_delete = []
        for cache_key, metadata in self._metadata.items():
            if metadata["scope_level"] == scope_level:
                if resource_id is None or metadata["resource_id"] == str(resource_id):
                    keys_to_delete.append(cache_key)

        # Also delete child scope keys if parent is invalidated
        scope_hierarchy_idx = next(
            (i for i, s in enumerate(self.SCOPE_HIERARCHY) if s.value == scope_level),
            -1,
        )
        if scope_hierarchy_idx >= 0:
            # Get all descendant scopes
            descendant_scopes = [self.SCOPE_HIERARCHY[i].value for i in range(scope_hierarchy_idx + 1, len(self.SCOPE_HIERARCHY))]
            
            # Recursively find all descendants in the scope hierarchy
            parent_id = str(resource_id) if resource_id else None
            scope_queue = [(child_scope, parent_id) for child_scope in descendant_scopes]
            visited_keys = set(keys_to_delete)
            
            while scope_queue:
                current_scope, current_parent = scope_queue.pop(0)
                for cache_key, metadata in self._metadata.items():
                    if cache_key in visited_keys:
                        continue
                    if metadata["scope_level"] == current_scope:
                        # Check if this is a direct child of current parent
                        if metadata.get("parent_scope_id") == current_parent:
                            keys_to_delete.append(cache_key)
                            visited_keys.add(cache_key)
                            # This key's resource_id becomes parent for next level
                            next_scope_idx = next(
                                (i for i, s in enumerate(self.SCOPE_HIERARCHY) if s.value == current_scope),
                                -1,
                            )
                            if next_scope_idx >= 0 and next_scope_idx + 1 < len(self.SCOPE_HIERARCHY):
                                next_scope = self.SCOPE_HIERARCHY[next_scope_idx + 1].value
                                scope_queue.append((next_scope, str(metadata["resource_id"])))

        # Delete all identified keys
        for cache_key in keys_to_delete:
            try:
                # Remove metadata
                self._metadata.pop(cache_key, None)

                # Delete from persistent cache
                if self._redis_client:
                    try:
                        await self._redis_client.delete(cache_key)
                    except Exception as exc:
                        logger.error(f"Error deleting Redis key {cache_key}: {exc}")

                # Delete from in-memory
                self._cache.pop(cache_key, None)
                deleted_count += 1
            except Exception as exc:
                logger.error(f"Error invalidating cache key {cache_key}: {exc}")

        logger.info(f"Invalidated {deleted_count} cache entries for {scope_level}:{resource_id}")
        return deleted_count

    async def invalidate_by_parent(
        self,
        parent_scope_id: str | int,
    ) -> int:
        """Invalidate all child cache entries for a parent scope.

        Args:
            parent_scope_id: Parent scope ID

        Returns:
            Number of entries invalidated
        """
        parent_scope_id_str = str(parent_scope_id)
        deleted_count = 0

        keys_to_delete = []
        for cache_key, metadata in self._metadata.items():
            if metadata.get("parent_scope_id") == parent_scope_id_str:
                keys_to_delete.append(cache_key)

        # Delete all identified keys
        for cache_key in keys_to_delete:
            try:
                # Remove metadata
                self._metadata.pop(cache_key, None)

                # Delete from persistent cache
                if self._redis_client:
                    try:
                        await self._redis_client.delete(cache_key)
                    except Exception as exc:
                        logger.error(f"Error deleting Redis key {cache_key}: {exc}")

                # Delete from in-memory
                self._cache.pop(cache_key, None)
                deleted_count += 1
            except Exception as exc:
                logger.error(f"Error invalidating cache key {cache_key}: {exc}")

        logger.info(f"Invalidated {deleted_count} cache entries for parent {parent_scope_id}")
        return deleted_count

    async def cleanup_expired(self) -> int:
        """Clean up expired cache entries.

        Returns:
            Number of entries cleaned up
        """
        now = datetime.utcnow()
        keys_to_delete = []

        # Collect keys and their metadata before deleting
        for cache_key, metadata in self._metadata.items():
            expires_at = datetime.fromisoformat(metadata["expires_at"])
            if expires_at < now:
                keys_to_delete.append((cache_key, metadata))

        # Delete all expired keys
        for cache_key, metadata in keys_to_delete:
            try:
                await self.delete(
                    metadata["scope_level"],
                    metadata["resource_id"],
                    cache_key.split(":")[-1],
                )
            except Exception as exc:
                logger.error(f"Error cleaning up cache key {cache_key}: {exc}")

        logger.info(f"Cleaned up {len(keys_to_delete)} expired cache entries")
        return len(keys_to_delete)

    async def clear_all(self) -> None:
        """Clear all cache entries (use with caution)."""
        logger.warning("Clearing all cache entries")

        # Clear metadata
        self._metadata.clear()

        # Clear in-memory cache
        self._cache.clear()

        # Clear Redis
        if self._redis_client:
            try:
                await self._redis_client.flushdb()
                logger.info("Flushed Redis database")
            except Exception as exc:
                logger.error(f"Error flushing Redis: {exc}")

    def get_metadata(self, cache_key: str) -> Optional[dict[str, Any]]:
        """Get metadata for a cache key.

        Args:
            cache_key: Cache key

        Returns:
            Metadata dict or None
        """
        return self._metadata.get(cache_key)

    def get_all_metadata(self) -> dict[str, dict[str, Any]]:
        """Get all cache metadata.

        Returns:
            Dictionary of all cache metadata
        """
        return dict(self._metadata)

    def get_size(self) -> dict[str, int]:
        """Get cache sizes.

        Returns:
            Dict with 'memory', 'metadata', and 'total' sizes
        """
        return {
            "memory": len(self._cache),
            "metadata": len(self._metadata),
            "total": len(self._cache) + len(self._metadata),
        }


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager(redis_url: Optional[str] = None) -> CacheManager:
    """Get or create global cache manager instance.

    Args:
        redis_url: Optional Redis connection URL

    Returns:
        Global CacheManager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(redis_url=redis_url)
    return _cache_manager


async def init_cache_manager(redis_url: Optional[str] = None) -> CacheManager:
    """Initialize and connect global cache manager.

    Args:
        redis_url: Optional Redis connection URL

    Returns:
        Initialized CacheManager instance
    """
    manager = get_cache_manager(redis_url=redis_url)
    await manager.connect()
    return manager


async def shutdown_cache_manager() -> None:
    """Shutdown global cache manager."""
    if _cache_manager:
        await _cache_manager.disconnect()

"""Redis-backed exact-match prompt cache (Tier 1).

Provides O(1) cached LLM responses for identical input prompts across all providers.
Uses SHA256(messages + model + system_prompt) as cache key, stores complete response.
"""

import json
from typing import Any

from css.core.cache.redis_cache import L2RedisCache
from css.core.logger import getLogger
from css.core.types.base_messages import LLMResponse

logger = getLogger(__name__)


class ExactMatchPromptCache:
    """O(1) exact-match cache for LLM responses using Redis."""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        ttl_seconds: int = 86400,
        namespace: str = "prompt_cache:exact",
    ):
        """Initialize exact-match prompt cache backed by Redis.

        Args:
            redis_url: Redis connection string
            ttl_seconds: Cache TTL in seconds (default 24 hours)
            namespace: Redis namespace prefix for this cache
        """
        self.backend = L2RedisCache(namespace=namespace, redis_url=redis_url)
        self.ttl_seconds = ttl_seconds

    async def get(self, cache_key: str) -> LLMResponse | None:
        """Retrieve cached LLM response by exact-match key.

        Args:
            cache_key: SHA256 hash key from PromptCacheManager.compute_exact_match_key()

        Returns:
            LLMResponse if found, None if miss/error
        """
        try:
            raw = await self.backend.get(cache_key)
            if raw is None:
                return None

            data = json.loads(raw) if isinstance(raw, str) else raw
            logger.debug(f"Exact-match cache hit for key {cache_key[:16]}...")
            return LLMResponse(**data)
        except Exception as e:
            logger.warning(f"Exact-match cache get error: {e}")
            return None

    async def set(
        self,
        cache_key: str,
        response: LLMResponse,
    ) -> bool:
        """Store LLM response in exact-match cache.

        Args:
            cache_key: SHA256 hash key from PromptCacheManager.compute_exact_match_key()
            response: LLMResponse to cache

        Returns:
            True if stored, False on error
        """
        try:
            serialized = json.dumps(response.__dict__, default=str)
            success = await self.backend.set(
                cache_key,
                serialized,
                ttl_seconds=self.ttl_seconds,
            )
            if success:
                logger.debug(f"Exact-match cache stored for key {cache_key[:16]}...")
            return success
        except Exception as e:
            logger.warning(f"Exact-match cache set error: {e}")
            return False

    async def delete(self, cache_key: str) -> bool:
        """Invalidate cached response by key.

        Args:
            cache_key: Key to invalidate

        Returns:
            True if deleted, False if not found or error
        """
        try:
            return await self.backend.delete(cache_key)
        except Exception as e:
            logger.warning(f"Exact-match cache delete error: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all entries in this cache namespace.

        Returns:
            True if cleared, False on error
        """
        try:
            return await self.backend.clear()
        except Exception as e:
            logger.warning(f"Exact-match cache clear error: {e}")
            return False

    @property
    def stats(self):
        """Get cache statistics from underlying backend."""
        return self.backend.stats

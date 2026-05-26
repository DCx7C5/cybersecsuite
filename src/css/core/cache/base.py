"""Abstract cache backend interface and implementations."""

from css.core.logger import getLogger
from abc import ABC, abstractmethod
from typing import Any

from .models import CacheStats

logger = getLogger(__name__)


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    def __init__(self, namespace: str = "default"):
        """Initialize cache backend."""
        self.namespace = namespace
        self.stats = CacheStats()
    
    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> bool:
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




class CacheDecorator:
    """Decorator for caching function results."""
    
    def __init__(self, cache: CacheBackend, ttl_seconds: int | None = None):
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


def cache(cache: CacheBackend, ttl_seconds: int | None = None) -> CacheDecorator:
    """Decorator factory for caching function results."""
    return CacheDecorator(cache, ttl_seconds)

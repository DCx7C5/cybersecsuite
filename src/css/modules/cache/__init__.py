"""Unified L1-L4 caching layer."""

from css.core.logger import getLogger

from .base import CacheBackend, L1MemoryCache, L2RedisCache, L3PostgresCache, L4SQLiteCache, CacheDecorator
from .exceptions import BaseCacheException, CacheNotFoundError, CacheExecutionError, CacheSerializationError
from .models import CacheEntry, CacheStats

logger = getLogger(__name__)

__all__ = [
    # Backends
    'CacheBackend',
    'L1MemoryCache',
    'L2RedisCache',
    'L3PostgresCache',
    'L4SQLiteCache',
    'CacheDecorator',
    
    # Exceptions
    'BaseCacheException',
    'CacheNotFoundError',
    'CacheExecutionError',
    'CacheSerializationError',
    
    # Models
    'CacheEntry',
    'CacheStats',
]

logger.info("Cache module loaded")

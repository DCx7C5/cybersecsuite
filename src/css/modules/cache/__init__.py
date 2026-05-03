"""Unified L1-L4 caching layer."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .base import CacheBackend, L1MemoryCache, L2RedisCache, CacheDecorator
from .exceptions import BaseCacheException, CacheNotFoundError, CacheExecutionError, CacheSerializationError
from .models import CacheEntry, CacheStats

__all__ = [
    # Backends
    'CacheBackend',
    'L1MemoryCache',
    'L2RedisCache',
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

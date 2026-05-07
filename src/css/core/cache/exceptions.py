from css.core.exceptions import BaseModuleException

class BaseCacheException(BaseModuleException):
    """Base exception for the cache module."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module_name="cache", **kwargs)


class CacheNotFoundError(BaseCacheException):
    """Raised when cached item is not found."""
    
    def __init__(self, cache_key: str, **kwargs):
        ctx = kwargs.get("context", {})
        ctx["cache_key"] = cache_key
        super().__init__(
            f"Cache item not found: {cache_key}",
            context=ctx,
            **kwargs
        )


class CacheExecutionError(BaseCacheException):
    """Raised when cache operation fails."""
    
    def __init__(self, message: str = None, operation: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if operation:
            ctx["operation"] = operation
        super().__init__(
            message or f"Cache operation failed: {operation}" if operation else "Cache operation failed",
            context=ctx,
            **kwargs
        )


class CacheSerializationError(BaseCacheException):
    """Raised when cache serialization/deserialization fails."""
    
    def __init__(self, message: str = None, data_type: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if data_type:
            ctx["data_type"] = data_type
        super().__init__(
            message or f"Cache serialization failed: {data_type}" if data_type else "Cache serialization failed",
            context=ctx,
            **kwargs
        )

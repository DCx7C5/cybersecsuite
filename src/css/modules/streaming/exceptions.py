from css.core.exceptions import BaseModuleException

class BaseStreamingExceptions(BaseModuleException):
    """Base exception for the streaming module."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module_name="streaming", **kwargs)


class StreamingConnectionError(BaseStreamingExceptions):
    """Raised when streaming connection fails."""
    
    def __init__(self, message: str = None, endpoint: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if endpoint:
            ctx["endpoint"] = endpoint
        super().__init__(
            message or f"Streaming connection failed: {endpoint}" if endpoint else "Streaming connection failed",
            context=ctx,
            **kwargs
        )


class StreamingTimeoutError(BaseStreamingExceptions):
    """Raised when streaming times out."""
    
    def __init__(self, message: str = None, timeout_seconds: int = None, **kwargs):
        ctx = kwargs.get("context", {})
        if timeout_seconds:
            ctx["timeout_seconds"] = timeout_seconds
        super().__init__(
            message or f"Streaming timed out after {timeout_seconds}s" if timeout_seconds else "Streaming timed out",
            context=ctx,
            **kwargs
        )


class StreamBufferError(BaseStreamingExceptions):
    """Raised when stream buffer operations fail."""
    
    def __init__(self, message: str = None, buffer_size: int = None, **kwargs):
        ctx = kwargs.get("context", {})
        if buffer_size:
            ctx["buffer_size"] = buffer_size
        super().__init__(
            message or f"Stream buffer error (size={buffer_size})" if buffer_size else "Stream buffer error",
            context=ctx,
            **kwargs
        )

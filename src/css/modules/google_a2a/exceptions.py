from css.core.exceptions import BaseModuleException

class BaseA2AExceptions(BaseModuleException):
    """Base exception for the google_a2a module."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module_name="google_a2a", **kwargs)


class A2AAgentError(BaseA2AExceptions):
    """Raised when A2A agents operation fails."""
    
    def __init__(self, message: str = None, agent_name: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if agent_name:
            ctx["agents"] = agent_name
        super().__init__(
            message or f"A2A agents error: {agent_name}" if agent_name else "A2A agents error",
            context=ctx,
            **kwargs
        )


class A2ACommunicationError(BaseA2AExceptions):
    """Raised when A2A communication fails."""
    
    def __init__(self, message: str = None, endpoint: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if endpoint:
            ctx["endpoint"] = endpoint
        super().__init__(
            message or f"A2A communication failed: {endpoint}" if endpoint else "A2A communication failed",
            context=ctx,
            **kwargs
        )


class A2ATimeoutError(BaseA2AExceptions):
    """Raised when A2A operation times out."""
    
    def __init__(self, message: str = None, timeout_seconds: int = None, **kwargs):
        ctx = kwargs.get("context", {})
        if timeout_seconds:
            ctx["timeout_seconds"] = timeout_seconds
        super().__init__(
            message or f"A2A operation timed out after {timeout_seconds}s" if timeout_seconds else "A2A operation timed out",
            context=ctx,
            **kwargs
        )


class PauseRequestError(BaseA2AExceptions):
    """Raised when pause request fails."""
    
    def __init__(self, message: str = None, request_id: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if request_id:
            ctx["request_id"] = request_id
        super().__init__(
            message or f"Pause request failed for: {request_id}" if request_id else "Pause request failed",
            context=ctx,
            **kwargs
        )

"""Chat exceptions."""

from css.core.exceptions import BaseModuleException


class BaseChatException(BaseModuleException):
    """Base exception for the chat module."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module_name="chat", **kwargs)


class ChatSessionNotFoundError(BaseChatException):
    """Raised when chat session is not found."""
    def __init__(self, session_id: str, **kwargs):
        ctx = kwargs.get("context", {})
        ctx["session_id"] = session_id
        super().__init__(
            f"Chat session not found: {session_id}",
            context=ctx,
            **kwargs
        )


class ChatProcessingError(BaseChatException):
    """Raised when chat processing fails."""
    def __init__(self, message: str = None, **kwargs):
        super().__init__(
            message or "Chat processing failed",
            **kwargs
        )

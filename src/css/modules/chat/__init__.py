"""Backend layer for frontend chat with QoL injections."""

from css.core.logger import getLogger
from .manager import ChatSessionManager
from .models import ChatMessage, ChatSession
from .enums import ChatRole, ChatMessageType, ChatStatus
from .exceptions import (
    BaseChatException,
    ChatSessionNotFoundError,
    ChatProcessingError,
)

logger = getLogger(__name__)

__all__ = [
    # Manager
    "ChatSessionManager",
    
    # Models
    "ChatMessage",
    "ChatSession",
    
    # Enums
    "ChatRole",
    "ChatMessageType",
    "ChatStatus",
    
    # Exceptions
    "BaseChatException",
    "ChatSessionNotFoundError",
    "ChatProcessingError",
]

logger.info("Chat module loaded")

"""Backend layer for frontend chat with QoL injections."""

from .manager import ChatSessionManager
from .models import ChatMessage, ChatMessageModel, ChatSession, ChatSessionModel
from .enums import ChatRole, ChatMessageType, ChatStatus
from css.core.logger import getLogger
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
    "ChatSessionModel",
    "ChatMessageModel",
    
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

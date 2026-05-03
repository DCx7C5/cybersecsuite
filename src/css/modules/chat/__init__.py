"""Backend layer for frontend chat with QoL injections."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .manager import ChatSessionManager
from .models import ChatMessage, ChatSession
from .enums import ChatRole, ChatMessageType, ChatStatus
from .exceptions import (
    BaseChatException,
    ChatSessionNotFoundError,
    ChatProcessingError,
)

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

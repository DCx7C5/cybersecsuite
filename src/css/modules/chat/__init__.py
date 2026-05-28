"""Backend layer for frontend chat with QoL injections."""

from .manager import ChatSessionManager
from .models import ChatMessage, ChatMessageModel, ChatSession, ChatSessionModel
from .enums import ChatRole, ChatMessageType, ChatStatus
from css.core.logger import getLogger
from .endpoints import router
from .exceptions import (
    BaseChatException,
    ChatSessionNotFoundError,
    ChatProcessingError,
)

logger = getLogger(__name__)

logger.info("Chat module loaded")

"""Chat data models and types."""
import msgspec

from typing import Any
from datetime import datetime

from .enums import ChatRole, ChatMessageType, ChatStatus

@msgspec.struct
class ChatMessage:
    """Single chat message."""
    id: str
    role: ChatRole
    message_type: ChatMessageType
    content: str
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)
    created_at: datetime = msgspec.field(default_factory=datetime.utcnow)
    tokens: int = 0

@msgspec.struct
class ChatSession:
    """Chat session containing messages."""
    session_id: str
    title: str
    status: ChatStatus = ChatStatus.ACTIVE
    model_id: str | None = None
    system_prompt: str = ""
    messages: list[ChatMessage] = msgspec.field(default_factory=list)
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)
    created_at: datetime = msgspec.field(default_factory=datetime.utcnow)
    updated_at: datetime = msgspec.field(default_factory=datetime.utcnow)
    
    def add_message(self, message: ChatMessage) -> None:
        """Add message to session."""
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def get_messages_for_api(self) -> list[dict[str, Any]]:
        """Get messages in API-ready format."""
        result = []
        
        if self.system_prompt:
            result.append({
                "role": ChatRole.SYSTEM.value,
                "content": self.system_prompt
            })
        
        for msg in self.messages:
            result.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        return result

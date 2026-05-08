"""Chat data models and types."""

from datetime import datetime

import msgspec
from tortoise import fields, models
from tortoise.models import Model

from css.core.db.models.base import BaseModel

from .enums import ChatRole, ChatMessageType, ChatStatus

@msgspec.struct
class ChatMessage:
    """Single chat message."""
    id: str
    role: ChatRole
    message_type: ChatMessageType
    content: str
    metadata: dict[str, object] = msgspec.field(default_factory=dict)
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
    metadata: dict[str, object] = msgspec.field(default_factory=dict)
    created_at: datetime = msgspec.field(default_factory=datetime.utcnow)
    updated_at: datetime = msgspec.field(default_factory=datetime.utcnow)
    
    def add_message(self, message: ChatMessage) -> None:
        """Add message to session."""
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def get_messages_for_api(self) -> list[dict[str, str]]:
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


class ChatSessionModel(BaseModel):
    """Persistent chat session row."""

    session_uuid = fields.CharField(max_length=128, unique=True, db_index=True)
    project: fields.ForeignKeyNullableRelation[Model] = fields.ForeignKeyField(
        "css.ProjectScope",
        related_name="chat_sessions",
        null=True,
        on_delete=fields.SET_NULL,
    )
    title = fields.CharField(max_length=512, default="")
    status = fields.CharEnumField(ChatStatus, default=ChatStatus.ACTIVE, db_index=True)
    model_id = fields.CharField(max_length=256, null=True, db_index=True)
    provider_slug = fields.CharField(max_length=64, null=True, db_index=True)
    system_prompt = fields.TextField(default="")
    message_count = fields.IntField(default=0)
    total_tokens = fields.IntField(default=0)
    extra_meta = fields.JSONField(default=dict)
    is_active = fields.BooleanField(default=True, db_index=True)
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "chat_session"
        table_description = "Persisted chat sessions"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["status", "updated_at"]),
            models.Index(fields=["model_id", "provider_slug"]),
        ]


class ChatMessageModel(BaseModel):
    """Persistent chat message row."""

    chat_session: fields.ForeignKeyRelation[ChatSessionModel] = fields.ForeignKeyField(
        "css.ChatSessionModel",
        related_name="messages",
        on_delete=fields.CASCADE,
    )
    message_uuid = fields.CharField(max_length=128, unique=True, db_index=True)
    role = fields.CharEnumField(ChatRole, db_index=True)
    message_type = fields.CharEnumField(ChatMessageType, default=ChatMessageType.TEXT)
    content = fields.TextField()
    tokens = fields.IntField(default=0)
    extra_meta = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True, db_index=True)

    class Meta:
        table = "chat_message"
        table_description = "Persisted chat messages"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["chat_session", "role"]),
            models.Index(fields=["chat_session", "created_at"]),
        ]

"""Tortoise models for durable chat session persistence."""

from tortoise import fields
from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin


class ChatSessionRecord(BaseModel, TimestampMixin):
    """Persistent chat session record."""

    session_id = fields.CharField(max_length=64, unique=True, db_index=True)
    title = fields.CharField(max_length=255)
    status = fields.CharField(max_length=32, default="active", db_index=True)
    model_id = fields.CharField(max_length=128, null=True)
    system_prompt = fields.TextField(default="")
    metadata = fields.JSONField(default=dict)
    class Meta:
        table = "chat_sessions"


class ChatMessageRecord(BaseModel):
    """Persistent chat message record."""

    message_id = fields.CharField(max_length=64, unique=True, db_index=True)
    session: fields.ForeignKeyRelation[ChatSessionRecord] = fields.ForeignKeyField(
        "css.ChatSessionRecord",
        related_name="messages",
        on_delete=fields.CASCADE,
    )
    role = fields.CharField(max_length=32)
    message_type = fields.CharField(max_length=32, default="text")
    content = fields.TextField()
    metadata = fields.JSONField(default=dict)
    tokens = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chat_messages"
        indexes = [("session_id", "created_at")]

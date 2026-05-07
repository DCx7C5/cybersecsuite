"""Chat handler and session management."""

import uuid
from datetime import datetime
from typing import Any

from . import getLogger
from .models import ChatMessage, ChatSession
from .enums import ChatRole, ChatMessageType, ChatStatus
from .exceptions import ChatSessionNotFoundError

logger = getLogger(__name__)



class ChatSessionManager:
    """Manages chat sessions and messages."""
    
    def __init__(self):
        """Initialize chat session manager."""
        self._sessions: dict[str, ChatSession] = {}
    
    async def create_session(self, title: str = "New Chat", system_prompt: str = "") -> ChatSession:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        
        session = ChatSession(
            session_id=session_id,
            title=title,
            system_prompt=system_prompt
        )
        
        self._sessions[session_id] = session
        await self._persist_session(session)
        logger.info(f"Created chat session: {session_id}")
        
        return session
    
    async def get_session(self, session_id: str) -> ChatSession | None:
        """Get chat session by ID."""
        cached = self._sessions.get(session_id)
        if cached:
            return cached
        return await self._load_session_from_db(session_id)
    
    async def get_session_or_fail(self, session_id: str) -> ChatSession:
        """Get chat session or raise error."""
        session = await self.get_session(session_id)
        if not session:
            raise ChatSessionNotFoundError(session_id)
        return session
    
    async def add_message(
        self,
        session_id: str,
        role: ChatRole,
        content: str,
        message_type: ChatMessageType = ChatMessageType.TEXT,
    ) -> ChatMessage:
        """Add message to session."""
        session = await self.get_session_or_fail(session_id)
        
        message = ChatMessage(
            id=str(uuid.uuid4()),
            role=role,
            message_type=message_type,
            content=content
        )
        
        session.add_message(message)
        await self._persist_message(session_id, message)
        logger.debug(f"Added message to session {session_id}: {role.value}")
        
        return message
    
    async def get_session_messages(self, session_id: str) -> list[ChatMessage]:
        """Get all messages in a session."""
        session = await self.get_session_or_fail(session_id)
        return session.messages
    
    async def list_sessions(self, status: ChatStatus = None) -> list[ChatSession]:
        """List chat sessions with optional filtering."""
        if not self._sessions:
            await self._load_recent_sessions()
        sessions = list(self._sessions.values())
        
        if status:
            sessions = [s for s in sessions if s.status == status]
        
        return sorted(sessions, key=lambda s: s.created_at, reverse=True)
    
    async def update_session_status(self, session_id: str, status: ChatStatus) -> None:
        """Update session status."""
        session = await self.get_session_or_fail(session_id)
        session.status = status
        session.updated_at = datetime.utcnow()
        await self._persist_session(session)
        logger.debug(f"Updated session {session_id} status: {status.value}")
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
        await self._delete_session_record(session_id)
        logger.info(f"Deleted chat session: {session_id}")
        return True
    
    def get_stats(self) -> dict[str, Any]:
        """Get chat statistics."""
        total_sessions = len(self._sessions)
        total_messages = sum(len(s.messages) for s in self._sessions.values())
        
        by_status = {}
        for session in self._sessions.values():
            status_key = session.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "by_status": by_status,
            "avg_messages_per_session": (total_messages / total_sessions) if total_sessions > 0 else 0,
        }

    async def _persist_session(self, session: ChatSession) -> None:
        from .persistence_models import ChatSessionRecord

        record = await ChatSessionRecord.get_or_none(session_id=session.session_id)
        payload = {
            "title": session.title,
            "status": session.status.value,
            "model_id": session.model_id,
            "system_prompt": session.system_prompt,
            "metadata": session.metadata,
            "updated_at": session.updated_at,
        }
        if record:
            await record.update_from_dict(payload).save()
            return

        await ChatSessionRecord.create(
            session_id=session.session_id,
            created_at=session.created_at,
            **payload,
        )

    async def _persist_message(self, session_id: str, message: ChatMessage) -> None:
        from .persistence_models import ChatSessionRecord, ChatMessageRecord

        session_record = await ChatSessionRecord.get_or_none(session_id=session_id)
        if not session_record:
            raise ChatSessionNotFoundError(session_id)

        await ChatMessageRecord.create(
            message_id=message.id,
            session_id=session_record.id,
            role=message.role.value,
            message_type=message.message_type.value,
            content=message.content,
            metadata=message.metadata,
            tokens=message.tokens,
            created_at=message.created_at,
        )

    async def _load_session_from_db(self, session_id: str) -> ChatSession | None:
        from .persistence_models import ChatSessionRecord, ChatMessageRecord

        session_record = await ChatSessionRecord.get_or_none(session_id=session_id)
        if not session_record:
            return None

        message_records = await ChatMessageRecord.filter(session_id=session_record.id).order_by("created_at")
        session = ChatSession(
            session_id=session_record.session_id,
            title=session_record.title,
            status=ChatStatus(session_record.status),
            model_id=session_record.model_id,
            system_prompt=session_record.system_prompt,
            metadata=session_record.metadata,
            created_at=session_record.created_at,
            updated_at=session_record.updated_at,
            messages=[
                ChatMessage(
                    id=msg.message_id,
                    role=ChatRole(msg.role),
                    message_type=ChatMessageType(msg.message_type),
                    content=msg.content,
                    metadata=msg.metadata,
                    created_at=msg.created_at,
                    tokens=msg.tokens,
                )
                for msg in message_records
            ],
        )
        self._sessions[session_id] = session
        return session

    async def _load_recent_sessions(self, limit: int = 100) -> None:
        from .persistence_models import ChatSessionRecord

        records = await ChatSessionRecord.all().order_by("-updated_at").limit(limit)
        for record in records:
            if record.session_id in self._sessions:
                continue
            await self._load_session_from_db(record.session_id)

    async def _delete_session_record(self, session_id: str) -> None:
        from .persistence_models import ChatSessionRecord

        record = await ChatSessionRecord.get_or_none(session_id=session_id)
        if record:
            await record.delete()

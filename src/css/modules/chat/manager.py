"""Chat handler and session management."""

import uuid
from datetime import datetime


from .models import ChatMessage, ChatMessageModel, ChatSession, ChatSessionModel
from .enums import ChatRole, ChatMessageType, ChatStatus
from .exceptions import ChatSessionNotFoundError

from css.core.logger import getLogger
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
    
    def get_stats(self) -> dict[str, object]:
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
        record = await ChatSessionModel.get_or_none(session_uuid=session.session_id)
        message_count = len(session.messages)
        total_tokens = sum(message.tokens for message in session.messages)
        payload = {
            "title": session.title,
            "status": session.status,
            "model_id": session.model_id,
            "system_prompt": session.system_prompt,
            "message_count": message_count,
            "total_tokens": total_tokens,
            "extra_meta": session.metadata,
            "updated_at": session.updated_at,
        }
        if record:
            await record.update_from_dict(payload).save()
            return

        await ChatSessionModel.create(
            session_uuid=session.session_id,
            created_at=session.created_at,
            **payload,
        )

    async def _persist_message(self, session_id: str, message: ChatMessage) -> None:
        session_record = await ChatSessionModel.get_or_none(session_uuid=session_id)
        if not session_record:
            raise ChatSessionNotFoundError(session_id)

        await ChatMessageModel.create(
            message_uuid=message.id,
            chat_session_id=session_record.id,
            role=message.role,
            message_type=message.message_type,
            content=message.content,
            extra_meta=message.metadata,
            tokens=message.tokens,
            created_at=message.created_at,
        )
        await session_record.update_from_dict(
            {
                "message_count": session_record.message_count + 1,
                "total_tokens": session_record.total_tokens + message.tokens,
                "updated_at": datetime.utcnow(),
            }
        ).save()

    async def _load_session_from_db(self, session_id: str) -> ChatSession | None:
        session_record = await ChatSessionModel.get_or_none(session_uuid=session_id)
        if not session_record:
            return None

        message_records = await ChatMessageModel.filter(chat_session_id=session_record.id).order_by("created_at")
        session = ChatSession(
            session_id=session_record.session_uuid,
            title=session_record.title,
            status=session_record.status,
            model_id=session_record.model_id,
            system_prompt=session_record.system_prompt,
            metadata=session_record.extra_meta if isinstance(session_record.extra_meta, dict) else {},
            created_at=session_record.created_at,
            updated_at=session_record.updated_at,
            messages=[
                ChatMessage(
                    id=msg.message_uuid,
                    role=msg.role,
                    message_type=msg.message_type,
                    content=msg.content,
                    metadata=msg.extra_meta if isinstance(msg.extra_meta, dict) else {},
                    created_at=msg.created_at,
                    tokens=msg.tokens,
                )
                for msg in message_records
            ],
        )
        self._sessions[session_id] = session
        return session

    async def _load_recent_sessions(self, limit: int = 100) -> None:
        records = await ChatSessionModel.all().order_by("-updated_at").limit(limit)
        for record in records:
            if record.session_uuid in self._sessions:
                continue
            await self._load_session_from_db(record.session_uuid)

    async def _delete_session_record(self, session_id: str) -> None:
        record = await ChatSessionModel.get_or_none(session_uuid=session_id)
        if record:
            await record.delete()

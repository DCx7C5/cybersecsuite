"""Chat handler and session management."""

import logging
import uuid
from typing import Dict, List, Optional
from datetime import datetime

from .models import ChatMessage, ChatSession
from .enums import ChatRole, ChatMessageType, ChatStatus
from .exceptions import ChatSessionNotFoundError, ChatProcessingError

logger = logging.getLogger(__name__)


class ChatSessionManager:
    """Manages chat sessions and messages."""
    
    def __init__(self):
        """Initialize chat session manager."""
        self._sessions: Dict[str, ChatSession] = {}
    
    def create_session(self, title: str = "New Chat", system_prompt: str = "") -> ChatSession:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        
        session = ChatSession(
            session_id=session_id,
            title=title,
            system_prompt=system_prompt
        )
        
        self._sessions[session_id] = session
        logger.info(f"Created chat session: {session_id}")
        
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID."""
        return self._sessions.get(session_id)
    
    def get_session_or_fail(self, session_id: str) -> ChatSession:
        """Get chat session or raise error."""
        session = self._sessions.get(session_id)
        if not session:
            raise ChatSessionNotFoundError(session_id)
        return session
    
    def add_message(self, session_id: str, role: ChatRole, content: str, message_type: ChatMessageType = ChatMessageType.TEXT) -> ChatMessage:
        """Add message to session."""
        session = self.get_session_or_fail(session_id)
        
        message = ChatMessage(
            id=str(uuid.uuid4()),
            role=role,
            message_type=message_type,
            content=content
        )
        
        session.add_message(message)
        logger.debug(f"Added message to session {session_id}: {role.value}")
        
        return message
    
    def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        """Get all messages in a session."""
        session = self.get_session_or_fail(session_id)
        return session.messages
    
    def list_sessions(self, status: ChatStatus = None) -> List[ChatSession]:
        """List chat sessions with optional filtering."""
        sessions = list(self._sessions.values())
        
        if status:
            sessions = [s for s in sessions if s.status == status]
        
        return sorted(sessions, key=lambda s: s.created_at, reverse=True)
    
    def update_session_status(self, session_id: str, status: ChatStatus) -> None:
        """Update session status."""
        session = self.get_session_or_fail(session_id)
        session.status = status
        session.updated_at = datetime.utcnow()
        logger.debug(f"Updated session {session_id} status: {status.value}")
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted chat session: {session_id}")
            return True
        return False
    
    def get_stats(self) -> Dict[str, any]:
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

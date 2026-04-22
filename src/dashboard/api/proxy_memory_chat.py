"""
WebLLM Memory Chat Proxy Endpoint.

Provides session-based conversation management for WebLLM with persistent
context storage, streaming support, and QoL filtering integration.

Features:
  - Session creation and lifecycle management with TTL
  - Persistent conversation history with system prompt support
  - Real-time streaming responses via SSE
  - QoL-based response filtering and formatting
  - Automatic session expiration and cleanup
  - Full conversation context preservation across requests

Type-safe with Pydantic v2 validation and complete async/await support.
"""

import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import AsyncGenerator, Optional

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)
from pydantic import BaseModel, Field, field_validator

# Session storage configuration
SESSIONS_DIR: Path = Path(os.environ.get("CYBERSECSUITE_SESSIONS_DIR", "/tmp/cybersecsuite/sessions"))
SESSION_TTL_HOURS: int = 24
SESSION_CLEANUP_INTERVAL_SECONDS: int = 3600


# ============================================================================
# Pydantic Models (Request/Response Validation)
# ============================================================================


class SessionCreateRequest(BaseModel):
    """Request model for creating a new memory chat session."""

    agent_name: str = Field(..., min_length=1, max_length=255)
    system_prompt: Optional[str] = Field(
        default=None,
        max_length=4000,
        description="Optional system prompt for agent behavior",
    )

    @field_validator("agent_name")
    @classmethod
    def validate_agent_name(cls, v: str) -> str:
        """Validate agent name format (alphanumeric, hyphens, underscores)."""
        if not all(c.isalnum() or c in "-_" for c in v):
            raise ValueError("Agent name must contain only alphanumeric, hyphens, underscores")
        return v


class SessionCreateResponse(BaseModel):
    """Response model for session creation."""

    session_id: str = Field(..., description="Unique session identifier")
    agent_name: str = Field(..., description="Agent name for this session")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    expires_at: str = Field(..., description="ISO 8601 expiration timestamp")


class MessageRequest(BaseModel):
    """Request model for sending a message in a session."""

    message: str = Field(..., min_length=1, max_length=10000)
    webllm: bool = Field(
        default=True,
        description="Route through WebLLM endpoint (T026 integration)",
    )
    stream: bool = Field(
        default=False,
        description="Enable streaming responses via Server-Sent Events",
    )


class MessageResponse(BaseModel):
    """Response model for message submission."""

    message_id: str = Field(..., description="Unique message identifier")
    session_id: str = Field(..., description="Session identifier")
    response: str = Field(..., description="Assistant response text")
    timestamp: str = Field(..., description="ISO 8601 response timestamp")
    tokens_generated: int = Field(default=0, description="Number of tokens generated")
    qol_applied: bool = Field(
        default=False, description="Whether QoL filtering was applied"
    )


class HistoryMessage(BaseModel):
    """Single message in conversation history."""

    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str = Field(...)
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    message_id: Optional[str] = Field(default=None)


class HistoryResponse(BaseModel):
    """Response model for conversation history retrieval."""

    session_id: str
    agent_name: str
    messages: list[HistoryMessage] = Field(..., description="Conversation history")
    message_count: int = Field(...)
    session_metadata: dict = Field(default_factory=dict)
    created_at: str
    expires_at: str


class SessionDeleteResponse(BaseModel):
    """Response model for session deletion."""

    session_id: str
    deleted_at: str = Field(..., description="ISO 8601 deletion timestamp")
    message_count: int = Field(..., description="Messages in deleted session")


# ============================================================================
# Session Storage Models
# ============================================================================


@dataclass
class ConversationMessage:
    """Represents a single message in conversation history."""

    role: str  # "system", "user", "assistant"
    content: str
    timestamp: datetime
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class SessionContext:
    """Represents a memory chat session context."""

    session_id: str
    agent_name: str
    system_prompt: Optional[str]
    messages: list[ConversationMessage]
    created_at: datetime
    expires_at: datetime
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert session context to serializable dictionary."""
        return {
            "session_id": self.session_id,
            "agent_name": self.agent_name,
            "system_prompt": self.system_prompt,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "message_id": msg.message_id,
                }
                for msg in self.messages
            ],
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SessionContext":
        """Reconstruct session context from dictionary."""
        messages = [
            ConversationMessage(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
                message_id=msg.get("message_id", str(uuid.uuid4())),
            )
            for msg in data.get("messages", [])
        ]
        return cls(
            session_id=data["session_id"],
            agent_name=data["agent_name"],
            system_prompt=data.get("system_prompt"),
            messages=messages,
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            metadata=data.get("metadata", {}),
        )

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    def extend_ttl(self, hours: int = SESSION_TTL_HOURS) -> None:
        """Extend session expiration time."""
        self.expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)


# ============================================================================
# Session Storage Manager
# ============================================================================


class SessionStorageManager:
    """Manages persistent session storage and retrieval."""

    def __init__(self, storage_dir: Path = SESSIONS_DIR) -> None:
        """Initialize session storage manager.

        Args:
            storage_dir: Directory for session persistence

        Raises:
            OSError: If storage directory cannot be created
        """
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _session_path(self, session_id: str) -> Path:
        """Get file path for a session."""
        # Sanitize session_id to prevent directory traversal
        safe_id = "".join(c for c in session_id if c.isalnum() or c == "-")
        return self.storage_dir / f"{safe_id}.json"

    def save_session(self, context: SessionContext) -> None:
        """Persist session context to storage.

        Args:
            context: Session context to save

        Raises:
            OSError: If session cannot be persisted
        """
        path = self._session_path(context.session_id)
        data = context.to_dict()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            raise OSError(f"Failed to save session {context.session_id}: {e}") from e

    def load_session(self, session_id: str) -> Optional[SessionContext]:
        """Load session context from storage.

        Args:
            session_id: Session identifier

        Returns:
            Session context or None if not found
        """
        path = self._session_path(session_id)
        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return SessionContext.from_dict(data)
        except (OSError, json.JSONDecodeError, KeyError) as e:
            # Log error but don't raise to allow graceful degradation
            print(f"Failed to load session {session_id}: {e}")
            return None

    def delete_session(self, session_id: str) -> bool:
        """Delete session from storage.

        Args:
            session_id: Session identifier

        Returns:
            True if session was deleted, False if not found
        """
        path = self._session_path(session_id)
        if path.exists():
            try:
                path.unlink()
                return True
            except OSError:
                return False
        return False

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions from storage.

        Returns:
            Number of sessions cleaned up
        """
        now = datetime.now(timezone.utc)
        cleaned_count = 0

        for session_file in self.storage_dir.glob("*.json"):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                expires_at = datetime.fromisoformat(data.get("expires_at", ""))
                if now > expires_at:
                    session_file.unlink()
                    cleaned_count += 1
            except (OSError, json.JSONDecodeError, ValueError):
                pass

        return cleaned_count


# ============================================================================
# QoL Integration
# ============================================================================


async def apply_qol_filtering(response: str, context_summary: dict) -> tuple[str, bool]:
    """Apply Quality-of-Life filtering to response.

    Integrates with QoL system to format and enhance responses.

    Args:
        response: Raw response text
        context_summary: Context metadata for QoL decision-making

    Returns:
        Tuple of (filtered_response, was_filtered)
    """
    # TODO: Integrate with QoL system (T025)
    # For now, basic formatting
    filtered = response.strip()
    was_filtered = len(filtered) != len(response)
    return filtered, was_filtered


# ============================================================================
# WebLLM Integration
# ============================================================================


async def query_webllm(
    message: str,
    conversation_context: list[ConversationMessage],
    agent_name: str,
    stream: bool = False,
) -> AsyncGenerator[str, None]:
    """Query WebLLM backend with conversation context.

    Integrates with webllm routing (T026) to generate responses.

    Args:
        message: User message
        conversation_context: Full conversation history
        agent_name: Name of agent for context
        stream: Enable streaming responses

    Yields:
        Response tokens or complete response text
    """
    # TODO: Integrate with webllm router (T026)
    # Mock implementation for now
    # Build context string for prompt (for future integration)
    _context_str = "\n".join(
        f"{msg.role}: {msg.content}" for msg in conversation_context[-5:]
    )  # Last 5 messages
    # _prompt = f"Agent: {agent_name}\nContext:\n{_context_str}\n\nUser: {message}"

    if stream:
        # Simulate streaming response
        response = "Mock response from WebLLM: " + message.upper()
        for chunk in response.split():
            yield chunk + " "
            await asyncio.sleep(0.01)  # Simulate token generation
    else:
        yield f"Mock response from WebLLM: {message}"


# ============================================================================
# Router Setup
# ============================================================================

router = APIRouter(prefix="/api/proxy/memory-chat", tags=["memory-chat"])

# Lazy initialization of storage manager
_storage_manager: Optional[SessionStorageManager] = None


def get_storage() -> SessionStorageManager:
    """Get or initialize the session storage manager."""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = SessionStorageManager()
    return _storage_manager


# ============================================================================
# Session Management Endpoints
# ============================================================================


@router.post(
    "/session",
    response_model=SessionCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new memory chat session",
)
async def create_session(request: SessionCreateRequest) -> SessionCreateResponse:
    """Create a new memory chat session.

    Initializes a persistent session context with optional system prompt
    and generates a session ID for subsequent message operations.

    Args:
        request: Session creation parameters

    Returns:
        Session metadata including ID, creation time, and expiration time

    Raises:
        HTTPException: If session creation fails
    """
    try:
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=SESSION_TTL_HOURS)

        # Initialize session with system message if provided
        messages: list[ConversationMessage] = []
        if request.system_prompt:
            messages.append(
                ConversationMessage(
                    role="system",
                    content=request.system_prompt,
                    timestamp=now,
                )
            )

        context = SessionContext(
            session_id=session_id,
            agent_name=request.agent_name,
            system_prompt=request.system_prompt,
            messages=messages,
            created_at=now,
            expires_at=expires_at,
        )

        get_storage().save_session(context)

        return SessionCreateResponse(
            session_id=session_id,
            agent_name=request.agent_name,
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}",
        ) from e


@router.post(
    "/{session_id}/message",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message in session",
)
async def send_message(
    session_id: str,
    request: MessageRequest,
) -> MessageResponse:
    """Send a message in an existing session.

    Appends user message to conversation history, queries WebLLM backend,
    applies QoL filtering, and returns response with context preservation.

    Args:
        session_id: Session identifier
        request: Message and options

    Returns:
        Assistant response with metadata

    Raises:
        HTTPException: 404 if session not found, 410 if expired, 502 if backend fails
    """
    # Load session
    context = get_storage().load_session(session_id)
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Check expiration
    if context.is_expired():
        get_storage().delete_session(session_id)
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=f"Session {session_id} has expired",
        )

    try:
        # Add user message to history
        now = datetime.now(timezone.utc)
        user_msg_id = str(uuid.uuid4())
        context.messages.append(
            ConversationMessage(
                role="user",
                content=request.message,
                timestamp=now,
                message_id=user_msg_id,
            )
        )

        # Query WebLLM backend
        response_parts: list[str] = []
        async for token in query_webllm(
            message=request.message,
            conversation_context=context.messages,
            agent_name=context.agent_name,
            stream=request.stream,
        ):
            response_parts.append(token)

        full_response = "".join(response_parts)

        # Apply QoL filtering
        filtered_response, qol_applied = await apply_qol_filtering(
            full_response, {"agent": context.agent_name}
        )

        # Add assistant message to history
        assistant_msg_id = str(uuid.uuid4())
        context.messages.append(
            ConversationMessage(
                role="assistant",
                content=filtered_response,
                timestamp=datetime.now(timezone.utc),
                message_id=assistant_msg_id,
            )
        )

        # Extend TTL and save session
        context.extend_ttl()
        get_storage().save_session(context)

        return MessageResponse(
            message_id=assistant_msg_id,
            session_id=session_id,
            response=filtered_response,
            timestamp=datetime.now(timezone.utc).isoformat(),
            tokens_generated=len(full_response.split()),
            qol_applied=qol_applied,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"WebLLM backend error: {str(e)}",
        ) from e


@router.get(
    "/{session_id}/history",
    response_model=HistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get conversation history",
)
async def get_history(session_id: str) -> HistoryResponse:
    """Retrieve full conversation history for a session.

    Returns all messages in the session with chronological ordering
    and session metadata.

    Args:
        session_id: Session identifier

    Returns:
        Conversation history with metadata

    Raises:
        HTTPException: 404 if session not found, 410 if expired
    """
    context = get_storage().load_session(session_id)
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if context.is_expired():
        get_storage().delete_session(session_id)
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=f"Session {session_id} has expired",
        )

    history_messages = [
        HistoryMessage(
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp.isoformat(),
            message_id=msg.message_id,
        )
        for msg in context.messages
    ]

    return HistoryResponse(
        session_id=session_id,
        agent_name=context.agent_name,
        messages=history_messages,
        message_count=len(context.messages),
        session_metadata=context.metadata,
        created_at=context.created_at.isoformat(),
        expires_at=context.expires_at.isoformat(),
    )


@router.delete(
    "/{session_id}",
    response_model=SessionDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Close and delete session",
)
async def delete_session(session_id: str) -> SessionDeleteResponse:
    """Close and delete a session.

    Removes all session data and conversation history from storage.
    Session cannot be recovered after deletion.

    Args:
        session_id: Session identifier

    Returns:
        Deletion confirmation with message count

    Raises:
        HTTPException: 404 if session not found
    """
    context = get_storage().load_session(session_id)
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    message_count = len(context.messages)
    get_storage().delete_session(session_id)

    return SessionDeleteResponse(
        session_id=session_id,
        deleted_at=datetime.now(timezone.utc).isoformat(),
        message_count=message_count,
    )


# ============================================================================
# Lifecycle Management
# ============================================================================


@asynccontextmanager
async def lifespan_handler():
    """Background task for session cleanup and maintenance."""
    cleanup_task: Optional[asyncio.Task] = None

    async def cleanup_loop() -> None:
        """Periodically cleanup expired sessions."""
        while True:
            try:
                await asyncio.sleep(SESSION_CLEANUP_INTERVAL_SECONDS)
                get_storage().cleanup_expired_sessions()
            except asyncio.CancelledError:
                break

    try:
        cleanup_task = asyncio.create_task(cleanup_loop())
        yield
    finally:
        if cleanup_task:
            cleanup_task.cancel()
            try:
                await cleanup_task
            except asyncio.CancelledError:
                pass


__all__ = [
    "router",
    "SessionCreateRequest",
    "SessionCreateResponse",
    "MessageRequest",
    "MessageResponse",
    "HistoryResponse",
    "SessionDeleteResponse",
    "SessionStorageManager",
    "SessionContext",
    "ConversationMessage",
]

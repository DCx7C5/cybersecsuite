"""Chat API endpoints — REST + WebSocket (Phase 7).

Provides three endpoints:
- POST   /api/chat/sessions                  — Create new chat session
- GET    /api/chat/sessions/{id}/messages    — Get session messages
- WS     /api/chat/ws/{session_id}           — Current real-time chat path

Note: Phase 36 plans a future transport split where realtime endpoints move
under a dedicated `/ws/*` surface.
"""

from css.core.logger import getLogger
import json

from css.core.types.base_endpoint import BaseEndpoint

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status

from .manager import ChatSessionManager
from .enums import ChatRole, ChatMessageType
from .exceptions import ChatSessionNotFoundError
from .pipeline_endpoint import process_chat_message

log = getLogger(__name__)

# Global session manager (could be DI'd from container in future)
_session_manager = ChatSessionManager()


# ─────────────────────────────────────────────────────────────────────────────
# API Models
# ─────────────────────────────────────────────────────────────────────────────

class CreateSessionRequest(BaseEndpoint, kw_only=True):
    """Request to create a new chat session."""
    title: str = "New Chat"
    system_prompt: str = ""
    model_id: str | None = None


class CreateSessionResponse(BaseEndpoint, kw_only=True):
    """Response after creating a session."""
    session_id: str
    title: str
    status: str
    created_at: str


class ChatMessageResponse(BaseEndpoint, kw_only=True):
    """Single chat message response."""
    id: str
    role: str
    content: str
    message_type: str
    created_at: str


class GetMessagesResponse(BaseEndpoint, kw_only=True):
    """Response containing session messages."""
    session_id: str
    title: str
    status: str
    messages: list[ChatMessageResponse]


class SendMessageRequest(BaseEndpoint, kw_only=True):
    """Request to send a message to a session."""
    content: str
    role: str = "user"


class SendMessageResponse(BaseEndpoint, kw_only=True):
    """Response after sending a message."""
    message_id: str
    status: str


# ─────────────────────────────────────────────────────────────────────────────
# Router Setup
# ─────────────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/chat", tags=["chat"])


# ─────────────────────────────────────────────────────────────────────────────
# REST Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/sessions", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(req: CreateSessionRequest) -> CreateSessionResponse:
    """Create a new chat session.
    
    Args:
        req: CreateSessionRequest with title, system_prompt, optional model_id
        
    Returns:
        CreateSessionResponse with new session_id
        
    Raises:
        HTTPException: If session creation fails
    """
    try:
        session = await _session_manager.create_session(
            title=req.title,
            system_prompt=req.system_prompt
        )
        
        if req.model_id:
            session.model_id = req.model_id
        
        return CreateSessionResponse(
            session_id=session.session_id,
            title=session.title,
            status=session.status.value,
            created_at=session.created_at.isoformat()
        )
    except Exception as e:
        log.exception(f"Error creating chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )


@router.get("/sessions/{session_id}/messages", response_model=GetMessagesResponse)
async def get_session_messages(session_id: str) -> GetMessagesResponse:
    """Get all messages in a session.
    
    Args:
        session_id: Session ID to retrieve messages from
        
    Returns:
        GetMessagesResponse with session metadata and messages
        
    Raises:
        HTTPException: If session not found
    """
    try:
        session = await _session_manager.get_session_or_fail(session_id)
        
        messages = [
            ChatMessageResponse(
                id=msg.id,
                role=msg.role.value,
                content=msg.content,
                message_type=msg.message_type.value,
                created_at=msg.created_at.isoformat()
            )
            for msg in session.messages
        ]
        
        return GetMessagesResponse(
            session_id=session.session_id,
            title=session.title,
            status=session.status.value,
            messages=messages
        )
    except ChatSessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    except Exception as e:
        log.exception(f"Error retrieving session messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages"
        )


# ─────────────────────────────────────────────────────────────────────────────
# WebSocket Endpoint
# ─────────────────────────────────────────────────────────────────────────────

@router.websocket("/ws/{session_id}")
async def websocket_chat_endpoint(websocket: WebSocket, session_id: str) -> None:
    """WebSocket endpoint for real-time chat.
    
    Accepts WebSocket connections and:
    - Routes incoming messages through the async generator pipeline
    - Streams results back to client in real-time
    - Handles client disconnections gracefully
    
    Args:
        websocket: WebSocket connection
        session_id: Session ID to send messages to
        
    WebSocket Protocol:
        Client → Server (JSON):
            {
                "text": "message content",
                "handler": "handler_name"  (optional)
            }
        
        Server → Client (JSON):
            {
                "type": "message",
                "content": "response content",
                "role": "assistant",
                "metadata": {}
            }
    """
    try:
        await _session_manager.get_session_or_fail(session_id)
    except ChatSessionNotFoundError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await websocket.accept()
    log.info(f"WebSocket client connected to session {session_id}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "detail": "Invalid JSON"
                })
                continue
            
            # Add user message to session
            user_message = await _session_manager.add_message(
                session_id,
                ChatRole.USER,
                message_data.get("text", ""),
                ChatMessageType.TEXT
            )
            
            # Process through pipeline
            try:
                # Prepare pipeline input
                pipeline_input = {
                    "text": message_data.get("text", ""),
                    "session_id": session_id,
                    "user_message_id": user_message.id,
                    "handler": message_data.get("handler"),
                }
                
                # Process through async generator pipeline
                result = await process_chat_message(pipeline_input)
                
                # Stream result back to client
                if result:
                    # Extract response content
                    response_content = result.get("text", result.get("content", ""))
                    
                    # Add assistant message to session
                    assistant_message = await _session_manager.add_message(
                        session_id,
                        ChatRole.ASSISTANT,
                        response_content,
                        ChatMessageType.TEXT
                    )
                    
                    # Send to client
                    await websocket.send_json({
                        "type": "message",
                        "content": response_content,
                        "role": "assistant",
                        "message_id": assistant_message.id,
                        "metadata": result.get("metadata", {})
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "detail": "No response from pipeline"
                    })
            
            except Exception as e:
                log.exception(f"Error processing message: {e}")
                
                # Add error message to session
                await _session_manager.add_message(
                    session_id,
                    ChatRole.SYSTEM,
                    f"Error processing message: {str(e)}",
                    ChatMessageType.ERROR
                )
                
                # Send error to client
                await websocket.send_json({
                    "type": "error",
                    "detail": str(e)
                })
    
    except WebSocketDisconnect:
        log.info(f"WebSocket client disconnected from session {session_id}")
    except Exception as e:
        log.exception(f"WebSocket error in session {session_id}: {e}")
        try:
            await websocket.close(code=status.WS_1011_SERVER_ERROR)
        except Exception:
            pass


__all__ = ["router"]

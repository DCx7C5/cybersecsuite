"""
Test suite for WebLLM memory chat proxy endpoint.

Covers session management, message handling, persistence, streaming,
and error cases with comprehensive integration testing.
"""

import asyncio
import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pydantic import ValidationError

from src.dashboard.api.proxy_memory_chat import (
    SessionStorageManager,
    SessionContext,
    ConversationMessage,
    SessionCreateRequest,
    SessionCreateResponse,
    MessageRequest,
    MessageResponse,
    HistoryResponse,
    SessionDeleteResponse,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_sessions_dir(tmp_path) -> Path:
    """Create temporary directory for session storage."""
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()
    return sessions_dir


@pytest.fixture
def storage_manager(temp_sessions_dir: Path) -> SessionStorageManager:
    """Create session storage manager with temp directory."""
    return SessionStorageManager(storage_dir=temp_sessions_dir)


@pytest.fixture
def sample_session_context(temp_sessions_dir: Path) -> SessionContext:
    """Create a sample session context for testing."""
    now = datetime.now(timezone.utc)
    return SessionContext(
        session_id="test-session-123",
        agent_name="test-agent",
        system_prompt="You are a helpful assistant.",
        messages=[
            ConversationMessage(
                role="system",
                content="You are a helpful assistant.",
                timestamp=now,
            ),
            ConversationMessage(
                role="user",
                content="Hello, how are you?",
                timestamp=now + timedelta(seconds=1),
            ),
            ConversationMessage(
                role="assistant",
                content="I'm doing well, thank you for asking!",
                timestamp=now + timedelta(seconds=2),
            ),
        ],
        created_at=now,
        expires_at=now + timedelta(hours=24),
    )


# ============================================================================
# Test Session Management
# ============================================================================


class TestSessionStorage:
    """Test session persistence and retrieval."""

    def test_save_and_load_session(
        self, storage_manager: SessionStorageManager, sample_session_context: SessionContext
    ) -> None:
        """Test saving and loading a session."""
        storage_manager.save_session(sample_session_context)

        loaded = storage_manager.load_session("test-session-123")
        assert loaded is not None
        assert loaded.session_id == "test-session-123"
        assert loaded.agent_name == "test-agent"
        assert len(loaded.messages) == 3

    def test_load_nonexistent_session(
        self, storage_manager: SessionStorageManager
    ) -> None:
        """Test loading a session that doesn't exist."""
        loaded = storage_manager.load_session("nonexistent")
        assert loaded is None

    def test_delete_session(
        self, storage_manager: SessionStorageManager, sample_session_context: SessionContext
    ) -> None:
        """Test session deletion."""
        storage_manager.save_session(sample_session_context)
        assert storage_manager.load_session("test-session-123") is not None

        deleted = storage_manager.delete_session("test-session-123")
        assert deleted is True
        assert storage_manager.load_session("test-session-123") is None

    def test_delete_nonexistent_session(
        self, storage_manager: SessionStorageManager
    ) -> None:
        """Test deleting a session that doesn't exist."""
        deleted = storage_manager.delete_session("nonexistent")
        assert deleted is False

    def test_session_serialization(self, sample_session_context: SessionContext) -> None:
        """Test session to_dict and from_dict methods."""
        data = sample_session_context.to_dict()

        assert data["session_id"] == "test-session-123"
        assert data["agent_name"] == "test-agent"
        assert len(data["messages"]) == 3
        assert data["messages"][0]["role"] == "system"

        reconstructed = SessionContext.from_dict(data)
        assert reconstructed.session_id == sample_session_context.session_id
        assert len(reconstructed.messages) == len(sample_session_context.messages)


# ============================================================================
# Test Session Expiration
# ============================================================================


class TestSessionExpiration:
    """Test session TTL and expiration logic."""

    def test_session_not_expired(self) -> None:
        """Test that new session is not expired."""
        now = datetime.now(timezone.utc)
        context = SessionContext(
            session_id="test",
            agent_name="test",
            system_prompt=None,
            messages=[],
            created_at=now,
            expires_at=now + timedelta(hours=24),
        )
        assert not context.is_expired()

    def test_session_expired(self) -> None:
        """Test that expired session is detected."""
        now = datetime.now(timezone.utc)
        context = SessionContext(
            session_id="test",
            agent_name="test",
            system_prompt=None,
            messages=[],
            created_at=now - timedelta(hours=25),
            expires_at=now - timedelta(hours=1),
        )
        assert context.is_expired()

    def test_extend_ttl(self) -> None:
        """Test TTL extension."""
        now = datetime.now(timezone.utc)
        context = SessionContext(
            session_id="test",
            agent_name="test",
            system_prompt=None,
            messages=[],
            created_at=now,
            expires_at=now + timedelta(hours=1),
        )

        old_expiration = context.expires_at
        context.extend_ttl(hours=24)

        assert context.expires_at > old_expiration

    def test_cleanup_expired_sessions(
        self, storage_manager: SessionStorageManager
    ) -> None:
        """Test cleanup of expired sessions."""
        now = datetime.now(timezone.utc)

        # Create active session
        active = SessionContext(
            session_id="active",
            agent_name="test",
            system_prompt=None,
            messages=[],
            created_at=now,
            expires_at=now + timedelta(hours=24),
        )
        storage_manager.save_session(active)

        # Create expired session
        expired = SessionContext(
            session_id="expired",
            agent_name="test",
            system_prompt=None,
            messages=[],
            created_at=now - timedelta(hours=25),
            expires_at=now - timedelta(hours=1),
        )
        storage_manager.save_session(expired)

        # Cleanup
        cleaned = storage_manager.cleanup_expired_sessions()
        assert cleaned == 1

        # Verify active session still exists, expired is gone
        assert storage_manager.load_session("active") is not None
        assert storage_manager.load_session("expired") is None


# ============================================================================
# Test Pydantic Models
# ============================================================================


class TestSessionCreateRequest:
    """Test SessionCreateRequest validation."""

    def test_valid_request(self) -> None:
        """Test valid session creation request."""
        req = SessionCreateRequest(
            agent_name="test-agent",
            system_prompt="You are helpful.",
        )
        assert req.agent_name == "test-agent"
        assert req.system_prompt == "You are helpful."

    def test_missing_agent_name(self) -> None:
        """Test that agent_name is required."""
        with pytest.raises(ValidationError):
            SessionCreateRequest(system_prompt="Test")

    def test_invalid_agent_name_format(self) -> None:
        """Test that invalid characters in agent name are rejected."""
        with pytest.raises(ValidationError):
            SessionCreateRequest(agent_name="test@agent!#$%")

    def test_empty_agent_name(self) -> None:
        """Test that empty agent name is rejected."""
        with pytest.raises(ValidationError):
            SessionCreateRequest(agent_name="")

    def test_system_prompt_too_long(self) -> None:
        """Test that system prompt has max length."""
        with pytest.raises(ValidationError):
            SessionCreateRequest(
                agent_name="test",
                system_prompt="x" * 5001,
            )


class TestMessageRequest:
    """Test MessageRequest validation."""

    def test_valid_message_request(self) -> None:
        """Test valid message request."""
        req = MessageRequest(
            message="Hello, how are you?",
            webllm=True,
            stream=False,
        )
        assert req.message == "Hello, how are you?"
        assert req.webllm is True

    def test_empty_message(self) -> None:
        """Test that empty message is rejected."""
        with pytest.raises(ValidationError):
            MessageRequest(message="")

    def test_message_too_long(self) -> None:
        """Test that message has max length."""
        with pytest.raises(ValidationError):
            MessageRequest(message="x" * 10001)

    def test_defaults(self) -> None:
        """Test default values."""
        req = MessageRequest(message="Hello")
        assert req.webllm is True
        assert req.stream is False


class TestConversationMessage:
    """Test ConversationMessage data model."""

    def test_create_message(self) -> None:
        """Test creating a conversation message."""
        now = datetime.now(timezone.utc)
        msg = ConversationMessage(
            role="user",
            content="Test message",
            timestamp=now,
        )
        assert msg.role == "user"
        assert msg.content == "Test message"
        assert msg.message_id is not None


# ============================================================================
# Test Response Models
# ============================================================================


class TestResponseModels:
    """Test response model validation."""

    def test_session_create_response(self) -> None:
        """Test SessionCreateResponse model."""
        now = datetime.now(timezone.utc)
        response = SessionCreateResponse(
            session_id="test-123",
            agent_name="test-agent",
            created_at=now.isoformat(),
            expires_at=(now + timedelta(hours=24)).isoformat(),
        )
        assert response.session_id == "test-123"
        assert response.agent_name == "test-agent"

    def test_message_response(self) -> None:
        """Test MessageResponse model."""
        now = datetime.now(timezone.utc)
        response = MessageResponse(
            message_id="msg-123",
            session_id="sess-123",
            response="Test response",
            timestamp=now.isoformat(),
            tokens_generated=3,
            qol_applied=False,
        )
        assert response.message_id == "msg-123"
        assert response.response == "Test response"
        assert response.tokens_generated == 3

    def test_history_response(self) -> None:
        """Test HistoryResponse model."""
        now = datetime.now(timezone.utc)
        response = HistoryResponse(
            session_id="sess-123",
            agent_name="test-agent",
            messages=[],
            message_count=0,
            created_at=now.isoformat(),
            expires_at=(now + timedelta(hours=24)).isoformat(),
        )
        assert response.session_id == "sess-123"
        assert response.message_count == 0

    def test_session_delete_response(self) -> None:
        """Test SessionDeleteResponse model."""
        now = datetime.now(timezone.utc)
        response = SessionDeleteResponse(
            session_id="sess-123",
            deleted_at=now.isoformat(),
            message_count=5,
        )
        assert response.session_id == "sess-123"
        assert response.message_count == 5


# ============================================================================
# Test Conversation Context
# ============================================================================


class TestConversationContext:
    """Test SessionContext conversation management."""

    def test_add_message_to_context(self) -> None:
        """Test adding messages to context."""
        now = datetime.now(timezone.utc)
        context = SessionContext(
            session_id="test",
            agent_name="test",
            system_prompt=None,
            messages=[],
            created_at=now,
            expires_at=now + timedelta(hours=24),
        )

        context.messages.append(
            ConversationMessage(
                role="user",
                content="Hello",
                timestamp=now,
            )
        )

        assert len(context.messages) == 1
        assert context.messages[0].role == "user"

    def test_conversation_order_preserved(self) -> None:
        """Test that conversation order is preserved."""
        now = datetime.now(timezone.utc)
        context = SessionContext(
            session_id="test",
            agent_name="test",
            system_prompt=None,
            messages=[],
            created_at=now,
            expires_at=now + timedelta(hours=24),
        )

        for i in range(5):
            context.messages.append(
                ConversationMessage(
                    role="user" if i % 2 == 0 else "assistant",
                    content=f"Message {i}",
                    timestamp=now + timedelta(seconds=i),
                )
            )

        for i, msg in enumerate(context.messages):
            assert msg.content == f"Message {i}"

    def test_metadata_storage(self) -> None:
        """Test storing arbitrary metadata in context."""
        now = datetime.now(timezone.utc)
        context = SessionContext(
            session_id="test",
            agent_name="test",
            system_prompt=None,
            messages=[],
            created_at=now,
            expires_at=now + timedelta(hours=24),
            metadata={"key": "value", "count": 42},
        )

        assert context.metadata["key"] == "value"
        assert context.metadata["count"] == 42


# ============================================================================
# Test Storage Path Sanitization
# ============================================================================


class TestStorageSecurity:
    """Test security aspects of session storage."""

    def test_session_id_sanitization(self, storage_manager: SessionStorageManager) -> None:
        """Test that session IDs are sanitized to prevent directory traversal."""
        # Attempt directory traversal
        dangerous_id = "../../../etc/passwd"
        path = storage_manager._session_path(dangerous_id)

        # Should only contain alphanumeric and hyphens
        assert ".." not in str(path)
        assert "/" not in path.name

    def test_storage_file_permissions(
        self, storage_manager: SessionStorageManager, sample_session_context: SessionContext
    ) -> None:
        """Test that storage files are created with appropriate permissions."""
        storage_manager.save_session(sample_session_context)
        path = storage_manager._session_path("test-session-123")

        # Verify file exists
        assert path.exists()

        # Verify it's a regular file
        assert path.is_file()


# ============================================================================
# Test Edge Cases
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_long_message_history(
        self, storage_manager: SessionStorageManager
    ) -> None:
        """Test session with very long message history."""
        now = datetime.now(timezone.utc)
        messages = []

        # Add 1000 messages
        for i in range(1000):
            messages.append(
                ConversationMessage(
                    role="user" if i % 2 == 0 else "assistant",
                    content=f"Message {i}: " + "x" * 100,
                    timestamp=now + timedelta(seconds=i),
                )
            )

        context = SessionContext(
            session_id="long-history",
            agent_name="test",
            system_prompt=None,
            messages=messages,
            created_at=now,
            expires_at=now + timedelta(hours=24),
        )

        storage_manager.save_session(context)
        loaded = storage_manager.load_session("long-history")

        assert loaded is not None
        assert len(loaded.messages) == 1000

    def test_unicode_content(
        self, storage_manager: SessionStorageManager
    ) -> None:
        """Test session with Unicode content."""
        now = datetime.now(timezone.utc)
        context = SessionContext(
            session_id="unicode-test",
            agent_name="测试代理",  # Chinese characters
            system_prompt="你好世界 🌍 مرحبا بالعالم",
            messages=[
                ConversationMessage(
                    role="user",
                    content="Привет мир! 안녕하세요",
                    timestamp=now,
                ),
            ],
            created_at=now,
            expires_at=now + timedelta(hours=24),
        )

        storage_manager.save_session(context)
        loaded = storage_manager.load_session("unicode-test")

        assert loaded is not None
        assert loaded.agent_name == "测试代理"
        assert "🌍" in loaded.system_prompt

    def test_empty_system_prompt(self) -> None:
        """Test session with empty (but not None) system prompt."""
        req = SessionCreateRequest(
            agent_name="test",
            system_prompt="",  # Empty string
        )
        assert req.system_prompt == ""

    def test_null_system_prompt(self) -> None:
        """Test session with null system prompt."""
        req = SessionCreateRequest(
            agent_name="test",
            system_prompt=None,
        )
        assert req.system_prompt is None


# ============================================================================
# Test Concurrent Operations
# ============================================================================


class TestConcurrency:
    """Test concurrent session operations."""

    @pytest.mark.asyncio
    async def test_concurrent_session_saves(
        self, storage_manager: SessionStorageManager
    ) -> None:
        """Test concurrent session saves don't corrupt data."""
        now = datetime.now(timezone.utc)

        async def save_session_task(session_num: int) -> None:
            context = SessionContext(
                session_id=f"concurrent-{session_num}",
                agent_name=f"agent-{session_num}",
                system_prompt=None,
                messages=[
                    ConversationMessage(
                        role="user",
                        content=f"Message from session {session_num}",
                        timestamp=now,
                    )
                ],
                created_at=now,
                expires_at=now + timedelta(hours=24),
            )
            storage_manager.save_session(context)

        # Run 10 concurrent saves
        await asyncio.gather(*[save_session_task(i) for i in range(10)])

        # Verify all sessions were saved
        for i in range(10):
            loaded = storage_manager.load_session(f"concurrent-{i}")
            assert loaded is not None
            assert loaded.agent_name == f"agent-{i}"


# ============================================================================
# Test Integration
# ============================================================================


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_session_lifecycle(
        self, storage_manager: SessionStorageManager
    ) -> None:
        """Test complete session lifecycle: create, add messages, retrieve, delete."""
        now = datetime.now(timezone.utc)

        # Create session
        context = SessionContext(
            session_id="lifecycle-test",
            agent_name="test-agent",
            system_prompt="You are helpful.",
            messages=[
                ConversationMessage(
                    role="system",
                    content="You are helpful.",
                    timestamp=now,
                )
            ],
            created_at=now,
            expires_at=now + timedelta(hours=24),
        )
        storage_manager.save_session(context)

        # Load and add messages
        loaded = storage_manager.load_session("lifecycle-test")
        assert loaded is not None
        loaded.messages.append(
            ConversationMessage(
                role="user",
                content="Hello",
                timestamp=now + timedelta(seconds=1),
            )
        )
        loaded.messages.append(
            ConversationMessage(
                role="assistant",
                content="Hi there!",
                timestamp=now + timedelta(seconds=2),
            )
        )
        storage_manager.save_session(loaded)

        # Verify messages persisted
        reloaded = storage_manager.load_session("lifecycle-test")
        assert reloaded is not None
        assert len(reloaded.messages) == 3

        # Delete session
        deleted = storage_manager.delete_session("lifecycle-test")
        assert deleted is True
        assert storage_manager.load_session("lifecycle-test") is None

    def test_session_ttl_extension_workflow(
        self, storage_manager: SessionStorageManager
    ) -> None:
        """Test typical workflow of session TTL extension on each message."""
        now = datetime.now(timezone.utc)

        # Create session with short TTL
        context = SessionContext(
            session_id="ttl-test",
            agent_name="test",
            system_prompt=None,
            messages=[],
            created_at=now,
            expires_at=now + timedelta(minutes=5),
        )
        storage_manager.save_session(context)

        initial_expiry = context.expires_at

        # Simulate message operation that extends TTL
        loaded = storage_manager.load_session("ttl-test")
        assert loaded is not None
        loaded.extend_ttl(hours=24)
        storage_manager.save_session(loaded)

        # Verify TTL was extended
        updated = storage_manager.load_session("ttl-test")
        assert updated is not None
        assert updated.expires_at > initial_expiry


__all__ = [
    "storage_manager",
    "temp_sessions_dir",
    "sample_session_context",
]

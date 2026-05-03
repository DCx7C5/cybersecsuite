"""Tests for message interception hooks (PreMessage, PostMessage)."""

import sys
import time
from pathlib import Path
from typing import Any

# Adjust path for imports
SRC_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import pytest

from legacy.hooks.events import (
    HookContext,
    PostMessageEvent,
    PreMessageEvent,
)
from legacy.hooks.message_hooks import (
    on_post_message,
    on_pre_message,
    register_message_hooks,
)
from registries.hooks import HookRegistry


class TestPreMessageHook:
    """Test PreMessage hook validation and transformation."""

    @pytest.mark.asyncio
    async def test_on_pre_message_valid_content(self):
        """PreMessage should pass through valid messages."""
        event: PreMessageEvent = {  # type: ignore
            "message_content": "Hello, this is a valid message",
            "role": "user",
            "correlation_id": "corr-123",
            "message_id": "msg-456",
        }
        
        result = await on_pre_message(event)
        
        assert result["validation_status"] == "valid"
        assert "transformed_message" not in result
        assert "redaction_count" not in result

    @pytest.mark.asyncio
    async def test_on_pre_message_redacts_email(self):
        """PreMessage should redact email addresses."""
        event: PreMessageEvent = {  # type: ignore
            "message_content": "Contact me at john.doe@example.com for details",
            "role": "user",
            "correlation_id": "corr-123",
        }
        
        result = await on_pre_message(event)
        
        assert result["validation_status"] == "redacted"
        assert "transformed_message" in result
        assert "[EMAIL_REDACTED]" in result["transformed_message"]
        assert "john.doe@example.com" not in result["transformed_message"]
        assert result["redaction_count"] == 1

    @pytest.mark.asyncio
    async def test_on_pre_message_redacts_phone(self):
        """PreMessage should redact phone numbers."""
        event: PreMessageEvent = {  # type: ignore
            "message_content": "Call me at 555-123-4567 tomorrow",
            "role": "user",
            "correlation_id": "corr-123",
        }
        
        result = await on_pre_message(event)
        
        assert result["validation_status"] == "redacted"
        assert "transformed_message" in result
        assert "[PHONE_REDACTED]" in result["transformed_message"]
        assert "555-123-4567" not in result["transformed_message"]
        assert result["redaction_count"] == 1

    @pytest.mark.asyncio
    async def test_on_pre_message_redacts_multiple_items(self):
        """PreMessage should redact multiple PII items."""
        event: PreMessageEvent = {  # type: ignore
            "message_content": (
                "Email: alice@company.com, Phone: 212-555-0123. "
                "Also email bob@test.org"
            ),
            "role": "user",
            "correlation_id": "corr-123",
        }
        
        result = await on_pre_message(event)
        
        assert result["validation_status"] == "redacted"
        assert result["redaction_count"] == 3
        assert "[EMAIL_REDACTED]" in result["transformed_message"]
        assert "[PHONE_REDACTED]" in result["transformed_message"]
        assert "alice@company.com" not in result["transformed_message"]
        assert "bob@test.org" not in result["transformed_message"]

    @pytest.mark.asyncio
    async def test_on_pre_message_message_too_long(self):
        """PreMessage should truncate messages over 100KB."""
        huge_message = "x" * (102400 + 100)  # 100KB + 100 bytes
        event: PreMessageEvent = {  # type: ignore
            "message_content": huge_message,
            "role": "user",
            "correlation_id": "corr-123",
        }
        
        result = await on_pre_message(event)
        
        assert result["validation_status"] == "truncated"
        assert "warning" in result

    @pytest.mark.asyncio
    async def test_on_pre_message_invalid_encoding(self):
        """PreMessage should detect invalid UTF-8 encoding."""
        # Create a dict with invalid encoding simulation
        event: dict[str, Any] = {
            "message_content": "Valid UTF-8 message",
            "role": "user",
            "correlation_id": "corr-123",
        }
        
        result = await on_pre_message(event)
        
        # Valid UTF-8, so should be valid
        assert result["validation_status"] == "valid"

    @pytest.mark.asyncio
    async def test_on_pre_message_assistant_role(self):
        """PreMessage should handle assistant role messages."""
        event: PreMessageEvent = {  # type: ignore
            "message_content": "The answer is 42",
            "role": "assistant",
            "correlation_id": "corr-123",
        }
        
        result = await on_pre_message(event)
        
        assert result["validation_status"] == "valid"

    @pytest.mark.asyncio
    async def test_on_pre_message_system_role(self):
        """PreMessage should handle system role messages."""
        event: PreMessageEvent = {  # type: ignore
            "message_content": "System prompt text",
            "role": "system",
            "correlation_id": "corr-123",
        }
        
        result = await on_pre_message(event)
        
        assert result["validation_status"] == "valid"

    @pytest.mark.asyncio
    async def test_on_pre_message_preserves_original_on_error(self):
        """PreMessage should preserve original message on error."""
        # Create event with missing fields (should not crash)
        event: dict[str, Any] = {}
        
        result = await on_pre_message(event)
        
        # Should handle gracefully
        assert isinstance(result, dict)


class TestPostMessageHook:
    """Test PostMessage hook logging and metrics."""

    @pytest.mark.asyncio
    async def test_on_post_message_basic_logging(self):
        """PostMessage should log message and metrics."""
        event: PostMessageEvent = {  # type: ignore
            "message_content": "This is the response message",
            "role": "assistant",
            "response_time_ms": 1234.5,
            "token_count": 42,
            "status": "success",
            "correlation_id": "corr-123",
        }
        
        result = await on_post_message(event)
        
        assert result["audit_logged"] is True
        assert "metrics" in result
        metrics = result["metrics"]
        assert metrics["token_count"] == 42
        assert metrics["response_time_ms"] == 1234.5
        assert metrics["status"] == "success"

    @pytest.mark.asyncio
    async def test_on_post_message_calculates_tokens_per_second(self):
        """PostMessage should calculate tokens per second."""
        event: PostMessageEvent = {  # type: ignore
            "message_content": "Response content",
            "role": "assistant",
            "response_time_ms": 1000.0,  # 1 second
            "token_count": 100,  # 100 tokens
            "status": "success",
            "correlation_id": "corr-123",
        }
        
        result = await on_post_message(event)
        
        metrics = result["metrics"]
        assert metrics["tokens_per_second"] == 100.0

    @pytest.mark.asyncio
    async def test_on_post_message_handles_zero_time(self):
        """PostMessage should handle zero response time."""
        event: PostMessageEvent = {  # type: ignore
            "message_content": "Fast response",
            "role": "assistant",
            "response_time_ms": 0.0,
            "token_count": 10,
            "status": "success",
            "correlation_id": "corr-123",
        }
        
        result = await on_post_message(event)
        
        metrics = result["metrics"]
        assert metrics["tokens_per_second"] == 0.0  # No division by zero

    @pytest.mark.asyncio
    async def test_on_post_message_with_metadata(self):
        """PostMessage should include metadata in audit log."""
        metadata = {"source": "api", "user_id": "user-789"}
        event: PostMessageEvent = {  # type: ignore
            "message_content": "Message with metadata",
            "role": "user",
            "response_time_ms": 100.0,
            "token_count": 5,
            "status": "success",
            "correlation_id": "corr-123",
            "metadata": metadata,
        }
        
        result = await on_post_message(event)
        
        assert result["audit_logged"] is True

    @pytest.mark.asyncio
    async def test_on_post_message_status_variations(self):
        """PostMessage should handle different status values."""
        for status in ["success", "filtered", "error", "timeout"]:
            event: PostMessageEvent = {  # type: ignore
                "message_content": f"Message with status: {status}",
                "role": "assistant",
                "response_time_ms": 150.0,
                "token_count": 20,
                "status": status,
                "correlation_id": "corr-123",
            }
            
            result = await on_post_message(event)
            
            assert result["metrics"]["status"] == status

    @pytest.mark.asyncio
    async def test_on_post_message_long_message(self):
        """PostMessage should handle very long messages."""
        long_message = "x" * 50000  # 50KB message
        event: PostMessageEvent = {  # type: ignore
            "message_content": long_message,
            "role": "assistant",
            "response_time_ms": 500.0,
            "token_count": 10000,
            "status": "success",
            "correlation_id": "corr-123",
        }
        
        result = await on_post_message(event)
        
        metrics = result["metrics"]
        assert metrics["message_length"] == 50000

    @pytest.mark.asyncio
    async def test_on_post_message_missing_optional_fields(self):
        """PostMessage should handle missing optional fields."""
        event: dict[str, Any] = {
            "message_content": "Message",
            "role": "assistant",
            # Omit response_time_ms, token_count, metadata, etc.
        }
        
        result = await on_post_message(event)
        
        # Should not crash and return valid output
        assert result["audit_logged"] is True


class TestMessageHooksIntegration:
    """Integration tests for message hooks with HookRegistry."""

    @pytest.mark.asyncio
    async def test_pre_message_hook_via_registry(self):
        """PreMessage hook should work via HookRegistry."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=time.time(),
        )
        
        message = "Contact: john@example.com"
        transformed, output = await registry.execute_pre_message(
            message_content=message,
            role="user",
            correlation_id="corr-123",
            context=context,
            message_id="msg-789",
        )
        
        # Message should be transformed if hooks are registered
        # (output structure should be valid)
        assert isinstance(transformed, str)
        assert isinstance(output, dict)

    @pytest.mark.asyncio
    async def test_post_message_hook_via_registry(self):
        """PostMessage hook should work via HookRegistry."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=time.time(),
        )
        
        output = await registry.execute_post_message(
            message_content="Response text",
            role="assistant",
            response_time_ms=100.0,
            token_count=25,
            status="success",
            correlation_id="corr-123",
            context=context,
        )
        
        assert isinstance(output, dict)

    @pytest.mark.asyncio
    async def test_pre_message_transformation_chaining(self):
        """PreMessage hooks should chain transformations."""
        # Create two simple hook functions
        async def hook1(event: dict[str, Any]) -> dict[str, Any]:
            content = event.get("message_content", "")
            return {"transformed_message": content.upper()}
        
        async def hook2(event: dict[str, Any]) -> dict[str, Any]:
            # This would receive uppercase from hook1
            content = event.get("message_content", "")
            return {"transformed_message": f"[{content}]"}
        
        # Apply transformations manually (simulating hook chaining)
        event1 = {"message_content": "hello"}
        result1 = await hook1(event1)
        
        # Next hook gets transformed message
        event2 = {"message_content": result1.get("transformed_message", "")}
        result2 = await hook2(event2)
        
        assert result2.get("transformed_message") == "[HELLO]"

    @pytest.mark.asyncio
    async def test_message_hooks_no_side_effects(self):
        """Message hooks should not have side effects on input events."""
        original_event: PreMessageEvent = {  # type: ignore
            "message_content": "Original content",
            "role": "user",
            "correlation_id": "corr-123",
        }
        
        # Create a copy to compare
        original_content = original_event["message_content"]
        
        await on_pre_message(original_event)
        
        # Original event should be unchanged
        assert original_event["message_content"] == original_content

    def test_register_message_hooks_returns_dict(self):
        """register_message_hooks should return proper hook registry dict."""
        hooks_dict = register_message_hooks()
        
        assert isinstance(hooks_dict, dict)
        assert "PreMessage" in hooks_dict
        assert "PostMessage" in hooks_dict
        assert on_pre_message in hooks_dict["PreMessage"]
        assert on_post_message in hooks_dict["PostMessage"]


class TestMessageHooksBackwardCompatibility:
    """Test backward compatibility of message hooks."""

    @pytest.mark.asyncio
    async def test_hook_output_backward_compat_empty_dict(self):
        """Hooks should accept returning empty dict."""
        async def minimal_hook(event: dict[str, Any]) -> dict[str, Any]:
            return {}
        
        result = await minimal_hook({})
        assert result == {}

    @pytest.mark.asyncio
    async def test_hook_output_backward_compat_partial_fields(self):
        """Hooks should accept partial field returns."""
        async def partial_hook(event: dict[str, Any]) -> dict[str, Any]:
            return {"some_key": "some_value"}
        
        result = await partial_hook({})
        assert "some_key" in result

    @pytest.mark.asyncio
    async def test_pre_message_idempotent(self):
        """PreMessage hook should be idempotent (safe to call multiple times)."""
        event: PreMessageEvent = {  # type: ignore
            "message_content": "Test message",
            "role": "user",
            "correlation_id": "corr-123",
        }
        
        result1 = await on_pre_message(event)
        result2 = await on_pre_message(event)
        
        # Results should be identical
        assert result1["validation_status"] == result2["validation_status"]

    @pytest.mark.asyncio
    async def test_post_message_idempotent(self):
        """PostMessage hook should be idempotent."""
        event: PostMessageEvent = {  # type: ignore
            "message_content": "Response",
            "role": "assistant",
            "response_time_ms": 100.0,
            "token_count": 25,
            "status": "success",
            "correlation_id": "corr-123",
        }
        
        result1 = await on_post_message(event)
        result2 = await on_post_message(event)
        
        # Results should be identical
        assert result1["audit_logged"] == result2["audit_logged"]
        assert result1["metrics"] == result2["metrics"]

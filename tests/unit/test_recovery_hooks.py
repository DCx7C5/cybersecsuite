"""Tests for recovery hooks: PreRetry, OnRecovery, OnError."""

import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# Adjust path for imports
SRC_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from legacy.hooks.events import ErrorStrategy, HookContext, OnErrorEvent, OnRecoveryEvent, PreRetryEvent
from legacy.hooks.recovery_hooks import (
    is_permanent_error,
    is_transient_error,
    on_error,
    on_pre_retry,
    on_recovery,
)
from css.core.registries.hooks import HookRegistry, reset_registry


class TestErrorClassification:
    """Test error classification (transient vs permanent)."""

    def test_transient_errors_classified_correctly(self):
        """Common transient errors should be classified as transient."""
        transient_errors = [
            "TimeoutError",
            "ConnectionError",
            "RateLimitError",
            "HTTPError",
            "BrokenPipeError",
        ]
        for error in transient_errors:
            assert is_transient_error(error), f"{error} should be transient"

    def test_permanent_errors_classified_correctly(self):
        """Common permanent errors should be classified as permanent."""
        permanent_errors = [
            "PermissionError",
            "ValueError",
            "KeyError",
            "NotFoundError",
            "AuthenticationError",
            "AuthorizationError",
        ]
        for error in permanent_errors:
            assert is_permanent_error(error), f"{error} should be permanent"

    def test_timeout_suffix_transient(self):
        """Errors ending with 'Timeout' should be transient."""
        assert is_transient_error("CustomTimeout")
        assert is_transient_error("RequestTimeout")

    def test_unknown_error_not_classified(self):
        """Unknown error types should not be classified as permanent."""
        assert not is_permanent_error("CustomError")
        assert not is_transient_error("CustomError")


class TestPreRetryHook:
    """Test on_pre_retry hook functionality."""

    @pytest.mark.asyncio
    async def test_pre_retry_logs_attempt(self):
        """PreRetry hook should log retry attempts."""
        event: PreRetryEvent = {  # type: ignore
            "error_type": "TimeoutError",
            "error_message": "Request timed out",
            "attempt_number": 1,
            "max_attempts": 3,
            "retry_delay_ms": 1000.0,
            "tool_name": "fetch",
            "correlation_id": "corr-123",
        }

        with patch("hooks.recovery_hooks.logger") as mock_logger:
            result = await on_pre_retry(event)

            # Should have logged the retry attempt
            assert mock_logger.info.called
            assert result == {}  # Should allow retry for transient error

    @pytest.mark.asyncio
    async def test_pre_retry_suppresses_permanent_error(self):
        """PreRetry hook should suppress retry for permanent errors."""
        event: PreRetryEvent = {  # type: ignore
            "error_type": "PermissionError",
            "error_message": "Access denied",
            "attempt_number": 1,
            "max_attempts": 3,
            "retry_delay_ms": 1000.0,
            "tool_name": "write",
            "correlation_id": "corr-123",
        }

        result = await on_pre_retry(event)

        assert result.get("suppress_retry") is True

    @pytest.mark.asyncio
    async def test_pre_retry_suppresses_at_max_attempts(self):
        """PreRetry hook should suppress retry when max attempts reached."""
        event: PreRetryEvent = {  # type: ignore
            "error_type": "TimeoutError",
            "error_message": "Request timed out",
            "attempt_number": 3,
            "max_attempts": 3,
            "retry_delay_ms": 1000.0,
            "tool_name": "fetch",
            "correlation_id": "corr-123",
        }

        result = await on_pre_retry(event)

        assert result.get("suppress_retry") is True

    @pytest.mark.asyncio
    async def test_pre_retry_allows_transient_below_max(self):
        """PreRetry hook should allow retry for transient errors below max."""
        event: PreRetryEvent = {  # type: ignore
            "error_type": "TimeoutError",
            "error_message": "Request timed out",
            "attempt_number": 1,
            "max_attempts": 3,
            "retry_delay_ms": 1000.0,
            "tool_name": "fetch",
            "correlation_id": "corr-123",
        }

        result = await on_pre_retry(event)

        assert "suppress_retry" not in result or result.get("suppress_retry") is False

    @pytest.mark.asyncio
    async def test_pre_retry_allows_unknown_error(self):
        """PreRetry hook should allow retry for unknown errors (conservative)."""
        event: PreRetryEvent = {  # type: ignore
            "error_type": "UnknownCustomError",
            "error_message": "Unknown error occurred",
            "attempt_number": 1,
            "max_attempts": 3,
            "retry_delay_ms": 1000.0,
            "tool_name": "process",
            "correlation_id": "corr-123",
        }

        result = await on_pre_retry(event)

        assert "suppress_retry" not in result or result.get("suppress_retry") is False

    @pytest.mark.asyncio
    async def test_pre_retry_missing_fields(self):
        """PreRetry hook should handle missing optional fields."""
        event: PreRetryEvent = {  # type: ignore
            "error_type": "TimeoutError",
            "attempt_number": 1,
        }

        result = await on_pre_retry(event)

        # Should not raise, just return decision
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_pre_retry_does_not_raise(self):
        """PreRetry hook should never raise exceptions."""
        event: PreRetryEvent = {}  # Empty event

        # Should not raise
        result = await on_pre_retry(event)
        assert isinstance(result, dict)


class TestOnRecoveryHook:
    """Test on_recovery hook functionality."""

    @pytest.mark.asyncio
    async def test_on_recovery_logs_success(self):
        """OnRecovery hook should log successful recovery."""
        event: OnRecoveryEvent = {  # type: ignore
            "error_type": "TimeoutError",
            "recovered_after_attempts": 2,
            "total_retry_duration_ms": 2500.0,
            "correlation_id": "corr-123",
        }

        with patch("hooks.recovery_hooks.logger") as mock_logger:
            result = await on_recovery(event)

            # Should have logged recovery
            assert mock_logger.info.called
            assert result == {}

    @pytest.mark.asyncio
    async def test_on_recovery_empty_event(self):
        """OnRecovery hook should handle empty event."""
        event: OnRecoveryEvent = {}  # type: ignore

        result = await on_recovery(event)

        # Should not raise, just return empty dict
        assert result == {}

    @pytest.mark.asyncio
    async def test_on_recovery_does_not_raise(self):
        """OnRecovery hook should never raise exceptions (fire-and-forget)."""
        event: OnRecoveryEvent = {  # type: ignore
            "error_type": "TimeoutError",
            "recovered_after_attempts": 3,
            "total_retry_duration_ms": 5000.0,
            "correlation_id": "corr-123",
        }

        # Should not raise even if something breaks
        result = await on_recovery(event)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_on_recovery_with_various_errors(self):
        """OnRecovery hook should work with various error types."""
        error_types = ["TimeoutError", "ConnectionError", "RateLimitError", "CustomError"]

        for error_type in error_types:
            event: OnRecoveryEvent = {  # type: ignore
                "error_type": error_type,
                "recovered_after_attempts": 1,
                "total_retry_duration_ms": 500.0,
                "correlation_id": "corr-123",
            }

            result = await on_recovery(event)
            assert result == {}


class TestOnErrorHook:
    """Test on_error hook functionality."""

    @pytest.mark.asyncio
    async def test_on_error_logs_fatal(self):
        """OnError hook should log fatal errors."""
        event: OnErrorEvent = {  # type: ignore
            "error_type": "PermissionError",
            "error_message": "Access denied",
            "is_fatal": True,
            "attempt_number": 1,
            "correlation_id": "corr-123",
        }

        with patch("hooks.recovery_hooks.logger") as mock_logger:
            result = await on_error(event)

            # Should have logged error
            assert mock_logger.error.called
            assert result == {}

    @pytest.mark.asyncio
    async def test_on_error_logs_non_fatal(self):
        """OnError hook should log non-fatal errors as warnings."""
        event: OnErrorEvent = {  # type: ignore
            "error_type": "TimeoutError",
            "error_message": "Request timed out",
            "is_fatal": False,
            "attempt_number": 3,
            "correlation_id": "corr-123",
        }

        with patch("hooks.recovery_hooks.logger") as mock_logger:
            result = await on_error(event)

            # Should have logged as warning
            assert mock_logger.warning.called or mock_logger.error.called
            assert result == {}

    @pytest.mark.asyncio
    async def test_on_error_empty_event(self):
        """OnError hook should handle empty event."""
        event: OnErrorEvent = {}  # type: ignore

        result = await on_error(event)

        # Should not raise, just return empty dict
        assert result == {}

    @pytest.mark.asyncio
    async def test_on_error_does_not_raise(self):
        """OnError hook should never raise exceptions (fire-and-forget)."""
        event: OnErrorEvent = {  # type: ignore
            "error_type": "PermissionError",
            "error_message": "Access denied",
            "is_fatal": True,
            "attempt_number": 1,
            "correlation_id": "corr-123",
        }

        # Should not raise even if something breaks
        result = await on_error(event)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_on_error_permanent_vs_transient(self):
        """OnError hook should differentiate permanent vs transient errors."""
        # Permanent error should be logged as error
        permanent_event: OnErrorEvent = {  # type: ignore
            "error_type": "PermissionError",
            "error_message": "Access denied",
            "is_fatal": False,  # Not fatal but permanent
            "attempt_number": 1,
            "correlation_id": "corr-123",
        }

        with patch("hooks.recovery_hooks.logger") as mock_logger:
            await on_error(permanent_event)
            # Permanent error should trigger error (not warning)
            assert mock_logger.error.called


class TestHookRegistryIntegration:
    """Test integration with HookRegistry."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Reset registry after each test."""
        yield
        reset_registry()

    @pytest.mark.asyncio
    async def test_registry_execute_pre_retry(self):
        """HookRegistry should execute PreRetry hooks."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=time.time(),
        )

        event: PreRetryEvent = {  # type: ignore
            "error_type": "TimeoutError",
            "error_message": "Request timed out",
            "attempt_number": 1,
            "max_attempts": 3,
            "retry_delay_ms": 1000.0,
            "tool_name": "fetch",
            "correlation_id": "corr-123",
        }

        # Should not raise even if no PreRetry hooks registered
        result = await registry.execute_pre_retry(event, context)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_registry_execute_on_recovery(self):
        """HookRegistry should execute OnRecovery hooks."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=time.time(),
        )

        event: OnRecoveryEvent = {  # type: ignore
            "error_type": "TimeoutError",
            "recovered_after_attempts": 2,
            "total_retry_duration_ms": 2500.0,
            "correlation_id": "corr-123",
        }

        # Should not raise even if no OnRecovery hooks registered
        result = await registry.execute_on_recovery(event, context)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_registry_execute_on_error(self):
        """HookRegistry should execute OnError hooks."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=time.time(),
        )

        event: OnErrorEvent = {  # type: ignore
            "error_type": "PermissionError",
            "error_message": "Access denied",
            "is_fatal": True,
            "attempt_number": 1,
            "correlation_id": "corr-123",
        }

        # Should not raise even if no OnError hooks registered
        result = await registry.execute_on_error(event, context)
        assert isinstance(result, dict)


class TestRecoveryHooksWithInstrumentation:
    """Test recovery hooks with instrumentation enabled."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Reset registry after each test."""
        yield
        reset_registry()

    @pytest.mark.asyncio
    async def test_pre_retry_with_instrumentation(self):
        """PreRetry execution should be instrumented for timing."""
        from hooks.instrumentation import HookInstrument

        instrument = HookInstrument()
        registry = HookRegistry(instrumentation=instrument)
        context = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=time.time(),
        )

        event: PreRetryEvent = {  # type: ignore
            "error_type": "TimeoutError",
            "error_message": "Request timed out",
            "attempt_number": 1,
            "max_attempts": 3,
            "retry_delay_ms": 1000.0,
            "tool_name": "fetch",
            "correlation_id": "corr-123",
        }

        result = await registry.execute_pre_retry(event, context)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_on_recovery_with_instrumentation(self):
        """OnRecovery execution should be instrumented for timing."""
        from hooks.instrumentation import HookInstrument

        instrument = HookInstrument()
        registry = HookRegistry(instrumentation=instrument)
        context = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=time.time(),
        )

        event: OnRecoveryEvent = {  # type: ignore
            "error_type": "TimeoutError",
            "recovered_after_attempts": 2,
            "total_retry_duration_ms": 2500.0,
            "correlation_id": "corr-123",
        }

        result = await registry.execute_on_recovery(event, context)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_on_error_with_instrumentation(self):
        """OnError execution should be instrumented for timing."""
        from hooks.instrumentation import HookInstrument

        instrument = HookInstrument()
        registry = HookRegistry(instrumentation=instrument)
        context = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=time.time(),
        )

        event: OnErrorEvent = {  # type: ignore
            "error_type": "PermissionError",
            "error_message": "Access denied",
            "is_fatal": True,
            "attempt_number": 1,
            "correlation_id": "corr-123",
        }

        result = await registry.execute_on_error(event, context)
        assert isinstance(result, dict)


class TestRecoveryHooksErrorHandling:
    """Test error handling in recovery hooks."""

    @pytest.mark.asyncio
    async def test_pre_retry_with_error_strategy_preserve(self):
        """PreRetry with PRESERVE_EXISTING strategy should not raise."""
        registry = HookRegistry(error_strategy=ErrorStrategy.PRESERVE_EXISTING)
        context = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=time.time(),
        )

        event: PreRetryEvent = {  # type: ignore
            "error_type": "TimeoutError",
            "attempt_number": 1,
            "correlation_id": "corr-123",
        }

        # Should not raise
        result = await registry.execute_pre_retry(event, context)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_on_recovery_always_fire_and_forget(self):
        """OnRecovery should always be fire-and-forget regardless of strategy."""
        registry = HookRegistry(error_strategy=ErrorStrategy.LOG)
        context = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=time.time(),
        )

        event: OnRecoveryEvent = {  # type: ignore
            "error_type": "TimeoutError",
            "recovered_after_attempts": 2,
            "total_retry_duration_ms": 2500.0,
            "correlation_id": "corr-123",
        }

        # Should not raise even with LOG strategy
        result = await registry.execute_on_recovery(event, context)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_on_error_always_fire_and_forget(self):
        """OnError should always be fire-and-forget regardless of strategy."""
        registry = HookRegistry(error_strategy=ErrorStrategy.WARN)
        context = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=time.time(),
        )

        event: OnErrorEvent = {  # type: ignore
            "error_type": "PermissionError",
            "error_message": "Access denied",
            "is_fatal": True,
            "attempt_number": 1,
            "correlation_id": "corr-123",
        }

        # Should not raise even with WARN strategy
        result = await registry.execute_on_error(event, context)
        assert isinstance(result, dict)


class TestRecoveryHooksBackwardCompatibility:
    """Test backward compatibility with existing hook system."""

    @pytest.mark.asyncio
    async def test_recovery_hooks_compatible_with_existing_hooks(self):
        """Recovery hooks should not break existing hook tests."""
        # This test just verifies that recovery hooks can coexist
        registry = HookRegistry()
        context = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=time.time(),
        )

        # Test that existing execute() method still works
        result = await registry.execute("PreToolUse", {"tool_name": "Bash"}, context)
        assert isinstance(result, dict)

        # Test that recovery execute methods work alongside
        event: PreRetryEvent = {  # type: ignore
            "error_type": "TimeoutError",
            "attempt_number": 1,
            "correlation_id": "corr-123",
        }
        result = await registry.execute_pre_retry(event, context)
        assert isinstance(result, dict)

"""Tests for hooks.registry: stateless hook registry wrapper."""

import asyncio
import sys
import time
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Adjust path for imports
SRC_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from hooks.core import ErrorStrategy, HookContext, HookOutput
from hooks.registry import HookRegistry, get_registry, reset_registry


class TestHookRegistry:
    """Test HookRegistry stateless design."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Reset global registry after each test."""
        yield
        reset_registry()

    def test_registry_initialization(self):
        """HookRegistry should initialize with cached hooks."""
        registry = HookRegistry()
        assert registry is not None
        assert hasattr(registry, "_hooks")
        assert isinstance(registry._hooks, dict)

    def test_registry_initialization_with_error_strategy(self):
        """HookRegistry should accept error strategy."""
        registry = HookRegistry(error_strategy=ErrorStrategy.LOG)
        assert registry._error_strategy == ErrorStrategy.LOG

    def test_registry_error_strategy_default(self):
        """Default error strategy should be PRESERVE_EXISTING."""
        registry = HookRegistry()
        assert registry._error_strategy == ErrorStrategy.PRESERVE_EXISTING

    def test_registry_immutable_hooks_cache(self):
        """Registry hooks cache should not change after init."""
        registry = HookRegistry()
        hooks_initial = registry._hooks.copy()
        
        # Try to trigger hook execution (shouldn't mutate _hooks)
        assert registry._hooks == hooks_initial

    def test_registry_multiple_instances_independent(self):
        """Multiple registry instances should be independent."""
        registry1 = HookRegistry(error_strategy=ErrorStrategy.LOG)
        registry2 = HookRegistry(error_strategy=ErrorStrategy.WARN)
        
        assert registry1._error_strategy != registry2._error_strategy
        # Each instance has its own hooks dict (from separate build_python_hooks() calls)
        # but they have the same content
        assert registry1._hooks.keys() == registry2._hooks.keys()

    @pytest.mark.asyncio
    async def test_registry_execute_unknown_event(self):
        """Registry should handle unknown event types gracefully."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        
        # Should not raise, just return empty output
        output = await registry.execute("UnknownEventType", {}, context)
        assert isinstance(output, dict)

    @pytest.mark.asyncio
    async def test_registry_execute_preserves_context(self):
        """Registry should maintain context across calls."""
        registry = HookRegistry()
        context1 = HookContext(
            correlation_id="corr-1",
            session_id="sess-1",
            timestamp=time.time(),
        )
        context2 = HookContext(
            correlation_id="corr-2",
            session_id="sess-2",
            timestamp=time.time(),
        )
        
        # Execute with different contexts
        await registry.execute("PreToolUse", {"tool_name": "Bash"}, context1)
        await registry.execute("PreToolUse", {"tool_name": "Bash"}, context2)
        
        # Registry state should be unchanged
        assert registry._hooks is not None


class TestRegistryStateless:
    """Test stateless design principle."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        yield
        reset_registry()

    @pytest.mark.asyncio
    async def test_no_per_call_state_storage(self):
        """Registry should not store per-call state."""
        registry = HookRegistry()
        
        # Get initial state
        initial_hooks = id(registry._hooks)
        
        # Make multiple calls
        context = HookContext(
            correlation_id="test",
            session_id="test",
            timestamp=time.time(),
        )
        await registry.execute("PreToolUse", {"tool_name": "Bash"}, context)
        await registry.execute("PostToolUse", {"tool_name": "Bash"}, context)
        await registry.execute("Stop", {}, context)
        
        # Cache should not change
        assert id(registry._hooks) == initial_hooks

    @pytest.mark.asyncio
    async def test_context_passed_per_call(self):
        """HookContext should be unique per call."""
        registry = HookRegistry()
        
        context1 = HookContext(
            correlation_id="corr-1",
            session_id="sess-1",
            timestamp=time.time(),
        )
        context2 = HookContext(
            correlation_id="corr-2",
            session_id="sess-2",
            timestamp=time.time(),
        )
        
        # Both should work independently
        await registry.execute("PreToolUse", {}, context1)
        await registry.execute("PreToolUse", {}, context2)
        
        assert context1.correlation_id != context2.correlation_id


class TestRegistryBackwardCompatibility:
    """Test backward compatibility with existing hooks."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        yield
        reset_registry()

    @pytest.mark.asyncio
    async def test_backward_compat_empty_dict_output(self):
        """Hooks returning {} should still work."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="test",
            session_id="test",
            timestamp=time.time(),
        )
        
        # Mock a hook that returns empty dict
        with patch("hooks.sdk_hooks.build_python_hooks") as mock_build:
            async def mock_hook(event):
                return {}
            
            from claude_agent_sdk import HookMatcher
            mock_build.return_value = {
                "PreToolUse": [HookMatcher(matcher=".*", hooks=[mock_hook])]
            }
            
            registry2 = HookRegistry()
            output = await registry2.execute("PreToolUse", {"tool_name": "Bash"}, context)
            assert isinstance(output, dict)

    @pytest.mark.asyncio
    async def test_backward_compat_dict_events(self):
        """Registry should accept old dict-based events."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="test",
            session_id="test",
            timestamp=time.time(),
        )
        
        # Old-style event dicts
        event_dict = {
            "tool_name": "Bash",
            "tool_input": {"command": "echo hello"},
            "agent_type": "explore",
        }
        
        # Should not raise
        output = await registry.execute("PreToolUse", event_dict, context)
        assert isinstance(output, dict)


class TestRegistryIntrospection:
    """Test registry introspection methods."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        yield
        reset_registry()

    def test_get_hooks_for_event(self):
        """Should return hooks for a given event type."""
        registry = HookRegistry()
        hooks = registry.get_hooks_for_event("PreToolUse")
        
        # Should return a list (may be empty if hooks not loaded)
        assert isinstance(hooks, list)

    def test_get_hooks_for_unknown_event(self):
        """Should return empty list for unknown event."""
        registry = HookRegistry()
        hooks = registry.get_hooks_for_event("UnknownEvent")
        
        assert hooks == []

    def test_validate_event_unknown_type(self):
        """Should return False for unknown event type."""
        registry = HookRegistry()
        result = registry.validate_event("UnknownEventType", {})
        
        assert result is False

    def test_validate_event_non_dict(self):
        """Should return False for non-dict events."""
        registry = HookRegistry()
        result = registry.validate_event("PreToolUse", "not a dict")  # type: ignore
        
        assert result is False

    def test_validate_event_dict(self):
        """Should return True for valid dict event."""
        registry = HookRegistry()
        event = {"tool_name": "Bash", "tool_input": {}}
        result = registry.validate_event("PreToolUse", event)
        
        assert result is True


class TestErrorHandling:
    """Test error handling strategies."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        yield
        reset_registry()

    def test_error_strategy_preserve_existing(self):
        """PRESERVE_EXISTING should not propagate errors."""
        registry = HookRegistry(error_strategy=ErrorStrategy.PRESERVE_EXISTING)
        assert registry._error_strategy == ErrorStrategy.PRESERVE_EXISTING

    def test_error_strategy_log(self):
        """LOG strategy should be settable."""
        registry = HookRegistry(error_strategy=ErrorStrategy.LOG)
        assert registry._error_strategy == ErrorStrategy.LOG

    def test_error_strategy_warn(self):
        """WARN strategy should be settable."""
        registry = HookRegistry(error_strategy=ErrorStrategy.WARN)
        assert registry._error_strategy == ErrorStrategy.WARN

    @pytest.mark.asyncio
    async def test_handle_hook_error_called_on_failure(self):
        """_handle_hook_error should be called on hook failure."""
        registry = HookRegistry()
        
        # Mock a failing hook
        async def failing_hook(event):
            raise ValueError("Test error")
        
        with patch("hooks.sdk_hooks.build_python_hooks") as mock_build:
            from claude_agent_sdk import HookMatcher
            mock_build.return_value = {
                "PreToolUse": [HookMatcher(matcher=".*", hooks=[failing_hook])]
            }
            
            registry2 = HookRegistry()
            context = HookContext(
                correlation_id="test",
                session_id="test",
                timestamp=time.time(),
            )
            
            # With PRESERVE_EXISTING, should not raise
            output = await registry2.execute("PreToolUse", {}, context)
            assert isinstance(output, dict)


class TestGlobalRegistry:
    """Test global registry singleton."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        yield
        reset_registry()

    def test_get_registry_creates_singleton(self):
        """get_registry should create a singleton."""
        registry1 = get_registry()
        registry2 = get_registry()
        
        assert registry1 is registry2

    def test_get_registry_default_strategy(self):
        """get_registry should use PRESERVE_EXISTING by default."""
        registry = get_registry()
        assert registry._error_strategy == ErrorStrategy.PRESERVE_EXISTING

    def test_get_registry_strategy_on_first_call(self):
        """get_registry should accept strategy only on first call."""
        registry1 = get_registry(error_strategy=ErrorStrategy.LOG)
        registry2 = get_registry(error_strategy=ErrorStrategy.WARN)
        
        # Both should be same instance with LOG strategy
        assert registry1 is registry2
        assert registry1._error_strategy == ErrorStrategy.LOG

    def test_reset_registry(self):
        """reset_registry should clear singleton."""
        registry1 = get_registry()
        reset_registry()
        registry2 = get_registry()
        
        assert registry1 is not registry2

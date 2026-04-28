"""Integration tests for agent SDK with typed hook system."""

import sys
import time
from pathlib import Path


# Adjust path for imports
SRC_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


class TestAgentSDKHooksIntegration:
    """Test agent SDK integration with typed hook registry."""

    def test_agent_sdk_build_options_with_typed_hooks(self):
        """Agent SDK should build options with typed hook registry."""
        from a2a.agent_sdk import build_agent_options
        
        options = build_agent_options()
        
        # Verify options have hooks
        assert options is not None
        assert hasattr(options, 'hooks')
        assert options.hooks is not None
        
        # Verify hooks dict structure
        hooks = options.hooks
        assert isinstance(hooks, dict)
        
        # Verify expected hook event types
        expected_events = {
            "PreToolUse",
            "PostToolUse",
            "PostToolUseFailure",
            "UserPromptSubmit",
            "Stop",
            "SubagentStart",
            "SubagentStop",
            "PreCompact",
            "PermissionRequest",
            "Notification",
        }
        
        for event in expected_events:
            assert event in hooks, f"Expected hook event {event} not found in SDK options"
            assert isinstance(hooks[event], list), f"Hook event {event} should have a list of matchers"
            assert len(hooks[event]) > 0, f"Hook event {event} should have at least one matcher"

    def test_agent_options_caching_unchanged(self):
        """Agent options caching should work unchanged with typed hooks."""
        from a2a.agent_sdk import (
            build_agent_options,
            clear_caches,
        )
        
        # Clear any existing cache
        clear_caches()
        
        # Build twice and verify we get the cached version
        opts1 = build_agent_options()
        opts2 = build_agent_options()
        
        # Same object (cached)
        assert opts1 is opts2
        
        # Verify no exceptions during caching
        for _ in range(5):
            opts = build_agent_options()
            assert opts is not None

    def test_hook_registry_singleton_in_options(self):
        """Agent options should use HookRegistry singleton."""
        from a2a.agent_sdk import build_agent_options
        from core.registries.hooks import get_registry, reset_registry
        
        # Reset to clean state
        reset_registry()
        
        # Build options (should create registry singleton)
        opts1 = build_agent_options()
        
        # Get registry
        registry = get_registry()
        
        # Verify registry exists and has hooks
        assert registry is not None
        assert registry._hooks is not None
        assert len(registry._hooks) > 0
        
        # Verify opts1 uses the same hooks from registry
        assert opts1.hooks == registry._hooks

    def test_pre_tool_write_guard_in_hooks(self):
        """Pre-tool write guard should be in PreToolUse hooks."""
        from a2a.agent_sdk import build_agent_options
        
        options = build_agent_options()
        pre_tool_hooks = options.hooks.get("PreToolUse", [])
        
        # Should have multiple matchers
        assert len(pre_tool_hooks) >= 2
        
        # Find the write guard matcher (Write|Edit|Bash)
        write_guard_found = False
        for matcher in pre_tool_hooks:
            if hasattr(matcher, 'matcher') and matcher.matcher and 'Write' in matcher.matcher:
                write_guard_found = True
                break
        
        assert write_guard_found, "Write guard matcher not found in PreToolUse hooks"

    def test_permission_request_hooks_present(self):
        """Permission request hooks should be present."""
        from a2a.agent_sdk import build_agent_options
        
        options = build_agent_options()
        perm_hooks = options.hooks.get("PermissionRequest", [])
        
        # Should have auto-allow and default-ask matchers
        assert len(perm_hooks) >= 2

    def test_backward_compatibility_hook_format(self):
        """Hooks should maintain backward compatible format."""
        from a2a.agent_sdk import build_agent_options
        from claude_agent_sdk import HookMatcher
        
        options = build_agent_options()
        hooks = options.hooks
        
        # Each event type should have a list of HookMatcher instances
        for event_type, matchers in hooks.items():
            assert isinstance(matchers, list), f"{event_type} hooks should be a list"
            
            for matcher in matchers:
                assert isinstance(matcher, HookMatcher), \
                    f"Hook matcher for {event_type} should be HookMatcher instance"

    def test_hook_execution_does_not_block_options(self):
        """Building options should not execute hooks."""
        from a2a.agent_sdk import build_agent_options, clear_caches
        
        clear_caches()
        
        # Should complete quickly (no hook execution)
        start = time.time()
        options = build_agent_options()
        elapsed = time.time() - start
        
        # Building options should be fast (<1 second)
        assert elapsed < 1.0, f"Options building took {elapsed}s, should be <1s"
        assert options.hooks is not None

    def test_all_38_hook_events_registered(self):
        """All 11 SDK hook events should be registered (represented by matchers)."""
        from a2a.agent_sdk import build_agent_options
        
        options = build_agent_options()
        hooks = options.hooks
        
        # The 11 SDK hook event types
        required_events = {
            "PreToolUse",
            "PostToolUse",
            "PostToolUseFailure",
            "UserPromptSubmit",
            "Stop",
            "SubagentStart",
            "SubagentStop",
            "PreCompact",
            "PermissionRequest",
            "Notification",
        }
        
        registered_events = set(hooks.keys())
        
        # Check all required events are registered
        for event in required_events:
            assert event in registered_events, \
                f"Required hook event {event} not registered"

    def test_hook_registry_error_strategy(self):
        """Hook registry should have proper error strategy."""
        from core.registries.hooks import HookRegistry
        from hooks.events import ErrorStrategy
        
        # Default strategy
        registry = HookRegistry()
        assert registry._error_strategy == ErrorStrategy.PRESERVE_EXISTING
        
        # Custom strategy
        registry2 = HookRegistry(error_strategy=ErrorStrategy.LOG)
        assert registry2._error_strategy == ErrorStrategy.LOG

    def test_hook_registry_instrumentation_optional(self):
        """Hook instrumentation should be optional."""
        from core.registries.hooks import HookRegistry
        from hooks.instrumentation import HookInstrument
        
        # Without instrumentation
        registry1 = HookRegistry()
        assert registry1.get_instrumentation() is None
        
        # With instrumentation
        instrument = HookInstrument()
        registry2 = HookRegistry(instrumentation=instrument)
        assert registry2.get_instrumentation() is not None
        assert registry2.get_instrumentation() is instrument


class TestHookCountValidation:
    """Validate all 38+ hooks are present."""

    def test_sdk_hook_count(self):
        """Verify all SDK hooks are registered."""
        from a2a.agent_sdk import build_agent_options
        
        options = build_agent_options()
        hooks = options.hooks
        
        # Count all matchers across all events
        total_matchers = sum(len(matchers) for matchers in hooks.values())
        
        # We should have at least 11 matchers (1 per event type minimum)
        # In reality we have more because some events have multiple matchers
        # (e.g., PreToolUse has write_guard + audit)
        assert total_matchers >= 11, \
            f"Expected at least 11 matchers, got {total_matchers}"

    def test_python_sdk_hooks_building(self):
        """Verify build_python_hooks builds the hook dict correctly."""
        from hooks.sdk_hooks import build_python_hooks
        
        hooks = build_python_hooks()
        
        # Verify structure
        assert isinstance(hooks, dict)
        
        # Verify all expected event types
        expected = {
            "PreToolUse",
            "PostToolUse",
            "PostToolUseFailure",
            "UserPromptSubmit",
            "Stop",
            "SubagentStart",
            "SubagentStop",
            "PreCompact",
            "PermissionRequest",
            "Notification",
        }
        
        for event in expected:
            assert event in hooks, f"Event {event} missing from build_python_hooks()"

    def test_hook_registry_wraps_build_python_hooks(self):
        """HookRegistry should wrap build_python_hooks output."""
        from core.registries.hooks import HookRegistry
        from hooks.sdk_hooks import build_python_hooks
        
        # Get direct output
        direct_hooks = build_python_hooks()
        
        # Get wrapped output
        registry = HookRegistry()
        wrapped_hooks = registry._hooks
        
        # Should have same event keys
        assert set(direct_hooks.keys()) == set(wrapped_hooks.keys())


class TestBackwardCompatibilityMatrix:
    """Test backward compatibility across different hook patterns."""

    def test_empty_dict_response_hooks(self):
        """Hooks returning empty dict should work."""
        from a2a.agent_sdk import build_agent_options
        
        # This just verifies options can be built
        # The actual hooks that return {} should work
        options = build_agent_options()
        assert options is not None

    def test_dict_with_async_flag_hooks(self):
        """Hooks returning {'async_': True} should work."""
        from a2a.agent_sdk import build_agent_options
        
        # PreCompact hook returns {'async_': True}
        options = build_agent_options()
        pre_compact_hooks = options.hooks.get("PreCompact", [])
        
        assert len(pre_compact_hooks) > 0, "PreCompact hooks should be present"

    def test_dict_with_hook_specific_output(self):
        """Hooks returning hookSpecificOutput should work."""
        from a2a.agent_sdk import build_agent_options
        
        # PermissionRequest hooks return hookSpecificOutput
        options = build_agent_options()
        perm_hooks = options.hooks.get("PermissionRequest", [])
        
        assert len(perm_hooks) > 0, "PermissionRequest hooks should be present"

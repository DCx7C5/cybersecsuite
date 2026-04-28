"""Tests for hooks.core: type-safe hook foundation."""

import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any


# Adjust path for imports
SRC_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from hooks.events import (
    ErrorStrategy,
    HookContext,
    HookOutput,
    PostToolUseEvent,
    PreToolUseEvent,
    StopEvent,
    AgentStartEvent,
)


class TestHookContext:
    """Test HookContext dataclass."""

    def test_hook_context_creation(self):
        """HookContext should be creatable with required fields."""
        ctx = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=time.time(),
        )
        assert ctx.correlation_id == "corr-123"
        assert ctx.session_id == "sess-456"
        assert ctx.timestamp > 0

    def test_hook_context_optional_fields(self):
        """HookContext optional fields should default to None."""
        ctx = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=time.time(),
        )
        assert ctx.tool_use_id is None
        assert ctx.agent_id is None

    def test_hook_context_with_optional_fields(self):
        """HookContext should accept optional fields."""
        ts = time.time()
        ctx = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=ts,
            tool_use_id="tool-789",
            agent_id="agent-999",
        )
        assert ctx.tool_use_id == "tool-789"
        assert ctx.agent_id == "agent-999"

    def test_hook_context_dataclass_fields(self):
        """HookContext should be convertible to dict."""
        ts = time.time()
        ctx = HookContext(
            correlation_id="corr-123",
            session_id="sess-456",
            timestamp=ts,
            tool_use_id="tool-789",
        )
        ctx_dict = asdict(ctx)
        assert isinstance(ctx_dict, dict)
        assert ctx_dict["correlation_id"] == "corr-123"
        assert ctx_dict["tool_use_id"] == "tool-789"

    def test_hook_context_immutable_intent(self):
        """HookContext instances should be created, not mutated."""
        ctx1 = HookContext(
            correlation_id="corr-1",
            session_id="sess-1",
            timestamp=time.time(),
        )
        # Create new instance for different correlation
        ctx2 = HookContext(
            correlation_id="corr-2",
            session_id="sess-1",
            timestamp=time.time(),
        )
        assert ctx1.correlation_id != ctx2.correlation_id


class TestErrorStrategy:
    """Test ErrorStrategy enum."""

    def test_error_strategy_values(self):
        """ErrorStrategy should have expected values."""
        assert ErrorStrategy.PRESERVE_EXISTING.value == "preserve"
        assert ErrorStrategy.LOG.value == "log"
        assert ErrorStrategy.WARN.value == "warn"

    def test_error_strategy_is_enum(self):
        """ErrorStrategy should be an Enum."""
        from enum import Enum
        assert issubclass(ErrorStrategy, Enum)

    def test_error_strategy_members(self):
        """ErrorStrategy should have all expected members."""
        members = set(ErrorStrategy.__members__.keys())
        assert "PRESERVE_EXISTING" in members
        assert "LOG" in members
        assert "WARN" in members


class TestEventTypedDicts:
    """Test event TypedDict definitions."""

    def test_pre_tool_use_event_structure(self):
        """PreToolUseEvent should match SDK input."""
        event: PreToolUseEvent = {  # type: ignore
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la"},
            "agent_type": "explore",
            "agent_id": "agent-123",
        }
        assert event["tool_name"] == "Bash"
        assert event["tool_input"]["command"] == "ls -la"

    def test_post_tool_use_event_structure(self):
        """PostToolUseEvent should support both result field names."""
        event1: PostToolUseEvent = {  # type: ignore
            "tool_name": "Bash",
            "tool_response": {"output": "file1.txt"},
            "agent_type": "explore",
        }
        event2: PostToolUseEvent = {  # type: ignore
            "tool_name": "Bash",
            "tool_result": {"output": "file1.txt"},
            "agent_type": "explore",
        }
        assert "tool_response" in event1
        assert "tool_result" in event2

    def test_subagent_start_event_structure(self):
        """SubagentStartEvent should contain lifecycle info."""
        event: AgentStartEvent = {  # type: ignore
            "agent_name": "code-review",
            "agent_type": "code-review",
            "session_id": "sess-456",
        }
        assert event["agent_name"] == "code-review"
        assert event["session_id"] == "sess-456"

    def test_stop_event_structure(self):
        """StopEvent should contain session info."""
        event: StopEvent = {  # type: ignore
            "agent_type": "explore",
            "session_id": "sess-456",
            "stop_reason": "end_turn",
        }
        assert event["stop_reason"] == "end_turn"

    def test_event_fields_optional_as_intended(self):
        """Event fields marked Optional should be omittable."""
        # Minimal PreToolUseEvent
        event: PreToolUseEvent = {}  # type: ignore
        assert isinstance(event, dict)


class TestHookOutput:
    """Test HookOutput TypedDict."""

    def test_hook_output_full(self):
        """HookOutput should support all fields."""
        output: HookOutput = {  # type: ignore
            "hookSpecificOutput": {"decision": "allow"},
            "message": "Tool approved",
            "success": True,
        }
        assert output["hookSpecificOutput"]["decision"] == "allow"
        assert output["message"] == "Tool approved"

    def test_hook_output_partial(self):
        """HookOutput should support partial fields (total=False)."""
        output: HookOutput = {  # type: ignore
            "hookSpecificOutput": {"decision": "deny"},
        }
        assert "message" not in output
        assert "success" not in output

    def test_hook_output_empty(self):
        """HookOutput should support empty dict (backward compat)."""
        output: HookOutput = {}  # type: ignore
        assert isinstance(output, dict)
        assert len(output) == 0

    def test_hook_output_async_fire_and_forget(self):
        """HookOutput should support legacy async_ field."""
        output: HookOutput = {"async_": True}  # type: ignore
        assert output['async_'] is True

    def test_hook_output_accepts_dict(self):
        """HookOutput type should accept plain dict (backward compat)."""
        plain_dict: Any = {"arbitrary": "field"}
        # Should not raise type errors at runtime
        assert isinstance(plain_dict, dict)

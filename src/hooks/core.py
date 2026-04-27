"""Type-safe hook system foundation using TypedDicts and dataclasses.

This module provides the type contracts for the hook system WITHOUT changing
any hook behavior. It defines:
- HookContext: contextual metadata passed to every hook
- ErrorStrategy: error handling semantics
- Event TypedDicts: input/output schemas for each event type
- HookOutput: standardized hook response type

NO Pydantic. NO runtime validation (yet). Pure typing annotations.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, TypedDict


# ── HookContext ───────────────────────────────────────────────────────────
@dataclass
class HookContext:
    """Metadata passed to every hook execution.
    
    Attributes:
        correlation_id: Unique request correlation ID (links logs across services)
        session_id: CyberSecSuite session ID
        timestamp: Hook execution start timestamp (seconds since epoch)
        tool_use_id: Claude SDK tool_use_id (optional, may not apply to all hooks)
        agent_id: Agent identifier (optional, may not apply to all hooks)
    """
    correlation_id: str
    session_id: str
    timestamp: float
    tool_use_id: Optional[str] = None
    agent_id: Optional[str] = None


# ── Error Handling Strategy ────────────────────────────────────────────────
class ErrorStrategy(Enum):
    """How to handle errors in hook execution.
    
    Values:
        PRESERVE_EXISTING: Don't break on hook failure (default, safest)
        LOG: Log errors to audit but don't propagate
        WARN: Log warnings to audit but don't propagate
    """
    PRESERVE_EXISTING = "preserve"
    LOG = "log"
    WARN = "warn"


# ── Event TypedDicts ──────────────────────────────────────────────────────

class PreToolUseEvent(TypedDict, total=False):
    """PreToolUse event from SDK.
    
    Input fields:
        tool_name: Name of tool being called
        tool_input: Arguments to the tool
        agent_type: Agent name (e.g., "explore", "code-review")
        agent_id: Session-scoped agent identifier
    
    Expected output: HookOutput with permissionDecision if blocking.
    
    Error handling: PRESERVE_EXISTING - hook failure doesn't block tool execution.
    """
    tool_name: str
    tool_input: dict[str, Any]
    agent_type: str
    agent_id: str
    hook_event_name: str


class PostToolUseEvent(TypedDict, total=False):
    """PostToolUse event from SDK.
    
    Input fields:
        tool_name: Name of tool that was called
        tool_response: Output from the tool
        tool_result: Alternative field name for output
        agent_type: Agent name
    
    Expected output: HookOutput with audit metadata.
    
    Error handling: PRESERVE_EXISTING - fire-and-forget logging.
    """
    tool_name: str
    tool_response: Any
    tool_result: Any
    agent_type: str
    hook_event_name: str


class PostToolUseFailureEvent(TypedDict, total=False):
    """PostToolUseFailure event from SDK.
    
    Input fields:
        tool_name: Name of tool that failed
        error: Error message or exception
        message: Alternative field for error details
        agent_type: Agent name
    
    Expected output: HookOutput with error audit.
    
    Error handling: PRESERVE_EXISTING - logging only, no propagation.
    """
    tool_name: str
    error: str
    message: str
    agent_type: str
    hook_event_name: str


class UserPromptSubmitEvent(TypedDict, total=False):
    """UserPromptSubmit event from SDK.
    
    Input fields:
        messages: List of conversation messages
        model: Model identifier
        system_prompt: System prompt text
    
    Expected output: HookOutput with additionalContext in hookSpecificOutput.
    
    Error handling: PRESERVE_EXISTING - missing context is acceptable.
    """
    messages: list[dict[str, Any]]
    model: str
    system_prompt: str
    hook_event_name: str


class StopEvent(TypedDict, total=False):
    """Stop event from SDK.
    
    Input fields:
        agent_type: Agent name
        session_id: Session identifier
        stop_reason: Reason for stop (e.g., "max_tokens", "end_turn")
    
    Expected output: HookOutput with session snapshot.
    
    Error handling: PRESERVE_EXISTING - snapshot creation is best-effort.
    """
    agent_type: str
    session_id: str
    stop_reason: str
    hook_event_name: str


class SubagentStartEvent(TypedDict, total=False):
    """SubagentStart event from SDK.
    
    Input fields:
        agent_name: Subagent identifier
        agent_type: Subagent type/role
        session_id: Parent session ID
    
    Expected output: HookOutput with lifecycle audit.
    
    Error handling: PRESERVE_EXISTING - tracking failures don't impact execution.
    """
    agent_name: str
    agent_type: str
    session_id: str
    hook_event_name: str


class SubagentStopEvent(TypedDict, total=False):
    """SubagentStop event from SDK.
    
    Input fields:
        agent_name: Subagent identifier
        agent_type: Subagent type/role
        session_id: Parent session ID
    
    Expected output: HookOutput with lifecycle audit.
    
    Error handling: PRESERVE_EXISTING - tracking failures don't impact execution.
    """
    agent_name: str
    agent_type: str
    session_id: str
    hook_event_name: str


class PreCompactEvent(TypedDict, total=False):
    """PreCompact event from SDK.
    
    Input fields:
        agent_type: Agent name
        tokens_in_context: Number of tokens before compact
    
    Expected output: HookOutput with async audit (fire-and-forget).
    
    Error handling: PRESERVE_EXISTING - pre-compact logging is optional.
    """
    agent_type: str
    tokens_in_context: int
    hook_event_name: str


class PermissionRequestEvent(TypedDict, total=False):
    """PermissionRequest event from SDK.
    
    Input fields:
        tool_name: Tool requiring permission
        tool_input: Arguments to tool
        action: Action type (e.g., "read", "write", "execute")
    
    Expected output: HookOutput with permissionDecision in hookSpecificOutput.
    
    Error handling: PRESERVE_EXISTING - permission denial is not an error,
                    just a decision. Hook failure defaults to ask/deny.
    """
    tool_name: str
    tool_input: dict[str, Any]
    action: str
    hook_event_name: str


class NotificationEvent(TypedDict, total=False):
    """Notification event from SDK.
    
    Input fields:
        message: Notification message text
        text: Alternative field for message
        hook_event_name: Event name
    
    Expected output: HookOutput with D-Bus notification metadata.
    
    Error handling: PRESERVE_EXISTING - notification failures don't affect core.
    """
    message: str
    text: str
    hook_event_name: str


# Union of all event types for dispatch
EventType = (
    PreToolUseEvent |
    PostToolUseEvent |
    PostToolUseFailureEvent |
    UserPromptSubmitEvent |
    StopEvent |
    SubagentStartEvent |
    SubagentStopEvent |
    PreCompactEvent |
    PermissionRequestEvent |
    NotificationEvent
)


# ── Hook Output ────────────────────────────────────────────────────────────

class HookOutput(TypedDict, total=False):
    """Standardized hook response type.
    
    Hook functions return this type (or compatible dict) after execution.
    
    Fields:
        hookSpecificOutput: Hook-specific return data (e.g., permissionDecision)
        message: Optional user-facing message
        success: Optional success indicator
    
    Backward Compatibility:
        Existing hooks returning plain {} are still valid (empty output).
        Hooks returning {'async_': True} for fire-and-forget are compatible.
    """
    hookSpecificOutput: dict[str, Any]
    message: str
    success: bool

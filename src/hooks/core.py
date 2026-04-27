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


class AgentStartEvent(TypedDict, total=False):
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


class AgentStopEvent(TypedDict, total=False):
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


class PreStreamingEvent(TypedDict, total=False):
    """PreStreaming event: before streaming response starts.
    
    Input fields:
        correlation_id: Unique request correlation ID
        session_id: CyberSecSuite session ID
        model: Model identifier (e.g., "claude-3.5-sonnet")
        token_count_estimate: Estimated total tokens in response (optional)
        hook_event_name: Event name
    
    Expected output: HookOutput with stream configuration in hookSpecificOutput.
    
    Error handling: PRESERVE_EXISTING - pre-stream setup failures don't block streaming.
    
    Use Cases:
        - Initialize token collectors/aggregators
        - Log streaming start with metadata
        - Adjust monitoring based on estimated token count
    """
    correlation_id: str
    session_id: str
    model: str
    token_count_estimate: Optional[int]
    hook_event_name: str


class StreamingTokenEvent(TypedDict, total=False):
    """StreamingToken event: each token/chunk arrives (per-token hook).
    
    Input fields:
        token: The token/chunk content (str)
        delta: The incremental content (str)
        cumulative_length: Total characters so far (int)
        token_count: Count of tokens processed (int)
        timestamp: When this token arrived (float, seconds since epoch)
        hook_event_name: Event name
    
    Expected output: HookOutput with token aggregation metadata.
    
    Error handling: PRESERVE_EXISTING - per-token hook failures don't block stream.
    
    Use Cases:
        - Token aggregation/batching (collect N tokens before action)
        - Real-time progress monitoring
        - Per-token filtering/transformation
        - Streaming analytics
    
    Performance Note:
        This hook is called FREQUENTLY (often per-token). Keep it lightweight.
        Use batching (e.g., collect 10 tokens then process) to reduce overhead.
    """
    token: str
    delta: str
    cumulative_length: int
    token_count: int
    timestamp: float
    hook_event_name: str


class PostStreamingEvent(TypedDict, total=False):
    """PostStreaming event: after streaming completes.
    
    Input fields:
        total_tokens: Total tokens in the completed stream (int)
        duration_ms: Total streaming duration in milliseconds (float)
        status: Stream completion status (str, e.g., "success", "interrupted")
        final_content: Complete streamed content (str, optional for large responses)
        cumulative_length: Total characters in stream (int)
        hook_event_name: Event name
    
    Expected output: HookOutput with stream summary/metrics.
    
    Error handling: PRESERVE_EXISTING - post-stream logging failures don't affect result.
    
    Use Cases:
        - Log streaming metrics (duration, token count, throughput)
        - Finalize token aggregators
        - Update stream statistics
        - Generate streaming analytics
    """
    total_tokens: int
    duration_ms: float
    status: str
    final_content: Optional[str]
    cumulative_length: int
    hook_event_name: str


class PreMessageEvent(TypedDict, total=False):
    """PreMessage event: before message is added to conversation.
    
    Input fields:
        message_content: The message text/content (str)
        role: Message role (e.g., "user", "assistant", "system")
        hook_event_name: Event name
    
    Expected output: HookOutput with optional message transformation.
    
    Error handling: PRESERVE_EXISTING - message pre-processing failures don't block message.
    
    Use Cases:
        - Message validation/sanitization
        - Pre-processing transformations
        - Content filtering
        - Message enrichment
    """
    message_content: str
    role: str
    hook_event_name: str


class PostMessageEvent(TypedDict, total=False):
    """PostMessage event: after message processed by agent.
    
    Input fields:
        message_content: The message that was processed (str)
        role: Message role (e.g., "assistant", "user")
        hook_event_name: Event name
    
    Expected output: HookOutput with processing results.
    
    Error handling: PRESERVE_EXISTING - post-message logging failures don't affect execution.
    
    Use Cases:
        - Message logging/auditing
        - Post-processing analytics
        - Message archive/storage
        - Notification triggers
    """
    message_content: str
    role: str
    hook_event_name: str


class PlanStartEvent(TypedDict, total=False):
    """PlanStart event from SDK.
    
    Input fields:
        plan_id: Unique plan identifier
        plan_title: Human-readable plan title
        total_tasks: Number of tasks in plan
        total_todos: Number of todos in plan
        triggered_by: Trigger source (user|auto|resume)
        hook_event_name: Event name
    """
    plan_id: int
    plan_title: str
    total_tasks: int
    total_todos: int
    triggered_by: str
    hook_event_name: str


class PlanStopEvent(TypedDict, total=False):
    """PlanStop event from SDK.
    
    Input fields:
        plan_id: Unique plan identifier
        stop_reason: Reason for stop (user_interrupt|error|timeout)
        completed_todos: Number of todos completed before stop
        total_todos: Total todos in plan
        hook_event_name: Event name
    """
    plan_id: int
    stop_reason: str
    completed_todos: int
    total_todos: int
    hook_event_name: str



class PlanCompleteEvent(TypedDict, total=False):
    """PlanComplete event from SDK.
    
    Input fields:
        plan_id: Unique plan identifier
        plan_title: Human-readable plan title
        total_todos: Total todos in plan
        completed_todos: Number of todos completed
        failed_todos: Number of todos that failed
        duration_ms: Total execution duration in milliseconds
        hook_event_name: Event name
    """
    plan_id: int
    plan_title: str
    total_todos: int
    completed_todos: int
    failed_todos: int
    duration_ms: float
    hook_event_name: str



class PlanPhaseStartEvent(TypedDict, total=False):
    """PlanPhaseStart event from SDK.
    
    Input fields:
        plan_id: Unique plan identifier
        phase_name: Logical label for phase (not DB field)
        phase_index: Zero-based phase index
        total_phases: Total phases in plan
        todos_in_phase: Number of todos in this phase
        hook_event_name: Event name
    """
    plan_id: int
    phase_name: str
    phase_index: int
    total_phases: int
    todos_in_phase: int
    hook_event_name: str


class PlanPhaseStopEvent(TypedDict, total=False):
    """PlanPhaseStop event from SDK.
    
    Input fields:
        plan_id: Unique plan identifier
        phase_name: Logical label for phase
        stop_reason: Reason for stop
        completed_todos: Number of todos completed in phase
        hook_event_name: Event name
    """
    plan_id: int
    phase_name: str
    stop_reason: str
    completed_todos: int
    hook_event_name: str


class PlanPhaseCompleteEvent(TypedDict, total=False):
    """PlanPhaseComplete event from SDK.
    
    Input fields:
        plan_id: Unique plan identifier
        phase_name: Logical label for phase
        phase_index: Zero-based phase index
        completed_todos: Number of todos completed in phase
        failed_todos: Number of todos that failed in phase
        duration_ms: Phase execution duration in milliseconds
        hook_event_name: Event name
    """
    plan_id: int
    phase_name: str
    phase_index: int
    completed_todos: int
    failed_todos: int
    duration_ms: float
    hook_event_name: str


class PlanTaskStartEvent(TypedDict, total=False):
    """PlanTaskStart event from SDK.
    
    Input fields:
        plan_id: Unique plan identifier
        task_id: Unique task identifier
        task_title: Human-readable task title
        task_sequence: Sequence number of task
        hook_event_name: Event name
    """
    plan_id: int
    task_id: int
    task_title: str
    task_sequence: int
    hook_event_name: str


class PlanTaskStopEvent(TypedDict, total=False):
    """PlanTaskStop event from SDK.
    
    Input fields:
        plan_id: Unique plan identifier
        task_id: Unique task identifier
        stop_reason: Reason for stop
        hook_event_name: Event name
    """
    plan_id: int
    task_id: int
    stop_reason: str
    hook_event_name: str


class PlanTaskCompleteEvent(TypedDict, total=False):
    """PlanTaskComplete event from SDK.
    
    Input fields:
        plan_id: Unique plan identifier
        task_id: Unique task identifier
        task_title: Human-readable task title
        duration_ms: Task execution duration in milliseconds
        hook_event_name: Event name
    """
    plan_id: int
    task_id: int
    task_title: str
    duration_ms: float
    hook_event_name: str


class PlanTodoStartEvent(TypedDict, total=False):
    """PlanTodoStart event from SDK.
    
    Input fields:
        plan_id: Unique plan identifier
        todo_id: Unique todo identifier
        todo_content: Todo content text (NOT "title")
        task_id: Parent task identifier
        hook_event_name: Event name
    """
    plan_id: int
    todo_id: int
    todo_content: str
    task_id: int
    hook_event_name: str


class PlanTodoStopEvent(TypedDict, total=False):
    """PlanTodoStop event from SDK.
    
    Input fields:
        plan_id: Unique plan identifier
        todo_id: Unique todo identifier
        stop_reason: Reason for stop
        hook_event_name: Event name
    """
    plan_id: int
    todo_id: int
    stop_reason: str
    hook_event_name: str


class PlanTodoCompleteEvent(TypedDict, total=False):
    """PlanTodoComplete event from SDK.
    
    Input fields:
        plan_id: Unique plan identifier
        todo_id: Unique todo identifier
        todo_content: Todo content text
        duration_ms: Todo execution duration in milliseconds
        hook_event_name: Event name
    """
    plan_id: int
    todo_id: int
    todo_content: str
    duration_ms: float
    hook_event_name: str


class OnFirstSetupEvent(TypedDict, total=False):
    """OnFirstSetup event: when CyberSecSuite runs for the first time.
    
    Input fields:
        project_root: Project root directory path
        app_home: Application home directory
        hostname: System hostname
        triggered_by: Setup trigger source (e.g., "user", "auto")
        hook_event_name: Event name
    """
    project_root: str
    app_home: str
    hostname: str
    triggered_by: str
    hook_event_name: str


class PreRetryEvent(TypedDict, total=False):
    """PreRetry event: before retry attempt.
    
    Input fields:
        error_type: Exception class name (e.g., "RateLimitError", "TimeoutError")
        error_message: Human-readable error message
        attempt_number: 1-based attempt number (1st, 2nd, 3rd, etc.)
        max_attempts: Maximum allowed retry attempts
        retry_delay_ms: Milliseconds to wait before retry
        tool_name: Optional tool name that caused the error
        correlation_id: Request correlation ID for tracking
    
    Expected output: HookOutput with optional suppress_retry decision.
    
    Error handling: PRESERVE_EXISTING - pre-retry decisions are best-effort.
    
    Use Cases:
        - Log retry attempts with context
        - Suppress retry for certain error types
        - Modify retry delay dynamically (future)
        - Alert on repeated failures
    """
    error_type: str
    error_message: str
    attempt_number: int
    max_attempts: int
    retry_delay_ms: float
    tool_name: Optional[str]
    correlation_id: str


class OnRecoveryEvent(TypedDict, total=False):
    """OnRecovery event: after successful recovery from error.
    
    Input fields:
        error_type: Exception class name that was recovered from
        recovered_after_attempts: Number of attempts taken to recover
        total_retry_duration_ms: Total milliseconds spent retrying
        correlation_id: Request correlation ID for tracking
    
    Expected output: HookOutput (fire-and-forget logging).
    
    Error handling: PRESERVE_EXISTING - recovery logging is optional.
    
    Use Cases:
        - Log successful recovery for monitoring
        - Update circuit breaker state
        - Send recovery notifications
        - Track MTTR (mean time to recovery)
    """
    error_type: str
    recovered_after_attempts: int
    total_retry_duration_ms: float
    correlation_id: str


class OnErrorEvent(TypedDict, total=False):
    """OnError event: when error is final (non-recoverable).
    
    Input fields:
        error_type: Exception class name (e.g., "PermissionError", "ValueError")
        error_message: Human-readable error message
        is_fatal: True if operation cannot be retried
        attempt_number: Number of attempts made (if retried)
        correlation_id: Request correlation ID for tracking
    
    Expected output: HookOutput (fire-and-forget logging).
    
    Error handling: PRESERVE_EXISTING - error logging is optional.
    
    Use Cases:
        - Log permanent failures for audit trail
        - Send alerts for fatal errors
        - Update monitoring dashboards
        - Trigger fallback workflows
    """
    error_type: str
    error_message: str
    is_fatal: bool
    attempt_number: int
    correlation_id: str



# Union of all event types for dispatch
EventType = (
        PreToolUseEvent |
        PostToolUseEvent |
        PostToolUseFailureEvent |
        UserPromptSubmitEvent |
        StopEvent |
        AgentStartEvent |
        AgentStopEvent |
        PreCompactEvent |
        PermissionRequestEvent |
        NotificationEvent |
        PreStreamingEvent |
        StreamingTokenEvent |
        PostStreamingEvent |
        PreMessageEvent |
        PostMessageEvent |
        PreRetryEvent |
        OnRecoveryEvent |
        OnErrorEvent |
        OnFirstSetupEvent |
        PlanStartEvent |
        PlanStopEvent |
        PlanCompleteEvent |
        PlanPhaseStartEvent |
        PlanPhaseStopEvent |
        PlanPhaseCompleteEvent |
        PlanTaskStartEvent |
        PlanTaskStopEvent |
        PlanTaskCompleteEvent |
        PlanTodoStartEvent |
        PlanTodoStopEvent |
        PlanTodoCompleteEvent
)


# ── Recovery Hook Output Types ─────────────────────────────────────────────

class PreRetryOutput(TypedDict, total=False):
    """Output from PreRetry hooks.
    
    Fields:
        suppress_retry: If True, prevent the retry attempt (default False)
        delay_override_ms: If provided, override the retry delay
        metadata: Optional additional context
    
    Fire-and-forget semantics:
        - Hooks that return empty {} are treated as "no change"
        - Multiple PreRetry hooks may execute; last one wins for decisions
        - If any hook returns suppress_retry=True, retry is suppressed
    """
    suppress_retry: bool
    delay_override_ms: Optional[float]
    metadata: Optional[dict[str, Any]]


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

"""Hook system for CyberSecSuite.

Type-safe hook wrapper around the existing Claude Agent SDK hook matchers.

Design Principles:
    - NO behavioral changes to existing hooks
    - Backward compatible with all existing hook code
    - Type safety through TypedDicts and dataclasses
    - Stateless registry: HookContext passed per-call
    - Gradual typing: wrap hooks incrementally
    - Performance instrumentation: optional, zero-cost when disabled

Public API:
    - HookContext: Metadata for hook execution
    - ErrorStrategy: Error handling semantics
    - HookOutput: Standardized hook response type
    - Event TypedDicts: Type contracts for each event
    - HookRegistry: Stateless hook executor
    - get_registry(): Get global registry singleton
    - HookInstrument: Performance instrumentation for hooks
    - HookMetrics: Individual hook timing metrics
    - PERFORMANCE_BUDGETS: Performance thresholds
"""

from hooks.core import (
    ErrorStrategy,
    HookContext,
    HookOutput,
    NotificationEvent,
    PermissionRequestEvent,
    PostToolUseEvent,
    PostToolUseFailureEvent,
    PreCompactEvent,
    PreToolUseEvent,
    StopEvent,
    SubagentStartEvent,
    SubagentStopEvent,
    UserPromptSubmitEvent,
)
from hooks.instrumentation import (
    HookInstrument,
    HookMetrics,
    PERFORMANCE_BUDGETS,
    get_instrumentation,
    reset_instrumentation,
)
from hooks.registry import (
    HookRegistry,
    get_registry,
    reset_registry,
)

__all__ = [
    # Core types
    "HookContext",
    "ErrorStrategy",
    "HookOutput",
    # Event types
    "PreToolUseEvent",
    "PostToolUseEvent",
    "PostToolUseFailureEvent",
    "UserPromptSubmitEvent",
    "StopEvent",
    "SubagentStartEvent",
    "SubagentStopEvent",
    "PreCompactEvent",
    "PermissionRequestEvent",
    "NotificationEvent",
    # Registry
    "HookRegistry",
    "get_registry",
    "reset_registry",
    # Instrumentation
    "HookInstrument",
    "HookMetrics",
    "PERFORMANCE_BUDGETS",
    "get_instrumentation",
    "reset_instrumentation",
]

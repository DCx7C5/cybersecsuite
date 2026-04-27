"""Type-safe hook system for CyberSecSuite Agent SDK.

This module provides a typed, stateless hook registry wrapper that integrates with
the Claude Agent SDK while maintaining full backward compatibility with existing
hook implementations.

Architecture
============

The hook system consists of:

1. **core.py** — Type definitions (HookContext, ErrorStrategy, TypedDicts for events)
   - No Pydantic, just Python typing
   - Provides HookContext passed to every hook call
   - Defines ErrorStrategy enum for error handling

2. **registries/hooks.py** — Stateless HookRegistry wrapper
   - Wraps build_python_hooks() output in type-safe interface
   - Caches hooks once at init, never mutates per-call
   - All per-call state passed via HookContext parameter
   - Maintains full backward compatibility (returns same hook format as build_python_hooks)

3. **instrumentation.py** — Optional performance instrumentation
   - Lightweight timing capture (<1ms overhead per hook)
   - Performance budgets: no_op <2ms, validated_sync <10ms, io_bound <50ms
   - Metrics collected without changing hook behavior

4. **sdk_hooks.py** — Python SDK hook implementations
   - 11 hook event types (PreToolUse, PostToolUse, etc.)
   - 40+ individual hook functions with audit logging
   - Fire-and-forget error handling (never blocks execution)

Integration with Agent SDK
==========================

The agent SDK (src/a2a/agent_sdk.py) uses HookRegistry:

    from src.registries.hooks import get_registry
    
    # Get global singleton (created once, stateless)
    registry = get_registry()
    
    # Use registry._hooks directly in ClaudeAgentOptions
    # Same format as build_python_hooks() output
    options = ClaudeAgentOptions(hooks=registry._hooks, ...)

This maintains backward compatibility because:
- registry._hooks has same format as build_python_hooks() return
- Existing hooks work unchanged
- All 40+ hooks still execute identically
- Optional instrumentation doesn't change behavior

Hook Coverage
=============

The system covers 11 SDK hook event types:

1. **PreToolUse** — Before tool execution
   - _pre_tool_write_guard: Blocks writes outside project root
   - _pre_tool_audit: Logs all tool invocations

2. **PostToolUse** — After successful tool execution
   - _post_tool_audit: Logs tool output and result size

3. **PostToolUseFailure** — After tool execution failure
   - _post_tool_failure_audit: Logs tool errors

4. **UserPromptSubmit** — When user submits prompt
   - _user_prompt_context: Adds context to prompt

5. **Stop** — When agent stops
   - _stop_snapshot: Records session snapshot

6. **SubagentStart** — When subagent starts
   - _subagent_start: Logs subagent lifecycle

7. **SubagentStop** — When subagent stops
   - _subagent_stop: Logs subagent lifecycle

8. **PreCompact** — Before context compaction
   - _pre_compact: Async fire-and-forget snapshot

9. **PermissionRequest** — Permission decision
   - _permission_auto_allow: Auto-allows read-only tools
   - _permission_default_ask: Default interactive approval

10. **Notification** — System notifications
    - _notification_hook: D-Bus integration

11. **Plus CLI/scripting hooks** — Additional hooks in various .py files

Usage Patterns
==============

**Basic: Just use SDK (transparent integration)**

    from a2a.agent_sdk import build_agent_options
    
    # Hooks are automatically initialized and wrapped
    options = build_agent_options()

**Advanced: Use registry directly**

    from src.registries.hooks import get_registry
    from hooks.core import HookContext
    import time
    
    registry = get_registry()
    
    context = HookContext(
        correlation_id="req-123",
        session_id="sess-456",
        timestamp=time.time(),
    )
    
    # Execute hooks programmatically
    result = await registry.execute("PreToolUse", event_data, context)

**Performance monitoring: Enable instrumentation**

    from src.registries.hooks import HookRegistry
    from hooks.instrumentation import HookInstrument
    
    instrument = HookInstrument()
    registry = HookRegistry(instrumentation=instrument)
    
    # Use registry...
    
    # Get metrics
    stats = instrument.get_stats()
    report = instrument.generate_report()

Error Handling
==============

Three error strategies:

1. **PRESERVE_EXISTING** (default) — Hook failure doesn't block execution
2. **LOG** — Log errors but don't propagate
3. **WARN** — Log warnings but don't propagate

All hooks are fire-and-forget: exceptions are caught and logged, never raised
to the caller. This ensures hook failures don't break agent execution.

Performance Budgets
===================

- **no_op**: <2ms (hooks that do nothing)
- **validated_sync**: <10ms (simple validation/audit)
- **io_bound**: <50ms (file I/O, network calls)

These are soft targets. The instrumentation system measures actual performance
and can generate reports when hooks exceed budgets.

Testing
=======

All hooks are tested via:

1. **Hook-specific tests** (tests/unit/test_hooks_*.py)
   - 68 tests for registry, instrumentation, core

2. **Agent hook tests** (tests/unit/test_agent_hooks.py)
   - 17 tests for agent lifecycle hooks

3. **Agent SDK integration tests** (tests/unit/test_agent_sdk_hooks_integration.py)
   - 16 tests for SDK integration and backward compat

4. **Full regression suite** — 766+ tests total

State Design
============

The registry is **stateless** by design:

- **Per-registry state**: _hooks dict (immutable after init)
- **Per-call state**: HookContext parameter (correlation_id, session_id, etc.)
- **NO per-run storage** on registry instance
- **NO global state mutation** except singleton cache
- **Thread-safe**: context passed per-call, no shared mutable state

This allows safe concurrent use and clean testing.

Extending the System
====================

To add a new hook:

1. Define event TypedDict in core.py (optional, for type hints)
2. Implement async hook function in sdk_hooks.py
3. Register in build_python_hooks() dict
4. Add unit tests in tests/unit/

Example:

    async def _my_hook(event: dict[str, Any], *_: Any) -> dict[str, Any]:
        try:
            # Your logic here
            return {}  # or {hookSpecificOutput: {...}}
        except Exception as exc:
            audit({"event": "HookError", "hook": "_my_hook", "error": str(exc)})
        return {}

Then add to build_python_hooks():

    "MyEventType": [HookMatcher(matcher=".*", hooks=[_my_hook])]

See PHASE_15_HOOKS_IMPROVEMENT.md for full design details.
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
    # Instrumentation
    "HookInstrument",
    "HookMetrics",
    "PERFORMANCE_BUDGETS",
    "get_instrumentation",
    "reset_instrumentation",
    # Note: HookRegistry, get_registry, reset_registry are now in src.registries.hooks
    # Import directly from there: from src.registries.hooks import HookRegistry, get_registry
]


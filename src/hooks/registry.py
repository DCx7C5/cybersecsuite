"""Stateless, immutable hook registry wrapper.

This module wraps the existing SDK hook matchers (from build_python_hooks())
in a type-safe, stateless interface WITHOUT changing hook behavior.

Key design principle: NO per-call state storage on the registry.
- HookContext passed in per-call (contains correlation_id, session_id, etc.)
- Timing/metrics computed in local scope only
- ClaudeAgentOptions caching unaffected
- Backward compatibility: old hooks returning dicts still work
"""

import logging
import time
from typing import TYPE_CHECKING, Any, Optional

from claude_agent_sdk import HookMatcher

from hooks.core import (
    ErrorStrategy,
    HookContext,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _audit(data: dict[str, Any]) -> None:
    """Lazy-load audit function to avoid circular imports."""
    try:
        from hooks._utils import audit as audit_fn
        audit_fn(data)
    except Exception:
        pass


# ── HookRegistry ──────────────────────────────────────────────────────────

class HookRegistry:
    """Stateless wrapper around existing SDK hook matchers.
    
    Design:
        - Wraps build_python_hooks() result at __init__ (called once)
        - Caches result in self._hooks (immutable after init)
        - Per-call state via HookContext parameter
        - No per-run state storage on registry instance
        - Timing/metrics computed locally, not stored
    
    Backward Compatibility:
        - Existing hooks returning plain {} are acceptable
        - Hooks returning {'async_': True} work as before
        - Old API continues working without modification
        - Gradual typing: can wrap hooks incrementally
    """
    
    def __init__(self, error_strategy: ErrorStrategy = ErrorStrategy.PRESERVE_EXISTING):
        """Initialize registry with cached hook matchers.
        
        Args:
            error_strategy: How to handle hook execution errors.
                Default PRESERVE_EXISTING means failures don't break execution.
        """
        # Import here to avoid circular dependency
        from hooks.sdk_hooks import build_python_hooks
        
        # Cache the hook matcher registry once at init
        self._hooks: dict[str, list[HookMatcher]] = build_python_hooks()
        self._error_strategy = error_strategy
    
    async def execute(
        self,
        event_type: str,
        event: dict[str, Any],
        context: HookContext,
    ) -> dict[str, Any]:
        """Execute hooks for event, returning typed output.
        
        Args:
            event_type: Event name (e.g., "PreToolUse", "PostToolUse")
            event: Event payload dict from SDK
            context: HookContext with correlation_id, session_id, etc.
        
        Returns:
            HookOutput with hookSpecificOutput (may be empty dict)
            
        Behavior:
            - Delegates to existing matchers from build_python_hooks()
            - Type validation at boundaries only (input/output)
            - Errors handled per error_strategy
            - Backward compatible with existing hook returns
        
        Raises:
            Nothing (errors are logged and handled per strategy)
        """
        if event_type not in self._hooks:
            logger.warning(f"No hooks registered for event_type: {event_type}")
            return {}
        
        matchers = self._hooks[event_type]
        combined_output: dict[str, Any] = {}
        
        try:
            # Execute all matching hooks in order
            for matcher in matchers:
                try:
                    # Get hooks from the matcher
                    hooks = matcher.hooks if hasattr(matcher, 'hooks') else []
                    
                    for hook_fn in hooks:
                        try:
                            # Execute hook with event (old API)
                            start_time = time.time()
                            result = await hook_fn(event)  # type: ignore
                            elapsed = time.time() - start_time
                            
                            # Validate result type (but accept any dict)
                            if not isinstance(result, dict):
                                logger.warning(
                                    f"Hook {hook_fn.__name__} returned non-dict: {type(result)}"
                                )
                                result = {}
                            
                            # Log execution
                            _audit({
                                "event": "HookExecuted",
                                "event_type": event_type,
                                "hook": hook_fn.__name__,
                                "correlation_id": context.correlation_id,
                                "session_id": context.session_id,
                                "elapsed_ms": round(elapsed * 1000),
                                "has_output": bool(result),
                            })
                            
                            # Merge output (later hooks can override)
                            if result:
                                combined_output.update(result)
                        
                        except Exception as exc:
                            self._handle_hook_error(
                                hook_fn.__name__,
                                event_type,
                                exc,
                                context,
                            )
                
                except Exception as exc:
                    logger.error(f"Error processing matcher for {event_type}: {exc}")
                    if self._error_strategy == ErrorStrategy.PRESERVE_EXISTING:
                        # Continue to next matcher
                        pass
                    else:
                        raise
        
        except Exception as exc:
            logger.error(f"Fatal error in hook registry for {event_type}: {exc}")
            if self._error_strategy != ErrorStrategy.PRESERVE_EXISTING:
                raise
        
        return combined_output
    
    def get_hooks_for_event(self, event_type: str) -> list[Any]:
        """Introspection: get all hook functions for an event type.
        
        Args:
            event_type: Event name (e.g., "PreToolUse")
        
        Returns:
            List of hook callables, or empty list if event not found
        """
        if event_type not in self._hooks:
            return []
        
        hooks = []
        for matcher in self._hooks[event_type]:
            if hasattr(matcher, 'hooks'):
                hooks.extend(matcher.hooks)
        return hooks
    
    def validate_event(self, event_type: str, event: dict[str, Any]) -> bool:
        """Validate event matches expected schema for event_type.
        
        Args:
            event_type: Event name (e.g., "PreToolUse")
            event: Event payload to validate
        
        Returns:
            True if event matches schema, False otherwise
            
        Note:
            Currently checks event_type exists in registry.
            Future: can add field validation using TypedDict hints.
        """
        if event_type not in self._hooks:
            logger.warning(f"Unknown event type: {event_type}")
            return False
        
        if not isinstance(event, dict):
            logger.warning(f"Event is not a dict: {type(event)}")
            return False
        
        # Future: add field-level validation using _EVENT_TYPE_MAP
        # For now, just basic schema check
        return True
    
    def _handle_hook_error(
        self,
        hook_name: str,
        event_type: str,
        exc: Exception,
        context: HookContext,
    ) -> None:
        """Handle hook execution error per error_strategy.
        
        Args:
            hook_name: Name of hook that failed
            event_type: Event type being processed
            exc: The exception raised
            context: HookContext for correlation
        """
        error_msg = f"Hook {hook_name} failed for {event_type}: {exc}"
        
        _audit({
            "event": "HookError",
            "hook": hook_name,
            "event_type": event_type,
            "correlation_id": context.correlation_id,
            "error": str(exc)[:500],
            "strategy": self._error_strategy.value,
        })
        
        if self._error_strategy == ErrorStrategy.LOG:
            logger.error(error_msg, exc_info=exc)
        elif self._error_strategy == ErrorStrategy.WARN:
            logger.warning(error_msg)
        else:  # PRESERVE_EXISTING
            # Don't log at all, just silently preserve
            pass


# ── Global Registry Singleton ─────────────────────────────────────────────

_global_registry: Optional[HookRegistry] = None


def get_registry(
    error_strategy: ErrorStrategy = ErrorStrategy.PRESERVE_EXISTING,
) -> HookRegistry:
    """Get or create the global hook registry.
    
    Args:
        error_strategy: Error handling strategy (only used on first call)
    
    Returns:
        The global HookRegistry instance
        
    Note:
        Registry is created once and cached. Subsequent calls ignore
        error_strategy parameter and return cached instance.
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = HookRegistry(error_strategy=error_strategy)
    return _global_registry


def reset_registry() -> None:
    """Reset the global registry (for testing only)."""
    global _global_registry
    _global_registry = None

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

from hooks.config import HookConfig
from hooks.core import (
    ErrorStrategy,
    HookContext,
)
from hooks.instrumentation import HookInstrument
from hooks.utils import get_app_home

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _audit(data: dict[str, Any]) -> None:
    """Lazy-load audit function to avoid circular imports."""
    try:
        from hooks.utils import audit as audit_fn
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
    
    def __init__(
        self,
        error_strategy: ErrorStrategy = ErrorStrategy.PRESERVE_EXISTING,
        instrumentation: Optional[HookInstrument] = None,
        config: Optional[HookConfig] = None,
    ):
        """Initialize registry with cached hook matchers.
        
        Args:
            error_strategy: How to handle hook execution errors.
                Default PRESERVE_EXISTING means failures don't break execution.
            instrumentation: Optional HookInstrument for performance tracking.
                If None, timing is not collected. Pass HookInstrument() to enable.
            config: Optional HookConfig for declarative hook configuration.
                If provided, will filter enabled/disabled hooks and apply performance budgets.
                Default None means all hooks are enabled (backward compat).
        """
        # Import here to avoid circular dependency
        from hooks.sdk_hooks import build_python_hooks
        
        # Cache the hook matcher registry once at init
        self._hooks: dict[str, list[HookMatcher]] = build_python_hooks()
        self._error_strategy = error_strategy
        self._instrumentation = instrumentation
        self._config = config
        
        # If config provided, apply performance budgets to instrumentation
        if self._config and self._instrumentation:
            perf = self._config.performance
            self._instrumentation.budget_no_op_ms = perf.budget_no_op_ms
            self._instrumentation.budget_validated_ms = perf.budget_validated_ms
            self._instrumentation.slow_hook_threshold_ms = perf.slow_hook_threshold_ms
    
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
            - Checks config to see if event type is enabled
            - Delegates to existing matchers from build_python_hooks()
            - Filters hooks based on config if provided
            - Type validation at boundaries only (input/output)
            - Errors handled per error_strategy
            - Backward compatible with existing hook returns
            - If instrumentation enabled, timing is captured (zero behavioral change)
        
        Raises:
            Nothing (errors are logged and handled per strategy)
        """
        # Check if event type is enabled in config
        if self._config and not self._config.is_event_enabled(event_type):
            logger.debug(f"Event type disabled in config: {event_type}")
            return {}
        
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
                            # Execute hook with optional instrumentation
                            if self._instrumentation:
                                result, metrics = await self._instrumentation.instrument_hook_call(
                                    hook_fn.__name__,
                                    event_type,
                                    hook_fn,
                                    event,
                                )
                            else:
                                # No instrumentation: execute directly
                                result = await hook_fn(event)  # type: ignore
                            
                            # Validate result type (but accept any dict)
                            if not isinstance(result, dict):
                                logger.warning(
                                    f"Hook {hook_fn.__name__} returned non-dict: {type(result)}"
                                )
                                result = {}
                            
                            # Log execution (timing info if instrumented)
                            log_data = {
                                "event": "HookExecuted",
                                "event_type": event_type,
                                "hook": hook_fn.__name__,
                                "correlation_id": context.correlation_id,
                                "session_id": context.session_id,
                                "has_output": bool(result),
                            }
                            
                            if self._instrumentation:
                                # Timing already captured in metrics
                                recent_metrics = self._instrumentation.metrics
                                if recent_metrics:
                                    last_metric = recent_metrics[-1]
                                    log_data["elapsed_ms"] = round(last_metric.duration_ms)
                                    log_data["success"] = last_metric.success
                            else:
                                # Legacy path: measure time for audit
                                start_time = time.time()
                                elapsed = time.time() - start_time
                                log_data["elapsed_ms"] = round(elapsed * 1000)
                            
                            _audit(log_data)
                            
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
    
    def get_instrumentation(self) -> Optional[HookInstrument]:
        """Get the instrumentation instance for this registry.
        
        Returns:
            HookInstrument instance if enabled, None otherwise
        """
        return self._instrumentation
    
    def get_config(self) -> Optional[HookConfig]:
        """Get the hook configuration for this registry.
        
        Returns:
            HookConfig instance if provided, None otherwise
        """
        return self._config
    
    def is_event_enabled(self, event_type: str) -> bool:
        """Check if an event type is enabled in the configuration.
        
        Args:
            event_type: Event type name (e.g., "PreToolUse")
        
        Returns:
            True if event is enabled (or no config), False if explicitly disabled
        """
        if not self._config:
            return True
        return self._config.is_event_enabled(event_type)
    
    async def execute_streaming(
        self,
        event_type: str,
        event: dict[str, Any],
        context: HookContext,
        batch_size: int = 1,
    ) -> dict[str, Any]:
        """Execute streaming hooks with optional token batching.
        
        This method is optimized for frequent streaming token events.
        It can batch multiple token events before executing hooks to
        reduce overhead (e.g., collect 10 tokens, then call hooks once).
        
        Args:
            event_type: Event name (e.g., "StreamingToken", "PreStreaming")
            event: Event payload dict from SDK
            context: HookContext with correlation_id, session_id, etc.
            batch_size: For StreamingToken events, batch this many tokens
                       before executing hooks (default 1 = no batching)
        
        Returns:
            HookOutput with hookSpecificOutput (maybe empty dict)
        
        Behavior:
            - Delegates to existing matchers from build_python_hooks()
            - For StreamingToken events with batch_size > 1:
              - Accumulates tokens in event dict as "_batched_tokens"
              - Executes hooks when batch reaches batch_size
              - Resets batch for next iteration
            - Type validation at boundaries only
            - Errors handled per error_strategy
            - Backward compatible with non-streaming hooks
        
        Raises:
            Nothing (errors are logged and handled per strategy)
        
        Performance Note:
            Streaming token hooks are called frequently (per token).
            Use batch_size > 1 to amortize hook execution cost.
            Example: batch_size=10 reduces hook calls to 10% overhead.
        """
        # Check if event type is enabled in config
        if self._config and not self._config.is_event_enabled(event_type):
            logger.debug(f"Event type disabled in config: {event_type}")
            return {}
        
        if event_type not in self._hooks:
            logger.warning(f"No hooks registered for event_type: {event_type}")
            return {}
        
        # For non-batched streams or pre- / post-streaming events, use standard execute
        if event_type != "StreamingToken" or batch_size <= 1:
            return await self.execute(event_type, event, context)
        
        # Streaming token batching logic
        matchers = self._hooks[event_type]
        combined_output: dict[str, Any] = {}
        
        # Initialize batch accumulator in event if needed
        if "_batched_tokens" not in event:
            event["_batched_tokens"] = []
        
        # Add current token to batch
        if "token" in event:
            event["_batched_tokens"].append({
                "token": event["token"],
                "delta": event.get("delta", ""),
                "cumulative_length": event.get("cumulative_length", 0),
                "token_count": event.get("token_count", 0),
                "timestamp": event.get("timestamp", time.time()),
            })
        
        # Check if we've reached batch size
        if len(event["_batched_tokens"]) >= batch_size:
            try:
                # Execute all matching hooks in order
                for matcher in matchers:
                    try:
                        hooks = matcher.hooks if hasattr(matcher, 'hooks') else []
                        
                        for hook_fn in hooks:
                            try:
                                # Execute hook with optional instrumentation
                                if self._instrumentation:
                                    result, metrics = await self._instrumentation.instrument_hook_call(
                                        hook_fn.__name__,
                                        event_type,
                                        hook_fn,
                                        event,
                                    )
                                else:
                                    # No instrumentation: execute directly
                                    result = await hook_fn(event)  # type: ignore
                                
                                # Validate result type
                                if not isinstance(result, dict):
                                    logger.warning(
                                        f"Hook {hook_fn.__name__} returned non-dict: {type(result)}"
                                    )
                                    result = {}
                                
                                # Log execution
                                log_data = {
                                    "event": "StreamingHookExecuted",
                                    "event_type": event_type,
                                    "hook": hook_fn.__name__,
                                    "correlation_id": context.correlation_id,
                                    "session_id": context.session_id,
                                    "batch_size": len(event["_batched_tokens"]),
                                    "has_output": bool(result),
                                }
                                
                                if self._instrumentation:
                                    recent_metrics = self._instrumentation.metrics
                                    if recent_metrics:
                                        last_metric = recent_metrics[-1]
                                        log_data["elapsed_ms"] = round(last_metric.duration_ms)
                                        log_data["success"] = last_metric.success
                                
                                _audit(log_data)
                                
                                # Merge output
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
                            pass
                        else:
                            raise
            
            except Exception as exc:
                logger.error(f"Fatal error in streaming hook registry for {event_type}: {exc}")
                if self._error_strategy != ErrorStrategy.PRESERVE_EXISTING:
                    raise
            
            # Reset batch for next iteration
            event["_batched_tokens"] = []
        
        return combined_output
    
    async def execute_pre_message(
        self,
        message_content: str,
        role: str,
        correlation_id: str,
        context: HookContext,
        message_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> tuple[str, dict[str, Any]]:
        """Execute PreMessage hooks for message transformation/validation.
        
        PreMessage hooks can transform or validate messages before they are
        added to the conversation. The message can be:
        - Passed through unchanged (most common)
        - Transformed (e.g., translated, redacted, reformatted)
        - Filtered (though not explicitly blocked, can be effectively filtered)
        
        Args:
            message_content: The message text to process
            role: Message role (e.g., "user", "assistant", "system")
            correlation_id: Request correlation ID for tracking
            context: HookContext with session_id, timestamp, etc.
            message_id: Optional unique message identifier
            metadata: Optional additional context metadata
        
        Returns:
            Tuple of (transformed_message, hook_output_dict):
            - transformed_message: The processed message (maybe transformed)
            - hook_output_dict: Combined output from all hooks (for logging/metrics)
        
        Behavior:
            - Executes all registered PreMessage hooks in order
            - Each hook receives the CURRENT message (maybe transformed by prior hooks)
            - First hook to return transformed_message wins (applied to subsequent hooks)
            - If no transformed_message, original message_content is used
            - Errors handled per error_strategy (failures preserve original message)
            - Instrumentation captures timing if enabled
        
        Raises:
            Nothing (errors are logged and handled per strategy)
        
        Use Cases:
            - Validate message format/encoding
            - Sanitize/redact sensitive data
            - Apply content transformations
            - Track message correlation
            - Prevent spam/malicious content
        """
        event: dict[str, Any] = {
            "message_content": message_content,
            "role": role,
            "correlation_id": correlation_id,
            "message_id": message_id,
            "metadata": metadata or {},
            "hook_event_name": "PreMessage",
        }
        
        if "PreMessage" not in self._hooks:
            logger.debug("No PreMessage hooks registered")
            return message_content, {}
        
        matchers = self._hooks["PreMessage"]
        combined_output: dict[str, Any] = {}
        current_message = message_content
        
        try:
            for matcher in matchers:
                try:
                    hooks = matcher.hooks if hasattr(matcher, 'hooks') else []
                    
                    for hook_fn in hooks:
                        try:
                            # Update event with current message (may be transformed)
                            event["message_content"] = current_message
                            
                            # Execute hook with optional instrumentation
                            if self._instrumentation:
                                result, metrics = await self._instrumentation.instrument_hook_call(
                                    hook_fn.__name__,
                                    "PreMessage",
                                    hook_fn,
                                    event,
                                )
                            else:
                                result = await hook_fn(event)  # type: ignore
                            
                            # Validate result type
                            if not isinstance(result, dict):
                                logger.warning(
                                    f"PreMessage hook {hook_fn.__name__} returned non-dict: {type(result)}"
                                )
                                result = {}
                            
                            # Check for message transformation
                            if "transformed_message" in result:
                                transformed = result.pop("transformed_message")
                                if isinstance(transformed, str):
                                    current_message = transformed
                                    logger.debug(
                                        f"PreMessage hook {hook_fn.__name__} transformed message "
                                        f"({len(message_content)} -> {len(current_message)} chars)"
                                    )
                            
                            # Log execution
                            log_data = {
                                "event": "PreMessageHookExecuted",
                                "hook": hook_fn.__name__,
                                "correlation_id": correlation_id,
                                "session_id": context.session_id,
                                "has_output": bool(result),
                            }
                            
                            if self._instrumentation:
                                recent_metrics = self._instrumentation.metrics
                                if recent_metrics:
                                    last_metric = recent_metrics[-1]
                                    log_data["elapsed_ms"] = round(last_metric.duration_ms)
                                    log_data["success"] = last_metric.success
                            
                            _audit(log_data)
                            
                            # Merge output
                            if result:
                                combined_output.update(result)
                        
                        except Exception as exc:
                            self._handle_hook_error(
                                hook_fn.__name__,
                                "PreMessage",
                                exc,
                                context,
                            )
                
                except Exception as exc:
                    logger.error(f"Error processing matcher for PreMessage: {exc}")
                    if self._error_strategy == ErrorStrategy.PRESERVE_EXISTING:
                        pass
                    else:
                        raise
        
        except Exception as exc:
            logger.error(f"Fatal error in PreMessage hook registry: {exc}")
            if self._error_strategy != ErrorStrategy.PRESERVE_EXISTING:
                raise
        
        return current_message, combined_output
    
    async def execute_post_message(
        self,
        message_content: str,
        role: str,
        response_time_ms: float,
        token_count: int,
        status: str,
        correlation_id: str,
        context: HookContext,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Execute PostMessage hooks for logging/metrics (read-only).
        
        PostMessage hooks are executed AFTER a message has been processed
        by the agent. They are read-only and cannot modify the message.
        They are typically used for:
        - Logging/auditing
        - Metrics collection
        - Performance monitoring
        - Token usage tracking
        
        Args:
            message_content: The processed message text (str)
            role: Message role (e.g., "assistant", "user")
            response_time_ms: Time to process/generate message (float)
            token_count: Number of tokens in message (int)
            status: Processing status (str, e.g., "success", "filtered")
            correlation_id: Request correlation ID for tracking
            context: HookContext with session_id, timestamp, etc.
            metadata: Optional additional context metadata
        
        Returns:
            Combined output dict from all hooks (for logging/metrics)
        
        Behavior:
            - Executes all registered PostMessage hooks in order (fire-and-forget)
            - Hooks receive read-only message (cannot modify)
            - Errors handled per error_strategy (failures don't affect message)
            - Instrumentation captures timing if enabled
            - Should complete quickly (logging only, no heavy processing)
        
        Raises:
            Nothing (errors are logged and handled per strategy)
        
        Use Cases:
            - Audit message and processing decision
            - Log response metrics (time, tokens)
            - Track message flow through system
            - Collect analytics
            - Export to monitoring systems
        
        Note:
            This is a fire-and-forget logging hook. If you need to modify
            the message, use PreMessage hooks instead.
        """
        event: dict[str, Any] = {
            "message_content": message_content,
            "role": role,
            "response_time_ms": response_time_ms,
            "token_count": token_count,
            "status": status,
            "correlation_id": correlation_id,
            "metadata": metadata or {},
            "hook_event_name": "PostMessage",
        }
        
        if "PostMessage" not in self._hooks:
            logger.debug("No PostMessage hooks registered")
            return {}
        
        matchers = self._hooks["PostMessage"]
        combined_output: dict[str, Any] = {}
        
        try:
            for matcher in matchers:
                try:
                    hooks = matcher.hooks if hasattr(matcher, 'hooks') else []
                    
                    for hook_fn in hooks:
                        try:
                            # Execute hook with optional instrumentation
                            if self._instrumentation:
                                result, metrics = await self._instrumentation.instrument_hook_call(
                                    hook_fn.__name__,
                                    "PostMessage",
                                    hook_fn,
                                    event,
                                )
                            else:
                                result = await hook_fn(event)  # type: ignore
                            
                            # Validate result type
                            if not isinstance(result, dict):
                                logger.warning(
                                    f"PostMessage hook {hook_fn.__name__} returned non-dict: {type(result)}"
                                )
                                result = {}
                            
                            # Log execution
                            log_data = {
                                "event": "PostMessageHookExecuted",
                                "hook": hook_fn.__name__,
                                "correlation_id": correlation_id,
                                "session_id": context.session_id,
                                "status": status,
                                "has_output": bool(result),
                            }
                            
                            if self._instrumentation:
                                recent_metrics = self._instrumentation.metrics
                                if recent_metrics:
                                    last_metric = recent_metrics[-1]
                                    log_data["elapsed_ms"] = round(last_metric.duration_ms)
                                    log_data["success"] = last_metric.success
                            
                            _audit(log_data)
                            
                            # Merge output
                            if result:
                                combined_output.update(result)
                        
                        except Exception as exc:
                            self._handle_hook_error(
                                hook_fn.__name__,
                                "PostMessage",
                                exc,
                                context,
                            )
                
                except Exception as exc:
                    logger.error(f"Error processing matcher for PostMessage: {exc}")
                    if self._error_strategy == ErrorStrategy.PRESERVE_EXISTING:
                        pass
                    else:
                        raise
        
        except Exception as exc:
            logger.error(f"Fatal error in PostMessage hook registry: {exc}")
            if self._error_strategy != ErrorStrategy.PRESERVE_EXISTING:
                raise
        
        return combined_output


    async def execute_pre_retry(
        self,
        event: dict[str, Any],
        context: HookContext,
    ) -> dict[str, Any]:
        """Execute PreRetry hooks before retry attempt.
        
        PreRetry hooks can examine the error and potentially suppress the retry
        or modify the retry delay. This is useful for:
        - Detecting unretryable errors (e.g., auth failures)
        - Logging retry attempts with context
        - Implementing circuit breaker patterns
        - Adjusting retry strategy dynamically
        
        Args:
            event: PreRetryEvent with error_type, attempt_number, etc.
            context: HookContext with correlation_id, session_id, etc.
        
        Returns:
            Dictionary with optional "suppress_retry" and "delay_override_ms" keys.
            If suppress_retry is True, the retry should be skipped.
        
        Behavior:
            - Executes all registered PreRetry hooks in order
            - Merges outputs from all hooks (last one wins for decisions)
            - Returns combined output dict
            - Errors are handled per error_strategy (default: PRESERVE_EXISTING)
            - Fire-and-forget on error: retry proceeds normally if hook fails
        
        Raises:
            Nothing (errors are logged and handled per strategy)
        """
        if "PreRetry" not in self._hooks:
            logger.debug("No PreRetry hooks registered")
            return {}
        
        matchers = self._hooks["PreRetry"]
        combined_output: dict[str, Any] = {}
        
        try:
            for matcher in matchers:
                try:
                    hooks = matcher.hooks if hasattr(matcher, 'hooks') else []
                    
                    for hook_fn in hooks:
                        try:
                            # Execute hook with optional instrumentation
                            if self._instrumentation:
                                result, metrics = await self._instrumentation.instrument_hook_call(
                                    hook_fn.__name__,
                                    "PreRetry",
                                    hook_fn,
                                    event,
                                )
                            else:
                                result = await hook_fn(event)  # type: ignore
                            
                            # Validate result type
                            if not isinstance(result, dict):
                                logger.warning(
                                    f"PreRetry hook {hook_fn.__name__} returned non-dict: {type(result)}"
                                )
                                result = {}
                            
                            # Log execution
                            log_data = {
                                "event": "PreRetryHookExecuted",
                                "hook": hook_fn.__name__,
                                "correlation_id": context.correlation_id,
                                "session_id": context.session_id,
                                "attempt_number": event.get("attempt_number"),
                                "has_output": bool(result),
                            }
                            
                            if self._instrumentation:
                                recent_metrics = self._instrumentation.metrics
                                if recent_metrics:
                                    last_metric = recent_metrics[-1]
                                    log_data["elapsed_ms"] = round(last_metric.duration_ms)
                                    log_data["success"] = last_metric.success
                            
                            _audit(log_data)
                            
                            # Merge output (suppress_retry: any hook can suppress)
                            if result:
                                combined_output.update(result)
                        
                        except Exception as exc:
                            self._handle_hook_error(
                                hook_fn.__name__,
                                "PreRetry",
                                exc,
                                context,
                            )
                
                except Exception as exc:
                    logger.error(f"Error processing matcher for PreRetry: {exc}")
                    if self._error_strategy == ErrorStrategy.PRESERVE_EXISTING:
                        pass
                    else:
                        raise
        
        except Exception as exc:
            logger.error(f"Fatal error in PreRetry hook registry: {exc}")
            if self._error_strategy != ErrorStrategy.PRESERVE_EXISTING:
                raise
        
        return combined_output

    async def execute_on_first_setup(
            self,
            event: dict[str, Any],
            context: HookContext,
    ) -> dict[str, Any]:
        """
        Execute OnFirstSetup hooks during initial system setup with atomic marker.
        
        Uses atomic marker file approach (~/.cybersecsuite/.initialized) for race-safe
        initialization. Hooks are always executed on errors to allow partial setup.
        
        Returns:
            - {"skipped": True, "reason": "already_initialized"} if already initialized
            - {"initialized": True, ...hook_outputs...} if successful
            - {"initialized": False, "had_errors": True, ...hook_outputs...} if errors occurred
        """
        # Determine marker path: ~/.cybersecsuite/.initialized (respects CYBERSECSUITE_HOME)
        app_home = get_app_home()
        marker_path = app_home / ".initialized"
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Try to atomically claim initialization using exclusive create mode
        try:
            marker_path.open("x").close()
        except FileExistsError:
            logger.debug("OnFirstSetup already executed (marker exists)")
            return {
                "skipped": True,
                "reason": "already_initialized",
                "marker_path": str(marker_path),
            }
        except Exception as exc:
            logger.error(f"Error checking initialization marker: {exc}")
            return {
                "initialized": False,
                "had_errors": True,
                "error": f"marker check failed: {exc}",
            }
        
        if "OnFirstSetup" not in self._hooks:
            logger.debug("No OnFirstSetup hooks registered")
            return {"initialized": True}

        matchers = self._hooks["OnFirstSetup"]
        combined_output: dict[str, Any] = {}
        had_errors = False

        try:
            for matcher in matchers:
                try:
                    hooks = matcher.hooks if hasattr(matcher, 'hooks') else []

                    for hook_fn in hooks:
                        try:
                            # Execute hook with optional instrumentation
                            if self._instrumentation:
                                result, metrics = await self._instrumentation.instrument_hook_call(
                                    hook_fn.__name__,
                                    "OnFirstSetup",
                                    hook_fn,
                                    event,
                                )
                            else:
                                result = await hook_fn(event)  # type: ignore

                            # Validate result type
                            if not isinstance(result, dict):
                                logger.warning(
                                    f"OnFirstSetup hook {hook_fn.__name__} returned non-dict: {type(result)}"
                                )
                                result = {}

                            # Log execution
                            log_data = {
                                "event": "OnFirstSetupHookExecuted",
                                "hook": hook_fn.__name__,
                                "correlation_id": context.correlation_id,
                                "session_id": context.session_id,
                                "has_output": bool(result),
                            }

                            if self._instrumentation:
                                recent_metrics = self._instrumentation.metrics
                                if recent_metrics:
                                    last_metric = recent_metrics[-1]
                                    log_data["elapsed_ms"] = round(last_metric.duration_ms)
                                    log_data["success"] = last_metric.success

                            _audit(log_data)

                            # Merge output
                            if result:
                                combined_output.update(result)

                        except Exception as exc:
                            had_errors = True
                            self._handle_hook_error(
                                hook_fn.__name__,
                                "OnFirstSetup",
                                exc,
                                context,
                            )

                except Exception as exc:
                    had_errors = True
                    logger.error(f"Error processing matcher for OnFirstSetup: {exc}")
                    if self._error_strategy != ErrorStrategy.PRESERVE_EXISTING:
                        pass

        except Exception as exc:
            had_errors = True
            logger.error(f"Fatal error in OnFirstSetup hook registry: {exc}")

        if had_errors:
            try:
                marker_path.unlink()
            except Exception as exc:
                logger.error(f"Failed to delete marker after errors: {exc}")
            return {
                "initialized": False,
                "had_errors": True,
                **combined_output,
            }

        return {
            "initialized": True,
            **combined_output,
        }







    async def execute_on_recovery(
        self,
        event: dict[str, Any],
        context: HookContext,
    ) -> dict[str, Any]:
        """Execute OnRecovery hooks after successful recovery from error.
        
        OnRecovery hooks are fire-and-forget (async) logging/monitoring hooks
        that track when a system recovers from an error after retries.
        
        Use Cases:
            - Log successful recovery for monitoring/alerting
            - Update circuit breaker state (closed after recovery)
            - Send recovery notifications
            - Track MTTR (mean time to recovery)
            - Update metrics/dashboards
        
        Args:
            event: OnRecoveryEvent with error_type, recovered_after_attempts, etc.
            context: HookContext with correlation_id, session_id, etc.
        
        Returns:
            Dictionary with combined hook outputs (may be empty)
        
        Behavior:
            - Executes all registered OnRecovery hooks in order
            - Errors are logged but never raised (fire-and-forget semantics)
            - Does not block caller (fully async)
            - Multiple hooks can execute concurrently in future versions
        
        Raises:
            Nothing (errors are logged and discarded)
        """
        if "OnRecovery" not in self._hooks:
            logger.debug("No OnRecovery hooks registered")
            return {}
        
        matchers = self._hooks["OnRecovery"]
        combined_output: dict[str, Any] = {}
        
        try:
            for matcher in matchers:
                try:
                    hooks = matcher.hooks if hasattr(matcher, 'hooks') else []
                    
                    for hook_fn in hooks:
                        try:
                            # Execute hook with optional instrumentation
                            if self._instrumentation:
                                result, metrics = await self._instrumentation.instrument_hook_call(
                                    hook_fn.__name__,
                                    "OnRecovery",
                                    hook_fn,
                                    event,
                                )
                            else:
                                result = await hook_fn(event)  # type: ignore
                            
                            # Validate result type
                            if not isinstance(result, dict):
                                logger.warning(
                                    f"OnRecovery hook {hook_fn.__name__} returned non-dict: {type(result)}"
                                )
                                result = {}
                            
                            # Log execution
                            log_data = {
                                "event": "OnRecoveryHookExecuted",
                                "hook": hook_fn.__name__,
                                "correlation_id": context.correlation_id,
                                "session_id": context.session_id,
                                "error_type": event.get("error_type"),
                                "has_output": bool(result),
                            }
                            
                            if self._instrumentation:
                                recent_metrics = self._instrumentation.metrics
                                if recent_metrics:
                                    last_metric = recent_metrics[-1]
                                    log_data["elapsed_ms"] = round(last_metric.duration_ms)
                                    log_data["success"] = last_metric.success
                            
                            _audit(log_data)
                            
                            # Merge output
                            if result:
                                combined_output.update(result)
                        
                        except Exception as exc:
                            # Fire-and-forget: log but don't raise
                            logger.exception(
                                f"OnRecovery hook {hook_fn.__name__} failed: {exc}",
                                extra={"hook": hook_fn.__name__, "event": "OnRecovery"},
                            )
                
                except Exception as exc:
                    logger.error(f"Error processing matcher for OnRecovery: {exc}")
        
        except Exception as exc:
            logger.error(f"Fatal error in OnRecovery hook registry: {exc}")
        
        return combined_output
    
    async def execute_on_error(
        self,
        event: dict[str, Any],
        context: HookContext,
    ) -> dict[str, Any]:
        """Execute OnError hooks when error is final (non-recoverable).
        
        OnError hooks are fire-and-forget (async) logging/monitoring hooks
        that track when a system encounters a fatal/permanent error.
        
        Use Cases:
            - Log permanent failures for audit trail
            - Send alerts for fatal errors
            - Update monitoring dashboards
            - Trigger fallback workflows
            - Archive error context for investigation
        
        Args:
            event: OnErrorEvent with error_type, error_message, is_fatal, etc.
            context: HookContext with correlation_id, session_id, etc.
        
        Returns:
            Dictionary with combined hook outputs (may be empty)
        
        Behavior:
            - Executes all registered OnError hooks in order
            - Errors are logged but never raised (fire-and-forget semantics)
            - Does not block caller (fully async)
            - Multiple hooks can execute concurrently in future versions
        
        Raises:
            Nothing (errors are logged and discarded)
        """
        if "OnError" not in self._hooks:
            logger.debug("No OnError hooks registered")
            return {}
        
        matchers = self._hooks["OnError"]
        combined_output: dict[str, Any] = {}
        
        try:
            for matcher in matchers:
                try:
                    hooks = matcher.hooks if hasattr(matcher, 'hooks') else []
                    
                    for hook_fn in hooks:
                        try:
                            # Execute hook with optional instrumentation
                            if self._instrumentation:
                                result, metrics = await self._instrumentation.instrument_hook_call(
                                    hook_fn.__name__,
                                    "OnError",
                                    hook_fn,
                                    event,
                                )
                            else:
                                result = await hook_fn(event)  # type: ignore
                            
                            # Validate result type
                            if not isinstance(result, dict):
                                logger.warning(
                                    f"OnError hook {hook_fn.__name__} returned non-dict: {type(result)}"
                                )
                                result = {}
                            
                            # Log execution
                            log_data = {
                                "event": "OnErrorHookExecuted",
                                "hook": hook_fn.__name__,
                                "correlation_id": context.correlation_id,
                                "session_id": context.session_id,
                                "error_type": event.get("error_type"),
                                "is_fatal": event.get("is_fatal"),
                                "has_output": bool(result),
                            }
                            
                            if self._instrumentation:
                                recent_metrics = self._instrumentation.metrics
                                if recent_metrics:
                                    last_metric = recent_metrics[-1]
                                    log_data["elapsed_ms"] = round(last_metric.duration_ms)
                                    log_data["success"] = last_metric.success
                            
                            _audit(log_data)
                            
                            # Merge output
                            if result:
                                combined_output.update(result)
                        
                        except Exception as exc:
                            # Fire-and-forget: log but don't raise
                            logger.exception(
                                f"OnError hook {hook_fn.__name__} failed: {exc}",
                                extra={"hook": hook_fn.__name__, "event": "OnError"},
                            )
                
                except Exception as exc:
                    logger.error(f"Error processing matcher for OnError: {exc}")
        
        except Exception as exc:
            logger.error(f"Fatal error in OnError hook registry: {exc}")
        
        return combined_output




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

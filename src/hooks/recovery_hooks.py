"""Recovery hooks for error handling and retry management.

This module provides hooks for the error recovery system:
- PreRetry: Log and validate retry attempts, optionally suppress
- OnRecovery: Log successful recovery after retries
- OnError: Log fatal/permanent errors

Key Design:
    - Classify errors as transient (retryable) vs permanent (non-retryable)
    - Provide decision points for retry suppression
    - Track recovery metrics for monitoring
    - Support both sync logging and async audit trail updates
"""

import logging
from typing import Any

from hooks.core import OnErrorEvent, OnRecoveryEvent, PreRetryEvent

logger = logging.getLogger(__name__)


# ── Error Classification ───────────────────────────────────────────────────

# Transient errors: network, timeouts, rate limits (retryable)
TRANSIENT_ERROR_TYPES = {
    "TimeoutError",
    "ConnectionError",
    "RateLimitError",
    "HTTPError",
    "ConnectionResetError",
    "ConnectionRefusedError",
    "ConnectionAbortedError",
    "BrokenPipeError",
    "RemoteDisconnected",
    "TemporaryError",
    "ServiceUnavailable",
    "GatewayTimeout",
    "TooManyRequests",
}

# Permanent errors: auth, validation, not found (non-retryable)
PERMANENT_ERROR_TYPES = {
    "PermissionError",
    "ValueError",
    "KeyError",
    "NotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "InvalidArgumentError",
    "TypeError",
    "AttributeError",
    "UnicodeDecodeError",
    "NotImplementedError",
}


def is_transient_error(error_type: str) -> bool:
    """Determine if error is transient (retryable).
    
    Args:
        error_type: Exception class name (e.g., "TimeoutError")
    
    Returns:
        True if error is transient and can be retried
    """
    return error_type in TRANSIENT_ERROR_TYPES or error_type.endswith("Timeout")


def is_permanent_error(error_type: str) -> bool:
    """Determine if error is permanent (non-retryable).
    
    Args:
        error_type: Exception class name (e.g., "PermissionError")
    
    Returns:
        True if error is permanent and cannot be retried
    """
    return error_type in PERMANENT_ERROR_TYPES


# ── PreRetry Hook ──────────────────────────────────────────────────────────

async def on_pre_retry(event: PreRetryEvent) -> dict[str, Any]:
    """PreRetry hook: log retry attempt, classify error, optionally suppress.
    
    This hook examines the error and retry context to:
    - Log the retry attempt with context
    - Classify error as transient or permanent
    - Suppress retry for unretryable errors
    - Alert on repeated failures
    
    Args:
        event: PreRetryEvent with error_type, attempt_number, etc.
    
    Returns:
        Dictionary with optional suppress_retry decision:
        - {"suppress_retry": True} to prevent retry
        - {} to allow retry to proceed
        - {"delay_override_ms": 5000} to override retry delay (future)
    
    Logic:
        1. Log the retry attempt with context
        2. Check if error is permanent (non-retryable)
        3. Check if max attempts exceeded (suppress on last attempt is natural)
        4. Alert if this is a frequently failing error
        5. Return suppress decision
    """
    error_type = event.get("error_type", "Unknown")
    attempt_number = event.get("attempt_number", 1)
    max_attempts = event.get("max_attempts", 3)
    error_message = event.get("error_message", "")
    tool_name = event.get("tool_name", "unknown")
    correlation_id = event.get("correlation_id", "unknown")
    
    # Log the retry attempt
    logger.info(
        f"Retry attempt {attempt_number}/{max_attempts} for {tool_name}: {error_type}",
        extra={
            "event": "RetryAttempt",
            "tool": tool_name,
            "error_type": error_type,
            "attempt": attempt_number,
            "max_attempts": max_attempts,
            "correlation_id": correlation_id,
        },
    )
    
    # Check if error is permanent (non-retryable)
    if is_permanent_error(error_type):
        logger.warning(
            f"Suppressing retry for permanent error {error_type}: {error_message}",
            extra={
                "event": "RetrySupressed",
                "reason": "permanent_error",
                "error_type": error_type,
                "correlation_id": correlation_id,
            },
        )
        return {"suppress_retry": True}
    
    # Check if we've reached max attempts (next retry would be pointless)
    if attempt_number >= max_attempts:
        logger.warning(
            f"Suppressing retry: max attempts reached ({attempt_number}/{max_attempts})",
            extra={
                "event": "RetrySupressed",
                "reason": "max_attempts",
                "attempt": attempt_number,
                "max_attempts": max_attempts,
                "correlation_id": correlation_id,
            },
        )
        return {"suppress_retry": True}
    
    # Transient errors are retryable
    if is_transient_error(error_type):
        logger.debug(
            f"Transient error {error_type}, allowing retry {attempt_number}/{max_attempts}",
            extra={
                "event": "RetryAllowed",
                "reason": "transient_error",
                "error_type": error_type,
                "attempt": attempt_number,
                "correlation_id": correlation_id,
            },
        )
        return {}  # Allow retry
    
    # Unknown error: allow retry (conservative approach)
    logger.debug(
        f"Unknown error type {error_type}, allowing retry (conservative)",
        extra={
            "event": "RetryAllowed",
            "reason": "unknown_error",
            "error_type": error_type,
            "attempt": attempt_number,
            "correlation_id": correlation_id,
        },
    )
    return {}  # Allow retry


# ── OnRecovery Hook ────────────────────────────────────────────────────────

async def on_recovery(event: OnRecoveryEvent) -> dict[str, Any]:
    """OnRecovery hook: log successful recovery after retries.
    
    This hook is called when a system recovers from an error after one or more
    retry attempts. It's useful for:
    - Logging success (contrast with failure)
    - Updating circuit breaker state (open -> closed)
    - Sending recovery notifications
    - Tracking MTTR (mean time to recovery)
    
    Args:
        event: OnRecoveryEvent with error_type, recovered_after_attempts, etc.
    
    Returns:
        Empty dict {} (fire-and-forget logging)
    
    Behavior:
        - Always logs recovery event
        - Never raises (fire-and-forget)
        - Errors are logged and discarded
    """
    error_type = event.get("error_type", "Unknown")
    recovered_after_attempts = event.get("recovered_after_attempts", 1)
    total_retry_duration_ms = event.get("total_retry_duration_ms", 0)
    correlation_id = event.get("correlation_id", "unknown")
    
    logger.info(
        f"Recovered from {error_type} after {recovered_after_attempts} attempts "
        f"({total_retry_duration_ms:.0f}ms total)",
        extra={
            "event": "RecoverySuccess",
            "error_type": error_type,
            "attempts": recovered_after_attempts,
            "duration_ms": total_retry_duration_ms,
            "correlation_id": correlation_id,
        },
    )
    
    return {}  # Fire-and-forget


# ── OnError Hook ───────────────────────────────────────────────────────────

async def on_error(event: OnErrorEvent) -> dict[str, Any]:
    """OnError hook: log fatal/permanent errors.
    
    This hook is called when a system encounters a fatal or permanent error
    that cannot be recovered through retries. It's useful for:
    - Logging permanent failures for audit trail
    - Sending alerts for fatal errors
    - Updating monitoring dashboards
    - Triggering fallback workflows
    
    Args:
        event: OnErrorEvent with error_type, error_message, is_fatal, etc.
    
    Returns:
        Empty dict {} (fire-and-forget logging)
    
    Behavior:
        - Always logs error event with full context
        - Logs as ERROR if fatal, WARNING if transient
        - Never raises (fire-and-forget)
        - Errors are logged and discarded
    """
    error_type = event.get("error_type", "Unknown")
    error_message = event.get("error_message", "")
    is_fatal = event.get("is_fatal", True)
    attempt_number = event.get("attempt_number", 1)
    correlation_id = event.get("correlation_id", "unknown")
    
    # Determine log level based on error type
    is_permanent = is_permanent_error(error_type)
    
    log_func = logger.error if (is_fatal or is_permanent) else logger.warning
    
    log_func(
        f"{'Fatal' if is_fatal else 'Non-fatal'} error {error_type} after {attempt_number} attempts: {error_message}",
        extra={
            "event": "ErrorFinal",
            "error_type": error_type,
            "is_fatal": is_fatal,
            "is_permanent": is_permanent,
            "attempts": attempt_number,
            "correlation_id": correlation_id,
        },
    )
    
    return {}  # Fire-and-forget

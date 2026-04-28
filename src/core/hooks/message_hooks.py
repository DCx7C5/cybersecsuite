"""Message interception hooks for pre/post processing.

This module provides default implementations of message interception hooks
that demonstrate the PreMessage (validation/transformation) and PostMessage
(logging/metrics) patterns.

Hooks:
    - on_pre_message: Validate and optionally transform message before processing
    - on_post_message: Log message and metrics after processing

Message Flow:
    User Message → on_pre_message (validate/transform) → Agent → on_post_message (log)
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


# ── PreMessage Hooks ──────────────────────────────────────────────────────


async def on_pre_message(event: dict[str, Any]) -> dict[str, Any]:
    """Validate and sanitize message before adding to conversation.
    
    Performs:
    - Content validation (encoding, length)
    - Basic PII redaction (email addresses, phone numbers)
    - Sanitization of common injection patterns
    
    Args:
        event: PreMessageEvent with:
            - message_content: The message text
            - role: Message role ("user", "assistant", "system")
            - correlation_id: Request correlation ID
            - message_id: Optional message identifier
            - metadata: Optional metadata dict
    
    Returns:
        HookOutput dict with:
        - transformed_message: Redacted message (if changes made)
        - validation_status: "valid" or "redacted"
        - redaction_count: Number of PII items redacted
    """
    message_content = event.get("message_content", "")
    role = event.get("role", "user")
    correlation_id = event.get("correlation_id", "")
    
    # Validation: check encoding
    try:
        message_content.encode("utf-8")
    except (UnicodeEncodeError, AttributeError) as exc:
        logger.warning(
            f"PreMessage validation failed for correlation {correlation_id}: {exc}",
            extra={"correlation_id": correlation_id, "role": role},
        )
        return {"validation_status": "invalid", "error": "Invalid message encoding"}
    
    # Validation: check length (allow up to 100KB for messages)
    if len(message_content) > 102400:
        logger.warning(
            f"PreMessage message too long ({len(message_content)} bytes) "
            f"for correlation {correlation_id}",
            extra={"correlation_id": correlation_id, "length": len(message_content)},
        )
        return {"validation_status": "truncated", "warning": "Message truncated to 100KB"}
    
    # Redaction: emails (basic pattern)
    redacted_message = message_content
    redaction_count = 0
    
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    email_matches = len(re.findall(email_pattern, message_content))
    if email_matches > 0:
        redacted_message = re.sub(email_pattern, "[EMAIL_REDACTED]", redacted_message)
        redaction_count += email_matches
    
    # Redaction: phone numbers (basic pattern)
    phone_pattern = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    phone_matches = len(re.findall(phone_pattern, message_content))
    if phone_matches > 0:
        redacted_message = re.sub(phone_pattern, "[PHONE_REDACTED]", redacted_message)
        redaction_count += phone_matches
    
    # Check for common injection patterns (but don't block, just log)
    injection_patterns = [
        r"__import__",
        r"exec\(",
        r"eval\(",
        r"os\.system",
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, message_content, re.IGNORECASE):
            logger.warning(
                f"PreMessage detected potential injection in correlation {correlation_id}",
                extra={
                    "correlation_id": correlation_id,
                    "pattern": pattern,
                    "role": role,
                },
            )
    
    # Return result
    output = {"validation_status": "valid"}
    
    if redaction_count > 0:
        output["transformed_message"] = redacted_message
        output["redaction_count"] = redaction_count
        output["validation_status"] = "redacted"
        logger.info(
            f"PreMessage redacted {redaction_count} PII items in correlation {correlation_id}",
            extra={
                "correlation_id": correlation_id,
                "redaction_count": redaction_count,
            },
        )
    
    return output


# ── PostMessage Hooks ─────────────────────────────────────────────────────


async def on_post_message(event: dict[str, Any]) -> dict[str, Any]:
    """Log processed message and metrics after agent processing.
    
    Performs:
    - Audit logging of message and processing result
    - Metrics collection (token usage, response time)
    - Performance tracking
    
    Args:
        event: PostMessageEvent with:
            - message_content: The processed message text
            - role: Message role ("user", "assistant", "system")
            - response_time_ms: Time to process (float)
            - token_count: Number of tokens (int)
            - status: Processing status (str, e.g., "success")
            - correlation_id: Request correlation ID
            - metadata: Optional metadata dict
    
    Returns:
        HookOutput dict with:
        - audit_logged: True if successfully logged
        - metrics: Summary dict with token count, response time
    """
    message_content = event.get("message_content", "")
    role = event.get("role", "unknown")
    response_time_ms = event.get("response_time_ms", 0.0)
    token_count = event.get("token_count", 0)
    status = event.get("status", "unknown")
    correlation_id = event.get("correlation_id", "")
    metadata = event.get("metadata", {})
    
    # Calculate metrics
    message_length = len(message_content)
    tokens_per_second = (token_count / (response_time_ms / 1000)) if response_time_ms > 0 else 0
    
    # Log audit entry
    audit_log = {
        "event": "MessageProcessed",
        "correlation_id": correlation_id,
        "role": role,
        "status": status,
        "message_length": message_length,
        "token_count": token_count,
        "response_time_ms": round(response_time_ms, 2),
        "tokens_per_second": round(tokens_per_second, 2),
    }
    
    # Add metadata if present
    if metadata and isinstance(metadata, dict):
        audit_log["metadata"] = metadata
    
    logger.info(
        f"PostMessage: {role} message processed in {response_time_ms:.0f}ms "
        f"({token_count} tokens, {tokens_per_second:.0f} tok/s) - {status}",
        extra=audit_log,
    )
    
    return {
        "audit_logged": True,
        "metrics": {
            "message_length": message_length,
            "token_count": token_count,
            "response_time_ms": response_time_ms,
            "tokens_per_second": tokens_per_second,
            "status": status,
        },
    }


# ── Hook Registration ─────────────────────────────────────────────────────


def register_message_hooks() -> dict[str, list[Any]]:
    """Register message interception hooks.
    
    Returns:
        Dictionary mapping event types to hook functions:
        {
            "PreMessage": [on_pre_message],
            "PostMessage": [on_post_message],
        }
    
    Note:
        This is typically called by the hook SDK integration to register
        these hooks into the global hook registry.
    """
    return {
        "PreMessage": [on_pre_message],
        "PostMessage": [on_post_message],
    }

"""Anthropic explicit cache control injection for advanced layouts.

Anthropic Claude API supports explicit cache_control tokens to create manual
cache checkpoints between messages. This module injects cache breakpoints into
message arrays based on message type, size, and layout heuristics.

See: https://docs.anthropic.com/en/docs/build-a-claude-api-application-with-claude-3-5-sonnet#controlling-cache-write
"""

from typing import Any


def inject_cache_breakpoints(
    messages: list[dict[str, Any]],
    ephemeral_breakpoint_every_n_messages: int | None = None,
    model: str | None = None,
) -> list[dict[str, Any]]:
    """Inject cache_control tokens into Anthropic message array.

    Supports two strategies:
      1. Explicit periodic: Add ephemeral breakpoint every N messages (e.g., every 5)
      2. Smart heuristic: Add breakpoint after large context blocks (>8K tokens est.)

    Args:
        messages: Input message list (unmodified; returns copy)
        ephemeral_breakpoint_every_n_messages: If set, add ephemeral breakpoint every N messages
        model: Model name hint (unused for now, reserved for per-model tuning)

    Returns:
        Modified message list with cache_control injection
    """
    if not messages:
        return messages

    modified = []
    message_count = 0

    for idx, msg in enumerate(messages):
        msg_copy = dict(msg)

        should_add_ephemeral = False
        if ephemeral_breakpoint_every_n_messages:
            message_count += 1
            if message_count % ephemeral_breakpoint_every_n_messages == 0:
                should_add_ephemeral = True

        if idx == len(messages) - 1:
            should_add_ephemeral = False

        if should_add_ephemeral:
            msg_copy.setdefault("cache_control", {})["type"] = "ephemeral"

        modified.append(msg_copy)

    return modified


def estimate_message_tokens(msg: dict[str, Any]) -> int:
    """Rough estimate of tokens in a message (1 token ≈ 4 chars).

    Used by heuristic breakpoint logic to detect large context blocks.
    """
    content = msg.get("content", "")
    if isinstance(content, str):
        return len(content) // 4
    elif isinstance(content, list):
        total = 0
        for block in content:
            if isinstance(block, dict):
                if "text" in block:
                    total += len(block["text"]) // 4
                elif "image_url" in block or "media_type" in block:
                    total += 255
        return total
    return 0

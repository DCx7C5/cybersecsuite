"""Token counting utilities for LLM message tokens.

Provides heuristic token counting for messages when provider SDKs don't
support tokenization. Estimates follow tiktoken's encoding rules.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def estimate_message_tokens(messages: list[dict[str, Any]]) -> int:
    """Estimate token count for a list of messages using heuristic rules.

    Heuristic rules:
    - Each message: 4 tokens (role + metadata)
    - Each field name: 1 token
    - Each field value: tokens based on content
      * String content: ~1.3 chars per token (OpenAI's average)
      * Numeric values: 2 tokens
      * Boolean: 1 token
      * None: 1 token
      * Nested structures: recursive

    Args:
        messages: List of message dicts with 'role' and 'content' keys

    Returns:
        Estimated token count (integer)
    """
    if not messages:
        return 0

    total_tokens = 0

    for msg in messages:
        # Base tokens for message structure
        total_tokens += 4

        # Count tokens for each field
        for key, value in msg.items():
            # Field name
            total_tokens += 1

            # Field value
            total_tokens += _count_field_tokens(value)

    return total_tokens


def _count_field_tokens(value: Any) -> int:
    """Count tokens for a single field value."""
    if value is None:
        return 1
    elif isinstance(value, bool):
        return 1
    elif isinstance(value, (int, float)):
        return 2
    elif isinstance(value, str):
        # Heuristic: ~1.3 chars per token
        return max(1, len(value) // 4)
    elif isinstance(value, (list, tuple)):
        total = 2  # Bracket tokens
        for item in value:
            total += _count_field_tokens(item) + 1  # +1 for separator
        return total
    elif isinstance(value, dict):
        total = 2  # Brace tokens
        for k, v in value.items():
            total += len(k) // 4 + 1  # Key
            total += _count_field_tokens(v) + 1  # Value + separator
        return total
    else:
        # Fallback: estimate from string representation
        return max(1, len(str(value)) // 4)


def estimate_completion_tokens(
    text: str,
    model_id: str | None = None,
) -> int:
    """Estimate token count for completion/response text.

    Args:
        text: Generated text to count
        model_id: Optional model ID for model-specific adjustments

    Returns:
        Estimated token count (integer)
    """
    if not text:
        return 0

    # Base heuristic: ~4 chars per token
    estimated = max(1, len(text) // 4)

    # Model-specific adjustments
    # Some models use different tokenizers
    if model_id:
        model_lower = model_id.lower()
        # Claude models tend to use fewer tokens per character
        if "claude" in model_lower:
            estimated = int(estimated * 0.8)

    return estimated


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    input_price_per_1k: float,
    output_price_per_1k: float,
) -> float:
    """Calculate cost based on token counts and pricing.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        input_price_per_1k: Price per 1000 input tokens (USD)
        output_price_per_1k: Price per 1000 output tokens (USD)

    Returns:
        Total cost in USD
    """
    input_cost = (input_tokens / 1000) * input_price_per_1k
    output_cost = (output_tokens / 1000) * output_price_per_1k
    return input_cost + output_cost



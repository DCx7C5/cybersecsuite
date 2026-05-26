"""Tests for token counting utilities and CSSLLMClient.estimate_tokens().

Tests both the heuristic token counter and the integration with CSSLLMClient.
"""

import pytest

from css.core.utils.token_counter import (
    estimate_message_tokens,
    estimate_completion_tokens,
    calculate_cost,
)
from css.core.sdks.css_client import CSSLLMClient


class TestEstimateMessageTokens:
    """Test heuristic message token counting."""

    def test_empty_messages(self) -> None:
        """Empty message list returns 0 tokens."""
        assert estimate_message_tokens([]) == 0

    def test_single_simple_message(self) -> None:
        """Single message with role and content is counted correctly."""
        messages = [{"role": "user", "content": "Hello"}]
        tokens = estimate_message_tokens(messages)
        # 4 (message overhead) + 1 (field 'role') + 1 (field 'content')
        # + 1 (value 'user') + 1 ('Hello' ~1 token)
        assert tokens >= 4
        assert tokens <= 15

    def test_multiple_messages(self) -> None:
        """Multiple messages accumulate tokens."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        tokens = estimate_message_tokens(messages)
        # Each message: 4 + fields + values
        assert tokens >= 8  # Minimum 4 tokens per message

    def test_long_content(self) -> None:
        """Longer content increases token count."""
        short_msg = [{"role": "user", "content": "Hi"}]
        long_msg = [{"role": "user", "content": "Hi" * 100}]

        short_tokens = estimate_message_tokens(short_msg)
        long_tokens = estimate_message_tokens(long_msg)

        assert long_tokens > short_tokens

    def test_nested_structures(self) -> None:
        """Nested dicts and lists are counted."""
        messages = [
            {
                "role": "user",
                "content": "Test",
                "tool_calls": [{"name": "func", "args": {"key": "value"}}],
            }
        ]
        tokens = estimate_message_tokens(messages)
        assert tokens > 4  # More than just message overhead

    def test_various_types(self) -> None:
        """Various field types are counted correctly."""
        messages = [
            {
                "role": "system",
                "content": "You are helpful",
                "max_tokens": 1000,
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": True,
                "metadata": None,
            }
        ]
        tokens = estimate_message_tokens(messages)
        # Should count all field types
        assert tokens > 4


class TestEstimateCompletionTokens:
    """Test completion/response token estimation."""

    def test_empty_text(self) -> None:
        """Empty text returns 0 tokens."""
        assert estimate_completion_tokens("") == 0

    def test_short_text(self) -> None:
        """Short text returns 1+ tokens."""
        tokens = estimate_completion_tokens("Hi")
        assert tokens >= 1

    def test_longer_text(self) -> None:
        """Longer text increases token count."""
        short = estimate_completion_tokens("Hello")
        long = estimate_completion_tokens("Hello" * 100)
        assert long > short

    def test_claude_adjustment(self) -> None:
        """Claude models use different tokenizer (fewer tokens)."""
        text = "This is a test message"
        gpt_tokens = estimate_completion_tokens(text, model_id="gpt-4")
        claude_tokens = estimate_completion_tokens(text, model_id="claude-opus")
        # Claude should estimate fewer tokens for same text
        assert claude_tokens <= gpt_tokens


class TestCalculateCost:
    """Test cost calculation."""

    def test_zero_tokens(self) -> None:
        """Zero tokens = zero cost."""
        cost = calculate_cost(0, 0, 0.01, 0.03)
        assert cost == 0.0

    def test_basic_calculation(self) -> None:
        """Cost is calculated correctly."""
        # 1000 input tokens @ $0.01/1k = $0.01
        # 1000 output tokens @ $0.03/1k = $0.03
        cost = calculate_cost(1000, 1000, 0.01, 0.03)
        assert abs(cost - 0.04) < 0.0001

    def test_partial_1k(self) -> None:
        """Partial 1k token usage is calculated correctly."""
        # 500 input tokens @ $0.01/1k = $0.005
        cost = calculate_cost(500, 0, 0.01, 0.03)
        assert abs(cost - 0.005) < 0.0001

    def test_different_pricing(self) -> None:
        """Different pricing tiers are applied correctly."""
        # Input: 1000 @ $0.001/1k, Output: 1000 @ $0.002/1k
        cost = calculate_cost(1000, 1000, 0.001, 0.002)
        assert abs(cost - 0.003) < 0.0001


class TestCSSLLMClientEstimateTokens:
    """Test CSSLLMClient.estimate_tokens() method."""

    @pytest.mark.asyncio
    async def test_estimate_tokens_simple(self) -> None:
        """Estimate tokens for simple messages."""
        client = CSSLLMClient()
        messages = [{"role": "user", "content": "Hello"}]

        tokens = await client.estimate_tokens("gpt-4", messages)

        assert isinstance(tokens, int)
        assert tokens > 0

    @pytest.mark.asyncio
    async def test_estimate_tokens_empty(self) -> None:
        """Estimate tokens for empty messages returns 0."""
        client = CSSLLMClient()
        tokens = await client.estimate_tokens("gpt-4", [])

        assert tokens == 0

    @pytest.mark.asyncio
    async def test_estimate_tokens_multiple(self) -> None:
        """Estimate tokens for multiple messages."""
        client = CSSLLMClient()
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "What is 2+2?"},
            {"role": "assistant", "content": "2+2 = 4"},
            {"role": "user", "content": "Why?"},
        ]

        tokens = await client.estimate_tokens("gpt-4", messages)

        assert isinstance(tokens, int)
        assert tokens > 20  # Should have reasonable token count

    @pytest.mark.asyncio
    async def test_estimate_tokens_consistent(self) -> None:
        """Multiple calls return consistent estimates."""
        client = CSSLLMClient()
        messages = [{"role": "user", "content": "Test"}]

        tokens1 = await client.estimate_tokens("gpt-4", messages)
        tokens2 = await client.estimate_tokens("gpt-4", messages)

        assert tokens1 == tokens2


__all__ = [
    "TestEstimateMessageTokens",
    "TestEstimateCompletionTokens",
    "TestCalculateCost",
    "TestCSSLLMClientEstimateTokens",
]

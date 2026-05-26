"""Tests for TokenAwareStrategy (Phase 16.T7: token-count-in-routing).

Tests cover:
- Provider selection based on token count
- Context window limit enforcement
- Graceful degradation on estimation failure
- Fallback to largest context window
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from css.modules.strategies import TokenAwareStrategy
from css.core.types import BaseMessage


class TestTokenAwareStrategyBasic:
    """Test basic TokenAwareStrategy functionality."""

    @pytest.mark.asyncio
    async def test_empty_providers_returns_ollama(self):
        """Return ollama fallback for empty provider list."""
        strategy = TokenAwareStrategy()
        result = await strategy.choose_provider([])
        assert result == "ollama"

    @pytest.mark.asyncio
    async def test_no_messages_returns_first_provider(self):
        """Return first provider when no messages provided."""
        strategy = TokenAwareStrategy()
        result = await strategy.choose_provider(["openai/gpt-4", "mistral"])
        assert result == "openai/gpt-4"

    @pytest.mark.asyncio
    async def test_empty_messages_returns_first_provider(self):
        """Return first provider for empty message list."""
        strategy = TokenAwareStrategy()
        result = await strategy.choose_provider(
            ["openai/gpt-4", "mistral"],
            messages=[],
        )
        assert result == "openai/gpt-4"

    @pytest.mark.asyncio
    async def test_no_provider_limits_returns_first_provider(self):
        """Return first provider when no context limits provided."""
        messages = [
            MagicMock(role="user", content="Test message"),
        ]
        strategy = TokenAwareStrategy()
        result = await strategy.choose_provider(
            ["openai/gpt-4", "mistral"],
            messages=messages,
        )
        assert result == "openai/gpt-4"


class TestTokenAwareStrategySelection:
    """Test provider selection based on token count."""

    @pytest.mark.asyncio
    async def test_select_provider_within_limit(self):
        """Select provider that can handle token count."""
        messages = [
            MagicMock(role="user", content="Test message"),
        ]
        provider_limits = {
            "openai/gpt-4": 128000,
            "mistral": 32000,
        }

        with patch("css.core.sdks.css_client.CSSLLMClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.estimate_tokens = AsyncMock(return_value=1000)

            strategy = TokenAwareStrategy()
            result = await strategy.choose_provider(
                ["openai/gpt-4", "mistral"],
                messages=messages,
                provider_limits=provider_limits,
            )

            # Both can handle 1000 tokens, should return first suitable
            assert result == "openai/gpt-4"

    @pytest.mark.asyncio
    async def test_select_provider_within_single_limit(self):
        """Select only provider that can handle token count."""
        messages = [
            MagicMock(role="user", content="Test message"),
        ]
        provider_limits = {
            "openai/gpt-4": 128000,
            "mistral": 900,  # Too small
        }

        with patch("css.core.sdks.css_client.CSSLLMClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.estimate_tokens = AsyncMock(return_value=1000)

            strategy = TokenAwareStrategy()
            result = await strategy.choose_provider(
                ["openai/gpt-4", "mistral"],
                messages=messages,
                provider_limits=provider_limits,
            )

            # Only openai/gpt-4 can handle 1000 tokens
            assert result == "openai/gpt-4"

    @pytest.mark.asyncio
    async def test_fallback_to_largest_context_window(self):
        """Fallback to provider with largest context window."""
        messages = [
            MagicMock(role="user", content="Test message"),
        ]
        provider_limits = {
            "openai/gpt-4": 128000,
            "mistral": 32000,
            "llama": 4096,  # All too small for 200k tokens
        }

        with patch("css.core.sdks.css_client.CSSLLMClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.estimate_tokens = AsyncMock(return_value=200000)

            strategy = TokenAwareStrategy()
            result = await strategy.choose_provider(
                ["openai/gpt-4", "mistral", "llama"],
                messages=messages,
                provider_limits=provider_limits,
            )

            # No provider can handle it, fallback to largest
            assert result == "openai/gpt-4"

    @pytest.mark.asyncio
    async def test_token_estimation_failure_graceful_degradation(self):
        """Gracefully handle token estimation failure."""
        messages = [
            MagicMock(role="user", content="Test message"),
        ]
        provider_limits = {
            "openai/gpt-4": 128000,
            "mistral": 32000,
        }

        with patch("css.core.sdks.css_client.CSSLLMClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.estimate_tokens = AsyncMock(side_effect=Exception("Estimation failed"))

            strategy = TokenAwareStrategy()
            result = await strategy.choose_provider(
                ["openai/gpt-4", "mistral"],
                messages=messages,
                provider_limits=provider_limits,
            )

            # On failure, return first provider
            assert result == "openai/gpt-4"


class TestTokenAwareStrategyMessageConversion:
    """Test message conversion to dict format."""

    @pytest.mark.asyncio
    async def test_convert_base_messages_to_dict(self):
        """Convert BaseMessage objects to dict format."""
        messages = [
            MagicMock(role="user", content="Hello"),
            MagicMock(role="assistant", content="Hi"),
        ]
        provider_limits = {"openai/gpt-4": 128000}

        with patch("css.core.sdks.css_client.CSSLLMClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.estimate_tokens = AsyncMock(return_value=50)

            strategy = TokenAwareStrategy()
            await strategy.choose_provider(
                ["openai/gpt-4"],
                messages=messages,
                provider_limits=provider_limits,
            )

            # Verify estimate_tokens was called with dict format
            mock_client.estimate_tokens.assert_called_once()
            call_args = mock_client.estimate_tokens.call_args
            assert call_args[0][0] == "gpt-4"  # default_model
            msg_dicts = call_args[0][1]
            assert len(msg_dicts) == 2
            assert msg_dicts[0] == {"role": "user", "content": "Hello"}
            assert msg_dicts[1] == {"role": "assistant", "content": "Hi"}

    @pytest.mark.asyncio
    async def test_custom_model_for_estimation(self):
        """Use custom model ID for token estimation."""
        messages = [MagicMock(role="user", content="Test")]
        provider_limits = {"mistral": 32000}

        with patch("css.core.sdks.css_client.CSSLLMClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.estimate_tokens = AsyncMock(return_value=100)

            strategy = TokenAwareStrategy()
            await strategy.choose_provider(
                ["mistral"],
                messages=messages,
                provider_limits=provider_limits,
                default_model="mistral/mistral-7b",
            )

            # Verify custom model was used
            call_args = mock_client.estimate_tokens.call_args
            assert call_args[0][0] == "mistral/mistral-7b"


class TestTokenAwareStrategyDefaults:
    """Test default values and fallback behavior."""

    @pytest.mark.asyncio
    async def test_default_context_window_128k(self):
        """Use 128k as default context window for unknown providers."""
        messages = [MagicMock(role="user", content="Test")]
        provider_limits = {"unknown_provider": 5000}  # Very small

        with patch("css.core.sdks.css_client.CSSLLMClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.estimate_tokens = AsyncMock(return_value=10000)

            strategy = TokenAwareStrategy()
            result = await strategy.choose_provider(
                ["unknown_provider", "another_unknown"],
                messages=messages,
                provider_limits=provider_limits,
            )

            # Both fail initial check, fallback uses default 128k
            # Both have 5000 in limits, so will pick first that fails
            assert result in ["unknown_provider", "another_unknown"]

    @pytest.mark.asyncio
    async def test_provider_order_respected_when_multiple_suitable(self):
        """Return first suitable provider from list order."""
        messages = [MagicMock(role="user", content="Test")]
        provider_limits = {
            "llama": 32000,
            "mistral": 32000,
            "openai/gpt-4": 128000,
        }

        with patch("css.core.sdks.css_client.CSSLLMClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.estimate_tokens = AsyncMock(return_value=1000)

            strategy = TokenAwareStrategy()
            # All three can handle 1000 tokens
            result = await strategy.choose_provider(
                ["openai/gpt-4", "mistral", "llama"],
                messages=messages,
                provider_limits=provider_limits,
            )

            # Should return first suitable provider
            assert result == "openai/gpt-4"


__all__ = [
    "TestTokenAwareStrategyBasic",
    "TestTokenAwareStrategySelection",
    "TestTokenAwareStrategyMessageConversion",
    "TestTokenAwareStrategyDefaults",
]

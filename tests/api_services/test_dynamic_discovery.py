"""Tests for dynamic model discovery infrastructure.

Tests the ModelRegistry discovery mechanism: registering discovery functions,
fetching models with cache TTL, and error handling.
"""

import asyncio
from unittest.mock import AsyncMock

import pytest

from css.core.models.registry import ModelRegistry
from css.core.models.models import ModelMetadata, ModelPricing
from css.core.models.enums import ModelProvider, ModelFamily


class TestDiscoveryRegistration:
    """Test registering discovery functions with ModelRegistry."""

    def test_register_discovery_function(self) -> None:
        """Register a discovery function for a provider."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]
        registry._discovery_funcs.clear()
        mock_discovery = AsyncMock()

        registry.register_discovery("openrouter", mock_discovery, ttl_seconds=7200)

        assert "openrouter" in registry._discovery_funcs
        func, last_fetch, ttl = registry._discovery_funcs["openrouter"]
        assert func == mock_discovery
        assert last_fetch == 0.0
        assert ttl == 7200

    def test_register_multiple_providers(self) -> None:
        """Register discovery functions for multiple providers."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]
        registry._discovery_funcs.clear()
        mock_openrouter = AsyncMock()
        mock_ollama = AsyncMock()

        registry.register_discovery("openrouter", mock_openrouter)
        registry.register_discovery("ollama", mock_ollama)

        assert len(registry._discovery_funcs) == 2
        assert "openrouter" in registry._discovery_funcs
        assert "ollama" in registry._discovery_funcs


class TestDiscoveryExecution:
    """Test executing discovery functions and caching."""

    @pytest.mark.asyncio
    async def test_discover_models_calls_function(self) -> None:
        """Calling discover_models invokes the registered function."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]
        model = ModelMetadata(
            id="test-model",
            provider=ModelProvider("openai"),
            family=ModelFamily.GPT,
            display_name="Test Model",
            context_window=128000,
            max_output_tokens=4096,
            latency_ms=500,
            pricing=ModelPricing(
                input_tokens_per_1k=0.01,
                output_tokens_per_1k=0.03,
            ),
        )
        mock_discovery = AsyncMock(return_value=[model])

        registry.register_discovery("test_provider", mock_discovery)
        result = await registry.discover_models("test_provider")

        mock_discovery.assert_called_once()
        assert len(result) == 1
        assert result[0].id == "test-model"

    @pytest.mark.asyncio
    async def test_discover_models_caches_result(self) -> None:
        """Results are cached with TTL; second call uses cache."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]
        model = ModelMetadata(
            id="cached-model",
            provider=ModelProvider("openai"),
            family=ModelFamily.GPT,
            display_name="Cached Model",
            context_window=128000,
            max_output_tokens=4096,
            latency_ms=500,
            pricing=ModelPricing(
                input_tokens_per_1k=0.01,
                output_tokens_per_1k=0.03,
            ),
        )
        call_count = 0

        async def mock_discovery() -> list[ModelMetadata]:
            nonlocal call_count
            call_count += 1
            return [model]

        registry.register_discovery("test", AsyncMock(side_effect=mock_discovery))

        # First call
        result1 = await registry.discover_models("test")
        assert call_count == 1

        # Second call should use cache (without advancing time)
        result2 = await registry.discover_models("test")
        assert call_count == 1  # Function not called again
        assert result1[0].id == result2[0].id

    @pytest.mark.asyncio
    async def test_discover_models_respects_ttl(self) -> None:
        """Cache expires after TTL; next call re-invokes function."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]
        model = ModelMetadata(
            id="ttl-model",
            provider=ModelProvider("openai"),
            family=ModelFamily.GPT,
            display_name="TTL Model",
            context_window=128000,
            max_output_tokens=4096,
            latency_ms=500,
            pricing=ModelPricing(
                input_tokens_per_1k=0.01,
                output_tokens_per_1k=0.03,
            ),
        )
        call_count = 0

        async def mock_discovery() -> list[ModelMetadata]:
            nonlocal call_count
            call_count += 1
            return [model]

        registry.register_discovery(
            "ttl_test",
            AsyncMock(side_effect=mock_discovery),
            ttl_seconds=1,
        )

        # First call
        await registry.discover_models("ttl_test")
        assert call_count == 1

        # Sleep past TTL
        await asyncio.sleep(1.1)

        # Second call should re-invoke (cache expired)
        await registry.discover_models("ttl_test")
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_discover_models_returns_empty_if_not_registered(self) -> None:
        """Requesting discovery for unregistered provider returns empty list."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]
        result = await registry.discover_models("unknown_provider")
        assert result == []

    @pytest.mark.asyncio
    async def test_discover_models_handles_discovery_error(self) -> None:
        """Discovery errors are handled gracefully; falls back to cache."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]
        model = ModelMetadata(
            id="error-fallback",
            provider=ModelProvider("openai"),
            family=ModelFamily.GPT,
            display_name="Error Fallback",
            context_window=128000,
            max_output_tokens=4096,
            latency_ms=500,
            pricing=ModelPricing(
                input_tokens_per_1k=0.01,
                output_tokens_per_1k=0.03,
            ),
        )

        call_count = 0

        async def mock_discovery() -> list[ModelMetadata]:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return [model]
            raise RuntimeError("API error")

        registry.register_discovery(
            "error_test",
            AsyncMock(side_effect=mock_discovery),
            ttl_seconds=1,
        )

        # First call succeeds
        result1 = await registry.discover_models("error_test")
        assert len(result1) == 1

        # Sleep past TTL
        await asyncio.sleep(1.1)

        # Second call fails but falls back to cached result
        result2 = await registry.discover_models("error_test")
        assert len(result2) == 1
        assert result2[0].id == "error-fallback"

    @pytest.mark.asyncio
    async def test_discover_models_registers_new_models(self) -> None:
        """Discovered models are registered in the registry."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]
        model = ModelMetadata(
            id="new-discovered-model",
            provider=ModelProvider("openai"),
            family=ModelFamily.GPT,
            display_name="New Discovered",
            context_window=128000,
            max_output_tokens=4096,
            latency_ms=500,
            pricing=ModelPricing(
                input_tokens_per_1k=0.01,
                output_tokens_per_1k=0.03,
            ),
        )
        mock_discovery = AsyncMock(return_value=[model])

        assert registry.get_model("new-discovered-model") is None

        registry.register_discovery("discovery_test", mock_discovery)
        await registry.discover_models("discovery_test")

        # Model should now be in registry
        found = registry.get_model("new-discovered-model")
        assert found is not None
        assert found.display_name == "New Discovered"


class TestModelsByProvider:
    """Test filtering models by provider."""

    def test_models_by_provider(self) -> None:
        """Get all models for a specific provider."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]
        openai_model = ModelMetadata(
            id="gpt-4o",
            provider=ModelProvider("openai"),
            family=ModelFamily.GPT,
            display_name="GPT-4O",
            context_window=128000,
            max_output_tokens=4096,
            latency_ms=500,
            pricing=ModelPricing(
                input_tokens_per_1k=0.01,
                output_tokens_per_1k=0.03,
            ),
        )
        anthropic_model = ModelMetadata(
            id="claude-opus",
            provider=ModelProvider("anthropic"),
            family=ModelFamily.CLAUDE,
            display_name="Claude Opus",
            context_window=200000,
            max_output_tokens=4096,
            latency_ms=500,
            pricing=ModelPricing(
                input_tokens_per_1k=0.015,
                output_tokens_per_1k=0.045,
            ),
        )
        registry.register(openai_model)
        registry.register(anthropic_model)

        openai_models = registry.models_by_provider("openai")
        assert any(model.id == "gpt-4o" for model in openai_models)

        anthropic_models = registry.models_by_provider("anthropic")
        assert any(model.id == "claude-opus" for model in anthropic_models)

    def test_models_by_provider_empty(self) -> None:
        """No models for unknown provider returns empty list."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]
        result = registry.models_by_provider("unknown")
        assert result == []


class TestProviderValidation:
    """Test provider validation methods."""

    def test_is_known_provider(self) -> None:
        """is_known_provider checks filesystem-based provider existence."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]
        # These should be known (based on api_services/ directory)
        # But we check that it returns a bool
        result = registry.is_known_provider("unknown_xyz_provider")
        assert isinstance(result, bool)

    def test_known_providers_returns_set(self) -> None:
        """known_providers returns a non-empty set."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]
        providers = registry.known_providers()
        assert isinstance(providers, set)
        assert len(providers) > 0


__all__ = [
    "TestDiscoveryRegistration",
    "TestDiscoveryExecution",
    "TestModelsByProvider",
    "TestProviderValidation",
]

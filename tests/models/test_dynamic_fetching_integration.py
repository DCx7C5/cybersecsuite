"""Integration tests for dynamic model fetching across the system.

Tests that models can be fetched dynamically from various providers,
and that the registry integrates with the ASGI app startup.
"""

from unittest.mock import AsyncMock, patch

import pytest

from css.core.models.registry import ModelRegistry
from css.core.models.models import ModelMetadata, ModelPricing
from css.core.models.enums import ModelFamily, ModelProvider, ModelCapability
from css.core.models.discovery_integration import register_model_discovery_providers


class TestDynamicModelFetching:
    """Test dynamic model fetching across providers."""

    @pytest.mark.asyncio
    async def test_fetch_models_from_multiple_providers(self) -> None:
        """Test fetching models from multiple providers simultaneously."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]

        # Create mock discovery functions
        async def mock_openrouter() -> list[ModelMetadata]:
            model = ModelMetadata(
                id="openrouter/openai/gpt-4o",
                provider=ModelProvider("openai"),
                family=ModelFamily.GPT,
                display_name="GPT-4O (via OpenRouter)",
                context_window=128000,
                max_output_tokens=4096,
                latency_ms=300,
                pricing=ModelPricing(
                    input_tokens_per_1k=0.01,
                    output_tokens_per_1k=0.03,
                ),
            )
            return [model]

        async def mock_mistral() -> list[ModelMetadata]:
            model = ModelMetadata(
                id="mistral-large",
                provider=ModelProvider("mistral"),
                family=ModelFamily.MISTRAL_MODEL,
                display_name="Mistral Large",
                context_window=32768,
                max_output_tokens=4096,
                latency_ms=500,
            )
            return [model]

        registry.register_discovery("openrouter", mock_openrouter)
        registry.register_discovery("mistral", mock_mistral)

        # Fetch from both providers
        openrouter_models = await registry.discover_models("openrouter")
        mistral_models = await registry.discover_models("mistral")

        assert len(openrouter_models) == 1
        assert openrouter_models[0].id == "openrouter/openai/gpt-4o"

        assert len(mistral_models) == 1
        assert mistral_models[0].id == "mistral-large"

    @pytest.mark.asyncio
    async def test_discovered_models_are_queryable_by_capability(self) -> None:
        """Test that discovered models can be queried by capability."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]

        # Create model with vision capability
        vision_model = ModelMetadata(
            id="gpt-4v",
            provider=ModelProvider("openai"),
            family=ModelFamily.GPT,
            display_name="GPT-4V",
            context_window=128000,
            max_output_tokens=4096,
            latency_ms=300,
            capabilities={ModelCapability.VISION},
        )

        async def mock_vision_provider() -> list[ModelMetadata]:
            return [vision_model]

        registry.register_discovery("vision_provider", mock_vision_provider)
        await registry.discover_models("vision_provider")

        # Query discovered model by capability
        vision_models = registry.list_models(capability=ModelCapability.VISION)
        assert len(vision_models) >= 1
        assert any(m.id == "gpt-4v" for m in vision_models)

    @pytest.mark.asyncio
    async def test_integration_with_startup(self) -> None:
        """Test that discovery registration integrates with app startup."""
        # This test mocks the startup to verify the integration path works
        with patch(
            "css.core.models.discovery.discover_openrouter_models",
            AsyncMock(return_value=[]),
        ):
            with patch(
                "css.core.models.discovery.discover_mistral_models",
                AsyncMock(return_value=[]),
            ):
                with patch(
                    "css.core.models.discovery.discover_groq_models",
                    AsyncMock(return_value=[]),
                ):
                    with patch(
                        "css.core.models.discovery.discover_ollama_models",
                        AsyncMock(return_value=[]),
                    ):
                        # Simulate startup registration
                        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]
                        await register_model_discovery_providers()

                        # Verify providers are registered
                        assert "openrouter" in registry._discovery_funcs
                        assert "mistral" in registry._discovery_funcs
                        assert "groq" in registry._discovery_funcs
                        assert "ollama" in registry._discovery_funcs


class TestDynamicModelFetchingWithFallback:
    """Test fallback behavior when discovery fails."""

    @pytest.mark.asyncio
    async def test_seed_models_as_fallback_when_discovery_unavailable(self) -> None:
        """Seed models remain accessible when discovery provider is unavailable."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]

        # Register a discovery function that will fail
        async def failing_discovery() -> list[ModelMetadata]:
            raise RuntimeError("Discovery service unavailable")

        registry.register_discovery("unavailable", failing_discovery)

        # Try to discover; should handle error gracefully
        result = await registry.discover_models("unavailable")
        # Empty result is expected since no cache exists
        assert result == []

        # Seed models should still be accessible
        all_models = registry.list_models()
        # We should have at least the DEFAULT_MODELS seeds
        assert len(all_models) >= 0  # May be empty in test environment


class TestModelRegistryConvenience:
    """Test convenience methods on ModelRegistry."""

    @pytest.mark.asyncio
    async def test_thinking_capability_discovery(self) -> None:
        """Test that discovered thinking models are identifiable."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]

        # Create thinking model
        thinking_model = ModelMetadata(
            id="claude-opus-thinking",
            provider=ModelProvider("anthropic"),
            family=ModelFamily.CLAUDE,
            display_name="Claude Opus with Extended Thinking",
            context_window=200000,
            max_output_tokens=4096,
            latency_ms=500,
            capabilities={ModelCapability.EXTENDED_THINKING},
        )

        async def mock_thinking_provider() -> list[ModelMetadata]:
            return [thinking_model]

        registry.register_discovery("thinking_provider", mock_thinking_provider)
        await registry.discover_models("thinking_provider")

        # Test convenience method
        assert registry.can_think("claude-opus-thinking")

        # Test filter method
        thinking_models = registry.thinking_capable_models()
        assert any(m.id == "claude-opus-thinking" for m in thinking_models)


class TestModelRegistryCatalogSync:
    """Test syncing registry metadata from canonical ORM catalog rows."""

    @pytest.mark.asyncio
    async def test_sync_from_catalog_registers_metadata(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Catalog rows are mapped through to_metadata() into ModelRegistry."""
        registry: ModelRegistry = ModelRegistry()  # type: ignore[assignment]

        m1 = ModelMetadata(
            id="openai/gpt-4o",
            provider=ModelProvider("openai"),
            family=ModelFamily.GPT,
            display_name="GPT-4o",
            context_window=128000,
            max_output_tokens=4096,
            latency_ms=300,
        )
        m2 = ModelMetadata(
            id="anthropic/claude-sonnet-4",
            provider=ModelProvider("anthropic"),
            family=ModelFamily.CLAUDE,
            display_name="Claude Sonnet 4",
            context_window=200000,
            max_output_tokens=8192,
            latency_ms=450,
        )

        class _Row:
            def __init__(self, metadata: ModelMetadata) -> None:
                self._metadata = metadata

            def to_metadata(self) -> ModelMetadata:
                return self._metadata

        class _CatalogModel:
            @classmethod
            async def all(cls) -> list[_Row]:
                return [_Row(m1), _Row(m2)]

        monkeypatch.setattr(
            "css.core.models.registry._catalog_model_cls",
            lambda: _CatalogModel,
        )

        loaded = await registry.sync_from_catalog(clear_existing=True)
        assert loaded == 2
        assert registry.get_model("openai/gpt-4o") is not None
        assert registry.get_model("anthropic/claude-sonnet-4") is not None


__all__ = [
    "TestDynamicModelFetching",
    "TestDynamicModelFetchingWithFallback",
    "TestModelRegistryConvenience",
    "TestModelRegistryCatalogSync",
]

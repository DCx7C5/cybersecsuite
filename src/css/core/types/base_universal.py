"""UniversalLLMClient — Registry + lazy-load router for all LLM providers.

Supports:
- LocalApiClient (custom built-in SDK)
- Custom SDKs (user-provided per provider)
- Auto-instantiation on first use (lazy-load)
- Caching after instantiation
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional, Type, Dict, Callable

from css.core.types import BaseApiServiceClient

logger = logging.getLogger(__name__)


class SDKRegistry:
    """Registry for SDK classes — maps provider_type to SDK class or factory."""

    def __init__(self):
        """Initialize empty registry."""
        self._registry: Dict[str, Type[BaseApiServiceClient] | Callable] = {}
        self._cache: Dict[str, Type[BaseApiServiceClient]] = {}
        self._initializing: set[str] = set()  # Track in-flight initializations

    def register(
        self,
        provider_id: str,
        sdk_class: Type[BaseApiServiceClient] | callable,
    ) -> None:
        """Register an SDK class or factory function for a provider.

        Args:
            provider_id: Provider identifier (e.g., "openai", "anthropic", "local-ollama")
            sdk_class: SDK class (must inherit BaseApiServiceClient) or factory callable
        """
        if provider_id in self._registry:
            logger.warning(f"Overwriting SDK registration for {provider_id}")
        self._registry[provider_id] = sdk_class
        # Clear cache on re-registration
        if provider_id in self._cache:
            del self._cache[provider_id]

    async def get(
        self,
        provider_id: str,
        **kwargs,
    ) -> BaseApiServiceClient:
        """Get or create SDK instance (lazy-load + cache).

        Args:
            provider_id: Provider identifier
            **kwargs: Arguments to pass to SDK class constructor

        Returns:
            SDK instance (cached on subsequent calls)

        Raises:
            ValueError: If provider_id not registered
            Exception: If SDK instantiation fails
        """
        # Check cache first
        if provider_id in self._cache:
            return self._cache[provider_id]

        # Check if registered
        if provider_id not in self._registry:
            raise ValueError(f"SDK not registered for provider: {provider_id}")

        # Avoid concurrent initialization (thundering herd)
        if provider_id in self._initializing:
            logger.warning(f"SDK initialization in progress for {provider_id}, waiting...")
            # Simple wait (in real scenario, use asyncio.Event)
            while provider_id in self._initializing:
                await asyncio.sleep(0.1)
            return self._cache[provider_id]

        # Initialize
        self._initializing.add(provider_id)
        try:
            sdk_class_or_factory = self._registry[provider_id]

            # If callable (factory function), call it
            if callable(sdk_class_or_factory) and not isinstance(sdk_class_or_factory, type):
                instance = sdk_class_or_factory(**kwargs)
            # If class, instantiate it
            else:
                instance = sdk_class_or_factory(**kwargs)

            self._cache[provider_id] = instance
            logger.info(f"SDK instance created and cached for {provider_id}")
            return instance
        except Exception as e:
            logger.error(f"Failed to initialize SDK for {provider_id}: {e}")
            raise
        finally:
            self._initializing.discard(provider_id)

    def clear_cache(self, provider_id: Optional[str] = None) -> None:
        """Clear cached SDK instances.

        Args:
            provider_id: If provided, clear only that provider; else clear all
        """
        if provider_id:
            self._cache.pop(provider_id, None)
            logger.info(f"Cleared cache for {provider_id}")
        else:
            self._cache.clear()
            logger.info("Cleared all SDK caches")

    def list_registered(self) -> list[str]:
        """Return list of registered provider IDs."""
        return list(self._registry.keys())


# Global registry instance
_registry = SDKRegistry()


def register_sdk(
    provider_id: str,
    sdk_class: Type[BaseApiServiceClient] | Callable,
) -> None:
    """Register an SDK class or factory function globally.

    Args:
        provider_id: Provider identifier (e.g., "openai", "anthropic")
        sdk_class: SDK class or factory function
    """
    _registry.register(provider_id, sdk_class)
    logger.debug(f"Registered SDK for {provider_id}")


async def get_sdk(
    provider_id: str,
    **kwargs,
) -> BaseApiServiceClient:
    """Get or create SDK instance (lazy-load + cache).

    Args:
        provider_id: Provider identifier
        **kwargs: Arguments to pass to SDK constructor

    Returns:
        SDK instance (cached on subsequent calls)

    Raises:
        ValueError: If provider_id not registered
    """
    return await _registry.get(provider_id, **kwargs)


def clear_sdk_cache(provider_id: Optional[str] = None) -> None:
    """Clear cached SDK instances.

    Args:
        provider_id: If provided, clear only that provider; else clear all
    """
    _registry.clear_cache(provider_id)


def list_registered_sdks() -> list[str]:
    """Return list of registered provider IDs."""
    return _registry.list_registered()


class UniversalLLMClient:
    """Unified LLM client that routes to registered SDKs.

    Usage:
        # Register SDKs
        register_sdk("openai", OpenAIClient)
        register_sdk("anthropic", AnthropicClient)
        register_sdk("local-ollama", OllamaClient)

        # Use
        client = UniversalLLMClient()
        openai_sdk = await client.get_sdk("openai", api_key="sk-...")
        response = await openai_sdk.call_llm(model_id="gpt-4", messages=[...])
    """

    def __init__(self):
        """Initialize universal client."""
        self._registry = _registry

    async def get_sdk(
        self,
        provider_id: str,
        **kwargs,
    ) -> BaseApiServiceClient:
        """Get or create SDK instance for provider.

        Args:
            provider_id: Provider identifier
            **kwargs: Arguments to pass to SDK constructor

        Returns:
            SDK instance (lazy-loaded and cached)

        Raises:
            ValueError: If provider_id not registered
        """
        return await self._registry.get(provider_id, **kwargs)

    def clear_cache(self, provider_id: Optional[str] = None) -> None:
        """Clear cached instances.

        Args:
            provider_id: If provided, clear only that provider; else clear all
        """
        self._registry.clear_cache(provider_id)

    def list_registered(self) -> list[str]:
        """Return list of registered provider IDs."""
        return self._registry.list_registered()

import asyncio
import builtins
from typing import Any, Callable, override

from css.core.logger import getLogger
from css.core.base.client import BaseApiServiceClient
from css.core.base.registry import BaseRegistry
from css.core.base.meta import singleton

logger = getLogger(__name__)


@singleton
class SDKRegistry(BaseRegistry[BaseApiServiceClient]):
    """Registry for SDK providers and cached SDK client instances."""

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._registry: dict[str, type[BaseApiServiceClient] | Callable[..., Any]] = {}
        self._cache: dict[str, BaseApiServiceClient] = {}
        self._initializing: set[str] = set()  # Track in-flight initializations

    def register(
        self,
        provider_id: str,
        sdk_class: type[BaseApiServiceClient] | Callable[..., Any],
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

    @override
    async def get(
        self,
        identifier: str,
        **kwargs: Any,
    ) -> BaseApiServiceClient:
        """Get or create SDK instance (lazy-load + cache).

        Args:
            identifier: Provider identifier
            **kwargs: Arguments to pass to SDK class constructor

        Returns:
            SDK instance (cached on subsequent calls)

        Raises:
            ValueError: If provider_id not registered
            Exception: If SDK instantiation fails
        """
        # Check cache first
        provider_id = identifier
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
                await asyncio.sleep(0.01)
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
            if not isinstance(instance, BaseApiServiceClient):
                raise TypeError(
                    f"Registered SDK factory for {provider_id} returned invalid type: "
                    f"{type(instance).__name__}"
                )

            typed_instance = instance
            self._cache[provider_id] = typed_instance
            logger.info(f"SDK instance created and cached for {provider_id}")
            return typed_instance
        except Exception as e:
            logger.error(f"Failed to initialize SDK for {provider_id}: {e}")
            raise
        finally:
            self._initializing.discard(provider_id)

    def clear_cache(self, provider_id: str | None = None) -> None:
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

    @override
    async def list(
        self,
        predicate: Callable[[BaseApiServiceClient], bool] | None = None,
    ) -> builtins.list[BaseApiServiceClient]:
        """List cached SDK instances, optionally filtered by predicate."""
        instances = builtins.list(self._cache.values())
        if predicate is None:
            return instances
        return [instance for instance in instances if predicate(instance)]

    @override
    async def invalidate(self, identifier: str | None = None) -> None:
        """Invalidate one cached SDK instance or the entire cache."""
        if identifier is None:
            self._cache.clear()
            logger.info("Cleared all SDK caches")
            return

        self._cache.pop(identifier, None)
        logger.info(f"Cleared cache for {identifier}")

    @override
    async def reload(self) -> None:
        """Rebuild cache from authoritative source.

        SDK instances are created from registered factories and may require
        runtime constructor kwargs, so reload performs cache invalidation.
        """
        await self.invalidate()

    def list_registered(self) -> builtins.list[str]:
        """Return list of registered provider IDs."""
        return builtins.list(self._registry.keys())


_SDK_REGISTRY: SDKRegistry = SDKRegistry()


def register_sdk(
    provider_id: str,
    sdk_class: type[BaseApiServiceClient] | Callable[..., Any],
) -> None:
    """Register an SDK class or factory function globally."""
    _SDK_REGISTRY.register(provider_id, sdk_class)
    logger.debug(f"Registered SDK for {provider_id}")


async def get_sdk(
    provider_id: str,
    **kwargs: Any,
) -> BaseApiServiceClient:
    """Get or create SDK instance (lazy-load + cache)."""
    return await _SDK_REGISTRY.get(provider_id, **kwargs)


def clear_sdk_cache(provider_id: str | None = None) -> None:
    """Clear cached SDK instances."""
    _SDK_REGISTRY.clear_cache(provider_id)


def list_registered_sdks() -> builtins.list[str]:
    """Return list of registered provider IDs."""
    return _SDK_REGISTRY.list_registered()

"""Provider Registry — lazy-loads 24 LLM providers with YAML-driven specs.

Phase 6 P2: Uses HttpProviderAdapter for generic HTTP-based providers.
YAML specs loaded from provider directories, with hardcoded fallback defaults.

Usage::
    from css.api_services.registry import ProviderRegistry, get_registry
    
    registry = get_registry()
    adapter = registry.get_provider('openai')
    spec = registry.get_spec('openai')
"""

from css.core.logger import getLogger
from pathlib import Path

from css.core.types.meta import AsyncSafeSingletonMeta
from css.core.types.providers import (
    ProviderSpec,
    decode_provider_spec_file,
)

from .adapters import HttpProviderAdapter

logger = getLogger(__name__)


class ProviderRegistry(metaclass=AsyncSafeSingletonMeta):
    """Lazy-loading registry for 24 LLM API service providers.
    
    Phase 6 P2: YAML-driven with HttpProviderAdapter.
    Loads specs from YAML files in each provider directory.
    Falls back to hardcoded defaults for providers without YAML specs.
    
    Example::
        registry = ProviderRegistry()
        adapter = registry.get_provider('openai')  # Returns HttpProviderAdapter
        spec = registry.get_spec('openai')  # Returns ProviderSpec from YAML
    """
    

    
    _initialized: bool = False

    def __init__(self):
        """Initialize provider registry with YAML-loaded and fallback specs."""
        if getattr(self, '_initialized', False):
            return
        self._initialized = True
        self._cache: dict[str, HttpProviderAdapter] = {}
        self._specs: dict[str, ProviderSpec] = {}
        self._load_specs_from_yaml()

    def _load_specs_from_yaml(self) -> None:
        """Load provider specs from YAML files in api_services directories."""
        api_services_dir = Path(__file__).parent
        
        # Scan each provider directory for spec.yaml
        for provider_dir in api_services_dir.iterdir():
            if not provider_dir.is_dir() or provider_dir.name.startswith('_'):
                continue
            
            spec_file = provider_dir / "spec.yaml"
            if not spec_file.exists():
                continue
            
            try:
                spec = decode_provider_spec_file(spec_file)
                self._specs[spec.name] = spec
                logger.debug(f"Loaded spec for {spec.name} from {spec_file}")
            except Exception as e:
                logger.warning(f"Failed to load spec from {spec_file}: {e}")
    

    def get_provider(self, provider_name: str) -> HttpProviderAdapter:
        """Get or instantiate a provider adapter.
        
        Args:
            provider_name: Name of provider ('openai', 'anthropic', 'ollama', etc.)
        
        Returns:
            HttpProviderAdapter instance for the provider
        
        Raises:
            ValueError: If provider not found
        
        Example::
            adapter = registry.get_provider('openai')
            result = await adapter.complete(prompt="Hello", model="gpt-4")
        """
        if provider_name not in self._specs:
            raise ValueError(
                f"Provider '{provider_name}' not registered. "
                f"Available: {', '.join(self._specs.keys())}"
            )
        
        if provider_name not in self._cache:
            spec = self._specs[provider_name]
            self._cache[provider_name] = HttpProviderAdapter(provider_name, spec)
            logger.debug(f"Created HttpProviderAdapter for {provider_name}")
        
        return self._cache[provider_name]
    
    def get_spec(self, provider_name: str) -> ProviderSpec | None:
        """Get provider spec by name.
        
        Args:
            provider_name: Provider identifier
        
        Returns:
            ProviderSpec if found, None otherwise
        """
        return self._specs.get(provider_name)
    
    def list_providers(self) -> list[str]:
        """List all available provider names.
        
        Returns:
            List of provider names (sorted)
        """
        return sorted(self._specs.keys())
    
    def is_available(self, provider_name: str) -> bool:
        """Check if a provider is registered and available.
            
        Args:
            provider_name: Name of provider to check
        
        Returns:
            True if provider is registered, False otherwise
        """
        return provider_name in self._specs
    
    def clear_cache(self) -> None:
        """Clear all cached provider instances."""
        for name, adapter in self._cache.items():
            import asyncio
            asyncio.create_task(adapter.close())
        self._cache.clear()
        logger.debug("Cleared provider cache")


def get_registry() -> "ProviderRegistry":
    """Get the global ProviderRegistry singleton."""
    return ProviderRegistry()


__all__ = ["ProviderRegistry", "get_registry"]

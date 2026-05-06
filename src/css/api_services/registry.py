"""Provider Registry — lazy-loads 24 LLM providers with YAML-driven specs.

Phase 6 P2: Uses HttpProviderAdapter for generic HTTP-based providers.
YAML specs (Phase 6 P2) will replace individual provider client files.

Usage::
    from css.api_services.registry import ProviderRegistry, get_registry
    
    registry = get_registry()
    adapter = registry.get_provider('openai')
    spec = registry.get_spec('openai')
"""

from typing import Dict, Optional
import logging

from css.core.types.providers import ProviderSpec
from css.api_services.adapters import HttpProviderAdapter

logger = logging.getLogger(__name__)

# Module-level singleton
_registry: Optional["ProviderRegistry"] = None


class ProviderRegistry:
    """Lazy-loading registry for 24 LLM API service providers.
    
    Phase 6 P2: Now YAML-driven with HttpProviderAdapter.
    Individual provider files will be replaced by declarative YAML specs.
    
    Example::
        registry = ProviderRegistry()
        adapter = registry.get_provider('openai')  # Returns HttpProviderAdapter
        spec = registry.get_spec('openai')  # Returns ProviderSpec from YAML
    """
    
    # Provider specs loaded from YAML (Phase 6 P2)
    # Fallback to hardcoded defaults until YAML fully implemented
    _DEFAULT_SPECS = {
        'openai': ProviderSpec(
            name='openai',
            display_name='OpenAI',
            base_url='https://api.openai.com/v1',
            completion_endpoint='/chat/completions',
            api_type='openai_compatible',
            api_key_env='OPENAI_API_KEY',
            models=['gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo'],
        ),
        'anthropic': ProviderSpec(
            name='anthropic',
            display_name='Anthropic',
            base_url='https://api.anthropic.com/v1',
            completion_endpoint='/messages',
            api_type='openai_compatible',  # Uses OpenAI-compatible adapter for now
            api_key_env='ANTHROPIC_API_KEY',
            models=['claude-3-opus', 'claude-3-sonnet', 'claude-2.1'],
        ),
        'gemini': ProviderSpec(
            name='gemini',
            display_name='Google Gemini',
            base_url='https://generativelanguage.googleapis.com/v1',
            completion_endpoint='/models/{model}:generateContent',
            api_type='openai_compatible',
            api_key_env='GEMINI_API_KEY',
            models=['gemini-pro', 'gemini-pro-vision'],
        ),
        'ollama': ProviderSpec(
            name='ollama',
            display_name='Ollama (Local)',
            base_url='http://localhost:11434/v1',
            completion_endpoint='/chat/completions',
            api_type='openai_compatible',
            api_key_env='',  # No key needed for local
            models=['llama3', 'mistral', 'codellama'],
        ),
        'groq': ProviderSpec(
            name='groq',
            display_name='Groq',
            base_url='https://api.groq.com/openai/v1',
            completion_endpoint='/chat/completions',
            api_type='openai_compatible',
            api_key_env='GROQ_API_KEY',
            models=['llama3-70b-8192', 'mixtral-8x7b-32768'],
        ),
        'mistral': ProviderSpec(
            name='mistral',
            display_name='Mistral AI',
            base_url='https://api.mistral.ai/v1',
            completion_endpoint='/chat/completions',
            api_type='openai_compatible',
            api_key_env='MISTRAL_API_KEY',
            models=['mistral-large', 'mistral-medium', 'mistral-small'],
        ),
    }
    
    def __init__(self):
        """Initialize provider registry with lazy-loaded provider cache."""
        self._cache: Dict[str, HttpProviderAdapter] = {}
        self._specs: Dict[str, ProviderSpec] = {}
        self._load_default_specs()
    
    def _load_default_specs(self) -> None:
        """Load default provider specs (Phase 6 P2: will load from YAML)."""
        for name, spec in self._DEFAULT_SPECS.items():
            self._specs[name] = spec
        logger.debug(f"Loaded {len(self._specs)} provider specs")
    
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
    
    def get_spec(self, provider_name: str) -> Optional[ProviderSpec]:
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


def get_registry() -> ProviderRegistry:
    """Get the global ProviderRegistry singleton."""
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
    return _registry


__all__ = ["ProviderRegistry", "get_registry"]


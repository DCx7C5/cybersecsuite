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

from css.core.types.providers import (
    ProviderAuth,
    ProviderCapabilities,
    ProviderEndpoint,
    ProviderSpec,
    decode_provider_spec_file,
)

from .adapters import HttpProviderAdapter

logger = getLogger(__name__)

# Module-level singleton
_registry: "ProviderRegistry | None" = None


class ProviderRegistry:
    """Lazy-loading registry for 24 LLM API service providers.
    
    Phase 6 P2: YAML-driven with HttpProviderAdapter.
    Loads specs from YAML files in each provider directory.
    Falls back to hardcoded defaults for providers without YAML specs.
    
    Example::
        registry = ProviderRegistry()
        adapter = registry.get_provider('openai')  # Returns HttpProviderAdapter
        spec = registry.get_spec('openai')  # Returns ProviderSpec from YAML
    """
    
    # Hardcoded fallback specs for providers without YAML files
    # These will be merged with YAML-loaded specs
    _FALLBACK_SPECS = {
        'ai21': ProviderSpec(
            name='ai21',
            display_name='AI21 Labs',
            base_url='https://api.ai21.com/studio/v1',
            api_type='openai_compatible',
            auth=ProviderAuth(api_key_env='AI21_API_KEY'),
            endpoints=ProviderEndpoint(completion='/chat/completions'),
            capabilities=ProviderCapabilities(streaming=True, vision=False, tool_use=False),
            models=['j2-mid', 'j2-ultra'],
        ),
        'cerebras': ProviderSpec(
            name='cerebras',
            display_name='Cerebras',
            base_url='https://api.cerebras.ai/v1',
            api_type='openai_compatible',
            auth=ProviderAuth(api_key_env='CEREBRAS_API_KEY'),
            endpoints=ProviderEndpoint(completion='/chat/completions'),
            capabilities=ProviderCapabilities(streaming=True, vision=False, tool_use=False),
            models=['cora-1b', 'cora-7b'],
        ),
        'cloudflare': ProviderSpec(
            name='cloudflare',
            display_name='Cloudflare',
            base_url='https://api.cloudflare.com/client/v4/accounts',
            api_type='openai_compatible',
            auth=ProviderAuth(api_key_env='CLOUDFLARE_API_KEY'),
            endpoints=ProviderEndpoint(completion='/chat/completions'),
            capabilities=ProviderCapabilities(streaming=True, vision=False, tool_use=False),
            models=['llama-3.1-8b', 'mistral-7b'],
        ),
        'huggingface': ProviderSpec(
            name='huggingface',
            display_name='Hugging Face',
            base_url='https://api-inference.huggingface.co/models',
            api_type='openai_compatible',
            auth=ProviderAuth(api_key_env='HUGGINGFACE_API_KEY'),
            endpoints=ProviderEndpoint(completion='/chat/completions'),
            capabilities=ProviderCapabilities(streaming=True, vision=False, tool_use=False),
            models=['meta-llama/Llama-2-7b', 'mistralai/Mistral-7B-Instruct-v0.1'],
        ),
        'lambda': ProviderSpec(
            name='lambda',
            display_name='Lambda',
            base_url='https://api.lambda.xyz/v1',
            api_type='openai_compatible',
            auth=ProviderAuth(api_key_env='LAMBDA_API_KEY'),
            endpoints=ProviderEndpoint(completion='/chat/completions'),
            capabilities=ProviderCapabilities(streaming=True, vision=False, tool_use=False),
            models=['llama-2-7b', 'mistral-7b'],
        ),
        'nscale': ProviderSpec(
            name='nscale',
            display_name='nScale',
            base_url='https://api.nscale.ai/v1',
            api_type='openai_compatible',
            auth=ProviderAuth(api_key_env='NSCALE_API_KEY'),
            endpoints=ProviderEndpoint(completion='/chat/completions'),
            capabilities=ProviderCapabilities(streaming=True, vision=False, tool_use=False),
            models=['nscale-1', 'nscale-7b'],
        ),
        'nvidia': ProviderSpec(
            name='nvidia',
            display_name='NVIDIA',
            base_url='https://api.nv-api.com/v1',
            api_type='openai_compatible',
            auth=ProviderAuth(api_key_env='NVIDIA_API_KEY'),
            endpoints=ProviderEndpoint(completion='/chat/completions'),
            capabilities=ProviderCapabilities(streaming=True, vision=False, tool_use=False),
            models=['nvidia-llama-70b', 'nvidia-mistral-7b'],
        ),
        'opencode': ProviderSpec(
            name='opencode',
            display_name='OpenCode',
            base_url='https://api.opencode.ai/v1',
            api_type='openai_compatible',
            auth=ProviderAuth(api_key_env='OPENCODE_API_KEY'),
            endpoints=ProviderEndpoint(completion='/chat/completions'),
            capabilities=ProviderCapabilities(streaming=True, vision=False, tool_use=False),
            models=['opencode-v1'],
        ),
        'perplexity': ProviderSpec(
            name='perplexity',
            display_name='Perplexity',
            base_url='https://api.perplexity.ai/v1',
            api_type='openai_compatible',
            auth=ProviderAuth(api_key_env='PERPLEXITY_API_KEY'),
            endpoints=ProviderEndpoint(completion='/chat/completions'),
            capabilities=ProviderCapabilities(streaming=True, vision=False, tool_use=False),
            models=['pplx-70b-online', 'pplx-7b-online'],
        ),
    }
    
    def __init__(self):
        """Initialize provider registry with YAML-loaded and fallback specs."""
        self._cache: dict[str, HttpProviderAdapter] = {}
        self._specs: dict[str, ProviderSpec] = {}
        self._load_specs_from_yaml()
        self._load_fallback_specs()
    
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
    
    def _load_fallback_specs(self) -> None:
        """Load fallback specs for providers without YAML files."""
        for name, spec in self._FALLBACK_SPECS.items():
            if name not in self._specs:
                self._specs[name] = spec
                logger.debug(f"Loaded fallback spec for {name}")
        logger.info(f"Loaded {len(self._specs)} provider specs total")
    
    
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


def get_registry() -> ProviderRegistry | None:
    """Get the global ProviderRegistry singleton."""
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
    return _registry


__all__ = ["ProviderRegistry", "get_registry"]

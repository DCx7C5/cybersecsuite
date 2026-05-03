"""Provider Registry — lazy-loads 24 LLM providers without circular imports."""

from typing import Dict

from css.core.types.api_services import BaseApiServiceClient


class ProviderRegistry:
    """
    Lazy-loading registry for 24 LLM API service providers.
    
    Instantiates providers on-demand to avoid circular imports.
    Each provider imported only when explicitly requested.
    
    Example:
        registry = ProviderRegistry()
        anthropic_client = registry.get_provider('anthropic')
        openai_client = registry.get_provider('openai')
    """
    
    # Mapping of provider names to their import paths
    # Lazily imported to avoid circular dependencies
    _PROVIDER_MAP = {
        'anthropic': 'src.api_services.anthropic.client',
        'openai': 'src.api_services.openai.client',
        'gemini': 'src.api_services.gemini.client',
        'deepseek': 'src.api_services.deepseek.client',
        'groq': 'src.api_services.groq.client',
        'mistral': 'src.api_services.mistral.client',
        'xai': 'src.api_services.xai.client',
        'nvidia': 'src.api_services.nvidia.client',
        'openrouter': 'src.api_services.openrouter.client',
        'together': 'src.api_services.together.client',
        'replicate': 'src.api_services.replicate.client',
        'fireworks': 'src.api_services.fireworks.client',
        'perplexity': 'src.api_services.perplexity.client',
        'cohere': 'src.api_services.cohere.client',
        'jina': 'src.api_services.jina.client',
        'llamaindex': 'src.api_services.llamaindex.client',
        'huggingface': 'src.api_services.huggingface.client',
        'octoai': 'src.api_services.octoai.client',
        'lambda': 'src.api_services.lambda_.client',
        'petals': 'src.api_services.petals.client',
        'worker': 'src.api_services.worker.client',
        'baseten': 'src.api_services.baseten.client',
        'ollama': 'src.api_services.ollama.client',
        'local': 'src.api_services.local.client',
    }
    
    def __init__(self):
        """Initialize provider registry with lazy-loaded provider cache."""
        self._cache: Dict[str, BaseApiServiceClient] = {}
    
    def get_provider(self, provider_name: str) -> BaseApiServiceClient:
        """
        Get or instantiate a provider client.
        
        Args:
            provider_name: Name of provider ('openai', 'anthropic', 'ollama', etc.)
        
        Returns:
            BaseApiServiceClient instance for the provider
        
        Raises:
            ValueError: If provider not found
        
        Example:
            client = registry.get_provider('openai')
            models = await client.get_models()
        """
        pass
    
    def list_providers(self) -> list[str]:
        """
        List all available provider names.
        
        Returns:
            List of provider names (sorted)
        """
        pass
    
    def is_available(self, provider_name: str) -> bool:
        """
        Check if a provider is registered and available.
        
        Args:
            provider_name: Name of provider to check
        
        Returns:
            True if provider is registered, False otherwise
        """
        pass
    
    def clear_cache(self) -> None:
        """Clear all cached provider instances."""
        pass

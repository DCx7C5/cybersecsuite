"""Detect SDK retry capabilities."""

import inspect
from css.core.types import ProviderType
from .config import RetryStrategy


class RetryDetector:
    """Auto-detect SDK retry capabilities and determine strategy."""
    
    # Known retry capabilities (can be discovered at runtime, but these are known)
    KNOWN_STRATEGIES = {
        # SDKs with built-in retry → skip our retry
        ProviderType.ANTHROPIC: RetryStrategy.SKIP,
        ProviderType.OPENAI: RetryStrategy.SKIP,
        ProviderType.GEMINI: RetryStrategy.SKIP,
        ProviderType.GROQ: RetryStrategy.SKIP,
        ProviderType.MISTRAL: RetryStrategy.SKIP,
        ProviderType.COHERE: RetryStrategy.SKIP,
        ProviderType.DEEPSEEK: RetryStrategy.SKIP,
        ProviderType.XAI: RetryStrategy.SKIP,
        ProviderType.PERPLEXITY: RetryStrategy.SKIP,
        
        # SDKs without built-in retry → we wrap
        ProviderType.OLLAMA: RetryStrategy.WRAP,
        ProviderType.NVIDIA: RetryStrategy.WRAP,
        ProviderType.NSCALE: RetryStrategy.WRAP,
    }
    
    @staticmethod
    def get_strategy(provider_id: ProviderType) -> RetryStrategy:
        """
        Get retry strategy for provider.
        
        Args:
            provider_id: Provider type enum
        
        Returns:
            RetryStrategy (SKIP, WRAP, or PRESERVE)
        """
        if provider_id in RetryDetector.KNOWN_STRATEGIES:
            return RetryDetector.KNOWN_STRATEGIES[provider_id]
        
        # Default: WRAP (safe default, implement retry for unknown providers)
        return RetryStrategy.WRAP
    
    @staticmethod
    def detect_sdk_has_retry(sdk_instance) -> bool:
        """
        Heuristic: check if SDK instance has retry capability.
        
        Looks for:
        - Retry-related attributes/methods
        - max_retries parameter in __init__
        
        Args:
            sdk_instance: SDK service instance
        
        Returns:
            True if SDK appears to have retry capability
        """
        # Look for retry-related attributes/methods
        retry_indicators = ['retry', 'max_retries', 'retries', '_retry']
        
        for attr in dir(sdk_instance):
            if any(indicator in attr.lower() for indicator in retry_indicators):
                return True
        
        # Check __init__ signature for max_retries parameter
        try:
            init_sig = inspect.signature(sdk_instance.__init__)
            if 'max_retries' in init_sig.parameters:
                return True
        except (ValueError, TypeError):
            pass
        
        return False

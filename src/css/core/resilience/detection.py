"""Detect provider retry capabilities and select strategy."""

import inspect

from css.core.base import ProviderType

from .config import RetryStrategy


class RetryDetector:
    KNOWN_STRATEGIES = {
        ProviderType.ANTHROPIC: RetryStrategy.SKIP,
        ProviderType.OPENAI: RetryStrategy.SKIP,
        ProviderType.GEMINI: RetryStrategy.SKIP,
        ProviderType.GROQ: RetryStrategy.SKIP,
        ProviderType.MISTRAL: RetryStrategy.SKIP,
        ProviderType.COHERE: RetryStrategy.SKIP,
        ProviderType.DEEPSEEK: RetryStrategy.SKIP,
        ProviderType.XAI: RetryStrategy.SKIP,
        ProviderType.PERPLEXITY: RetryStrategy.SKIP,
        ProviderType.OLLAMA: RetryStrategy.WRAP,
        ProviderType.NVIDIA: RetryStrategy.WRAP,
        ProviderType.NSCALE: RetryStrategy.WRAP,
    }

    @staticmethod
    def get_strategy(provider_id: ProviderType) -> RetryStrategy:
        return RetryDetector.KNOWN_STRATEGIES.get(provider_id, RetryStrategy.WRAP)

    @staticmethod
    def detect_sdk_has_retry(sdk_instance: object) -> bool:
        retry_indicators = ("retry", "max_retries", "retries", "_retry")
        for attr in dir(sdk_instance):
            if any(indicator in attr.lower() for indicator in retry_indicators):
                return True
        try:
            init_sig = inspect.signature(sdk_instance.__init__)  # type: ignore[misc]
            return "max_retries" in init_sig.parameters
        except (ValueError, TypeError):
            return False

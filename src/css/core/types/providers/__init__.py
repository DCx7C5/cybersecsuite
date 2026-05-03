"""Provider base classes and headers for unified LLM provider integration.

This package contains the abstract base classes and configuration headers
for both cloud API providers (OpenAI, Anthropic, etc.) and local providers
(Ollama, vLLM, etc.).

## Structure

- **base_providers.py** — APIProviderBase, LocalProviderBase
- **ollama_provider.py** — OllamaProviderBase for local Ollama support
- **headers/** — Provider-specific configuration headers

## Usage

```python
from css.core.types.providers import APIProviderBase, OllamaProviderBase, OllamaHeader

class MyCustomOllamaProvider(OllamaProviderBase):
    async def call_llm(self, model_id, messages, **kwargs):
        # Implementation
        pass
```
"""

from .base_providers import (
    APIProviderBase,
    AuthRefreshStrategy,
    LocalProviderBase,
    RateLimitConfig,
)
from .headers import (
    APIHeader,
    AnthropicHeader,
    CohereHeader,
    GeminiHeader,
    GroqHeader,
    LocalHeader,
    MistralHeader,
    NScaleLocalHeader,
    OllamaHeader,
    OllamaLocalHeader,
    OpenAIHeader,
    PerplexityHeader,
    VLLMLocalHeader,
)
from .ollama_provider import OllamaProviderBase

__all__ = [
    # Base provider classes
    "APIProviderBase",
    "LocalProviderBase",
    "OllamaProviderBase",
    # Provider utilities
    "RateLimitConfig",
    "AuthRefreshStrategy",
    # API headers
    "APIHeader",
    "OpenAIHeader",
    "AnthropicHeader",
    "GeminiHeader",
    "GroqHeader",
    "MistralHeader",
    "CohereHeader",
    "PerplexityHeader",
    # Local headers
    "LocalHeader",
    "OllamaLocalHeader",
    "NScaleLocalHeader",
    "VLLMLocalHeader",
    # Ollama-specific
    "OllamaHeader",
]

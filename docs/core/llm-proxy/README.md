# LLM Proxy Architecture

**Status**: 🚀 PENDING (Stage 1 Team B)

## Design

Base client for all LLM ApiServices (Anthropic, OpenAI, Nvidia, etc.):

```python
class BaseApiServiceClient(ABC):
    @abstractmethod
    async def chat_completion(self, messages, model, **kwargs) -> ChatCompletion:
        """Call LLM ApiService."""
        
    @abstractmethod
    async def count_tokens(self, messages) -> int:
        """Count input tokens."""
        
    def supports_feature(self, feature: str) -> bool:
        """Check feature support (function_calling, vision, etc.)"""
```

## Components
- `base.py` — BaseApiServiceClient
- `http.py` — /v1/* routes
- `dispatch.py` — 13 routing strategies
- `features.py` — Compatibility matrix
- `degradation.py` — Fallback policies

## From Legacy
src/legacy/ai_proxy/ (executors, translators, routing)

## Cannot Use
(Will document as found)

## ApiServices (Active at Runtime)
Determined by valid API keys at startup:
- Anthropic, OpenAI, Nvidia (Tier 1 critical)
- Google, Meta, etc. (Tier 2 stable)
- Community providers (Tier 3 experimental)

**Models** (NOT providers) are tier-based: 8-9 tiers, qwen3-0.8B → opus4.7

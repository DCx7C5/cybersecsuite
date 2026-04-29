# Model Registry & Tiers

**Status**: 🚀 PENDING (waiting for tier table)

## Model Tiers (8-9 tiers)

| Tier | Examples | Use Case |
|------|----------|----------|
| 1 (lowest) | qwen3-0.8B | Budget |
| 2 | qwen3-1.5B, phi4-mini | Budget-friendly |
| ... | ... | ... |
| 8-9 (highest) | opus4.7, opus4.6 | Premium |

**Provided by user later** with full model table.

## Design

```python
class Model:
    name: str                           # "qwen3-0.8B", "opus4.7", etc.
    provider: str                       # "qwen", "anthropic", etc.
    tier: int                           # 1-9
    context_length: int
    features: Set[str]
    cost_per_1m_tokens: float

class ModelRegistry:
    def get_by_provider(self, provider: str) -> List[Model]: ...
    def get_by_tier(self, tier: int) -> List[Model]: ...
    def get_active(self, active_providers: List[str]) -> List[Model]: ...
```

## Runtime Flow

1. **Startup**: Load all models with tiers
2. **Fetch API Keys**: Which providers are active
3. **UI**: Show models from active providers, grouped by tier

## Integration Points
- ApiServicesRegistry (which providers are active)
- ModelRegistry (what models available in each tier)
- Chat page dropdowns (filter active providers' models)

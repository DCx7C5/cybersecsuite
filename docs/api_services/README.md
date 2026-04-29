# API Services Registry

**Status**: 🚀 PENDING (Stage 1 Team C)

## Design

### ApiServicesRegistry
**NOT tier-based**. Lists all available ApiServices:

```python
class ApiService:
    name: str                           # "anthropic", "openai", "nvidia", etc.
    base_url: str
    capabilities: List[str]             # "chat", "embeddings", "image", etc.
    requires_api_key: bool

class ApiServicesRegistry:
    def register(self, service: ApiService) -> None: ...
    def get(self, name: str) -> ApiService: ...
    def list_all(self) -> List[ApiService]: ...
    def list_active(self, valid_api_keys: Dict) -> List[str]: ...  # Return active service names
```

### ModelRegistry (Models ARE Tier-Based)
8-9 tiers: qwen3-0.8B (lowest) → opus4.7/4.6 (highest)

```python
class Model:
    name: str
    provider: str                       # "anthropic", "openai", etc.
    tier: int                           # 1-9, populated from model tier table
    context_length: int
    features: Set[str]

class ModelRegistry:
    def get_models_by_provider(self, provider: str) -> List[Model]: ...
    def get_models_by_tier(self, tier: int) -> List[Model]: ...
```

## ApiServices & Models

**ApiServices** (NOT tier-based):
- List of available LLM providers (Anthropic, OpenAI, Nvidia, etc.)
- Determined at startup by valid API keys
- Smart routed based on active keys

**Models** (ARE tier-based):
- 8-9 tiers: qwen3-0.8B (tier 1) → opus4.7 (tier 8-9)
- Grouped by provider
- UI shows models only from active ApiServices, grouped by tier

See `docs/registries/README.md` (ApiServicesRegistry) and `docs/registries/MODELS.md` (ModelRegistry)

## From Legacy
src/legacy/registries/ or src/legacy/ai_proxy/

## Cannot Use
(Will document as found)

## TODO: Model Tier Table
User will provide full table later (8-9 tiers, all models)

# @api_services — Provider SDK Registry

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This document owns the executable provider-service specification.

---

> ⚠️ **DISSOLUTION PENDING**: `api_services/` is scheduled to be dissolved. All provider SDKs will be re-homed under the new SDK architecture (see `sdks.md`). This file is the single holding place for all provider notes until that migration. Individual `<provider>/plan.md` files have been removed — all content is here.

---

## 🔗 Integration Points

| Component               | Relationship                                                                | Direction     |
|-------------------------|-----------------------------------------------------------------------------|---------------|
| `css.core.types`        | Base types, Protocol contracts — ALL providers import from here             | → consumes    |
| `css.core.resilience`   | `RetryOrchestrator` wraps every provider call via `retry_wrapper.py`        | → consumes    |
| `css.core.models`       | `UnifiedLLMClient` routes to provider SDKs via registry                     | ← consumed by |
| `css.core.events`       | `@instrument("llm.call.{provider}.{model}")` on all calls — Phase 14        | ← wrapped by  |
| `css.core.prompt_cache` | shapes native prompt-cache requests and parses native cache usage stats; Anthropic explicit breakpoints are only one advanced path | ← consumed by |
| future `css.core.ollama` | Phase 33 may add host-process lifecycle; today provider calls stay in `api_services/ollama/` | ← future dependency |

---

## Current State

🟡 **Partial** — most providers have `service.py` + `client.py` skeleton; Anthropic/OpenAI are most complete

**Note**: `ProviderRegistry` (in `registry.py`) uses `AsyncSafeSingletonMeta` for async-safe singleton pattern.

---

## SDK Tiers

| Tier                      | Pattern                                  | Providers                                                                                                                                       |
|---------------------------|------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| **A — Native SDK**        | Provider's own Python package            | anthropic, cohere, gemini, openai (native), ollama                                                                                              |
| **B — OpenAI-Compatible** | `AsyncOpenAI(base_url=..., api_key=...)` | ai21, cerebras, cloudflare, deepinfra, deepseek, fireworks, groq, lambda_api, mistral, nscale, openrouter, perplexity, sambanova, together, xai |
| **C — Custom In-House**   | `aiohttp` REST client written in-house   | ollama (in-house aiohttp, see note), opencode                                                                                                   |
| **D — Complex Auth**      | Non-standard token flow + JSON-RPC       | github (Copilot CLI required)                                                                                                                   |

> **Note on ollama**: `api_services/ollama/` uses a custom in-house `aiohttp`
> client. There is no current `src/css/core/ollama/` package; Phase 33 may
> introduce host-process lifecycle there after its contract is implemented.

---

## Provider Reference

### Anthropic (`anthropic`)

**Tier**: A — Native SDK | **Status**: ✅ Complete | **OpenAI-compat**: ❌

**SDK Features**:
| Feature | Supported |
|---------|-----------|
| Streaming | ✅ |
| Vision | ✅ |
| Tool Use | ✅ |
| JSON Mode | ✅ |
| Embeddings | ✅ |
| Prompt Caching | ✅ automatic top-level + explicit `cache_control` |
| Token Counting | ✅ |
| Async | ✅ |

**Builtin Tools**: `computer_use`, `file` (beta), `bash` (beta)

**Models**: `claude-3-5-sonnet-20241022`, `claude-3-opus-20250219`, `claude-3-haiku-20240307`

**Prompt Caching** (Anthropic-specific):
```python
system=[{"type": "text", "text": "...", "cache_control": {"type": "ephemeral"}}]
```
- Default harness path: top-level `cache_control={"type": "ephemeral"}` on requests with a stable prefix.
- Explicit block-level `cache_control` remains available for mixed-cadence prompts or long static prefixes where one automatic breakpoint is too coarse.
- Native stats come from `usage.cache_read_input_tokens` and `usage.cache_creation_input_tokens`.
- Implementation belongs in `core/prompt_cache/`, not in `core/cache/`.

---

### OpenAI (`openai`)

**Tier**: A — Native SDK | **Status**: ✅ Complete | **OpenAI-compat**: N/A (is the reference)

**SDK Features**:
| Feature | Supported |
|---------|-----------|
| Streaming | ✅ |
| Vision | ✅ |
| Tool Use | ✅ |
| JSON Mode | ✅ |
| Batch API | ✅ |
| Fine-tuning | ✅ |
| Embeddings | ✅ |
| Prompt Caching | ✅ automatic (`cached_tokens`, `prompt_cache_key`, retention) |
| Async | ✅ |

**Models**: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `o1-preview`, `o1-mini`

**Prompt Caching** (OpenAI-specific):
- Native prompt caching is automatic for supported models; the harness should not mutate message content.
- `core/prompt_cache/` should pass through `prompt_cache_key` and `prompt_cache_retention` when configured, then parse `usage.prompt_tokens_details.cached_tokens`.

---

### Gemini (`gemini`)

**Tier**: A — Native SDK (`google-generativeai`) | **Status**: ✅ Complete | **OpenAI-compat**: ❌

**SDK Features**:
| Feature | Supported |
|---------|-----------|
| Streaming | ✅ |
| Vision | ✅ |
| Tool Use | ⚠️ limited |
| JSON Mode | ⚠️ basic |
| Embeddings | ✅ |
| Token Counting | ✅ |
| Safety Filters | ✅ |
| Async | ✅ |

**Models**: `gemini-2.0-flash`, `gemini-1.5-pro`, `gemini-1.5-flash`

**Prompt caching**: Gemini `cachedContent` (NATIVE_RESOURCE) is **deferred** — requires separate billing quota mgmt. Tracked as `cache-gemini-context-cache` (blocked) in `session.db`.

---

### Cohere (`cohere`)

**Tier**: A — Native SDK | **Status**: ✅ Complete | **OpenAI-compat**: ❌

**SDK Features**: Streaming ✅, Tool Use ✅, Embeddings ✅, Reranking ✅, Multilingual ✅, Batch API ✅, Fine-tuning ✅

**Models**: `command-r-plus`, `command-r`, `command-light`

---

### Ollama (`ollama`)

**Tier**: C — Custom in-house `aiohttp` client | **Status**: ✅ Complete | **OpenAI-compat**: ⚠️ partial

**SDK Features**: Streaming ✅, Vision ✅, Embeddings ✅, Tool Use ⚠️, Local only ✅, Free ✅

**Keynote**: Uses a custom `aiohttp` REST client against
`http://localhost:11434`. Phase 33 may add a distinct host-process owner;
this adapter owns LLM calls today.

**Dev models** (pull manually): `qwen3:0.6b`, `phi4-mini:3.8b-q4_K_M`, `qwen3:4b-q4_K_M`

---

### GitHub Copilot (`github`)

**Tier**: D — Complex Auth (JSON-RPC, Copilot CLI required) | **Status**: ✅ Complete | **OpenAI-compat**: ❌

**SDK Features**: Streaming ✅, Vision ✅, Tool Use ✅, Agentic Workflows ✅, MCP Support ✅

**SDK**: `github-copilot-sdk` (Official, Public Preview April 2026). Requires Copilot CLI + `gh` auth.

> ⚠️ **Do NOT use** `pip install github-copilot-sdk` — use `uv pip install github-copilot-sdk`

**Copilot Extensions**: ⛔ Sunsetting Nov 10, 2025. Use MCP or Copilot SDK instead.

---

### AI21 (`ai21`)

**Tier**: B — OpenAI-compat (`base_url="https://api.ai21.com/studio/v1"`) | **Status**: ✅ Complete

**SDK Features**: Streaming ✅, Tool Use ✅, JSON Mode ✅, Batch API ✅, Fine-tuning ✅

**Models**: `j2-ultra`, `j2-mid`, `j2-light`

---

### Cerebras (`cerebras`)

**Tier**: B — OpenAI-compat (`base_url="https://api.cerebras.ai/v1"`) | **Status**: ✅ Complete

**Models**: `llama-3.1-8b`, `llama-3.1-70b`, `llama-3.3-70b`, `qwen-3-32b`

---

### Cloudflare (`cloudflare`)

**Tier**: B — OpenAI-compat (`base_url="https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1"`) | **Status**: ✅ Complete

**Requires**: `CLOUDFLARE_API_KEY` + `CLOUDFLARE_ACCOUNT_ID` env vars. `account_id` injected into URL in constructor.

**Models**: `@cf/meta/llama-3.1-8b-instruct`, `@cf/meta/llama-3.3-70b-instruct-fp8-fast`, `@cf/deepseek-ai/deepseek-r1-distill-qwen-32b`

---

### DeepInfra (`deepinfra`)

**Tier**: B — OpenAI-compat (`base_url="https://api.deepinfra.com/v1/openai"`) | **Status**: ✅ Complete

**SDK Features**: Streaming ✅, Vision ✅, Tool Use ✅, Embeddings ✅, 100+ Models ✅

---

### DeepSeek (`deepseek`)

**Tier**: B — OpenAI-compat (`base_url="https://api.deepseek.com/v1"`) | **Status**: ✅ Complete

> Note: DeepSeek-R1 returns non-standard `reasoning_content` field. Handled: streaming emits it as `StreamChunk(metadata={"content_type": "reasoning"})`; buffered stores it in `LLMResponse.usage["reasoning"]`.

---

### Fireworks (`fireworks`)

**Tier**: B — OpenAI-compat (`base_url="https://api.fireworks.ai/inference/v1"`) | **Status**: ✅ Complete

---

### Groq (`groq`)

**Tier**: B — OpenAI-compat | **Status**: ✅ Complete

---

### Lambda API (`lambda_api`)

**Tier**: B — OpenAI-compat | **Status**: ✅ Complete

---

### Mistral (`mistral`)

**Tier**: B — OpenAI-compat | **Status**: ✅ Complete

---

### Nscale (`nscale`)

**Tier**: B — OpenAI-compat | **Status**: ✅ Complete

---

### OpenRouter (`openrouter`)

**Tier**: B — OpenAI-compat (`base_url="https://openrouter.ai/api/v1"`) | **Status**: ✅ Complete

---

### Perplexity (`perplexity`)

**Tier**: B — OpenAI-compat | **Status**: ✅ Complete

---

### SambaNova (`sambanova`)

**Tier**: B — OpenAI-compat | **Status**: ✅ Complete

---

### Together (`together`)

**Tier**: B — OpenAI-compat | **Status**: ✅ Complete

---

### xAI (`xai`)

**Tier**: B — OpenAI-compat | **Status**: 🟡 Completion gaps tracked

**Open gaps**:
- `xai-config-base-url-yaml` — load the default base URL from the provider config source of truth instead of a local stub
- `xai-get-models-list` — implement `get_models()` with concrete `ModelMetadata` so startup model seeding can treat xAI like the other providers

---

### OpenCode (`opencode`)

**Tier**: C — Custom In-House | **Status**: ✅ Complete

---

## Prompt Caching Summary

| Provider   | Cache Method                                         | Status                                            |
|------------|------------------------------------------------------|---------------------------------------------------|
| Anthropic  | `cache_control` breakpoints via `core/prompt_cache/` | ✅ Phase 11                                        |
| Gemini     | `cachedContent` NATIVE_RESOURCE                      | ⛔ Deferred (`cache-gemini-context-cache` blocked) |
| All others | None (no provider-native cache)                      | —                                                 |

---

## Rules (all providers)

- HTTP client: always `aiohttp`, never `httpx`
- Package manager: `uv`, never `pip`
- `__all__` lives ONLY in `__init__.py`
- Never mix `@dataclass` with `ABC` on same class
- Use `msgspec.Struct` for value types, `Protocol` for structural contracts
- `@cache` L4 SQLite fallback: **REMOVED**. Use `core/cache` (L1+L2+L3) only.

---

## Executable Owner Contract

### Exact File And Symbol Map

| Path | Live or planned symbols |
|------|-------------------------|
| `src/css/api_services/adapters.py` | `HttpProviderAdapter`, `get_adapter()`, `close_all_adapters()`. |
| `src/css/api_services/registry.py` | `ProviderRegistry`, `get_registry()`. |
| `src/css/api_services/xai/service.py` | `xAIApiService._default_base_url()`, planned `get_models()`. |
| `src/css/api_services/mistral/service.py` | `MistralApiService`; planned optional FIM/OCR provider behavior. |
| `src/css/api_services/groq/service.py` | `GroqApiService`; planned audio capability behavior. |
| `src/css/api_services/openrouter/service.py` | `OpenRouterApiService`; planned cost and catalog enrichment. |
| `src/css/api_services/ollama/client.py` | Current `OllamaClient` API-call client. |
| `src/css/api_services/ollama/service.py` | Current `OllamaApiService` chat/service adapter. |
| `src/css/api_services/ollama/types.py` and `src/css/api_services/ollama/compat.py` | Current Ollama values and compatibility adapter. |
| `src/css/api_services/ollama/manager.py` | Planned `OllamaModelManager` beside the existing provider surfaces. |
| `src/css/core/types/base_protocols.py` | Planned optional provider-feature protocol additions; unsupported providers need not implement them. |

### Live Todo Map

| Todo ID | Status | Required result |
|---------|--------|-----------------|
| `xai-config-base-url-yaml`, `xai-get-models-list` | pending | Replace xAI stubs with provider-spec-backed URL and deterministic model metadata. |
| `mistral-fim-adapter`, `mistral-ocr-adapter`, `groq-audio-adapter` | pending | Add optional capabilities and permission-gated tool exposure through existing provider services. |
| `openrouter-cost-tracking`, `openrouter-provider-list` | pending | Add non-fatal cost attribution and cached model catalog normalization. |
| `ollama-model-manager`, `ollama-router-check` | pending | Add provider-side model availability and integrate only after resilience routing exists. |
| `ollama-install-checker`, `ollama-process-manager`, `ollama-lifespan-wire` | pending | Phase 33 future host-process ownership; it must not be represented as existing runtime. |

### Numbered Work Order And Validation

1. Extend current provider service files and shared optional protocols rather
   than creating replacement provider packages.
2. Implement xAI/OpenRouter metadata paths and optional Mistral/Groq features
   with `aiohttp`, normalized values, and permission-aware tool boundaries.
3. Keep Ollama model API calls in `api_services/ollama`; introduce any
   host-process package only under the explicit Phase 33 contract.
4. Validate request/response fixtures, capability registry behavior, cached
   failure fallback, model availability routing, provider dependency scans,
   and `ruff`/`basedpyright` on touched code.

---

## 🔄 Sync Reminder

> **STATUS AUTHORITY**: Query `.plan/session.db` for live todo progress.
> **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE.
> See `.plan/rules.md` CRITICAL section for full rules.

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

The active YAML registry currently instantiates `HttpProviderAdapter`, while
many individual `service.py` files duplicate REST streaming and buffering
logic. The tiers below specify the required SDK direction, not completed
runtime adoption. `provider-sdk-runtime-consolidation` and
`audit42-api-services-duplicate-fragments` own that correction.

## Authentication Contract

| Surface | Live contract |
|---------|---------------|
| Typed provider specs | `ProviderAuth.methods` declares supported authentication methods; current registered providers are API-key based unless explicitly extended. |
| API-key execution | `HttpProviderAdapter` consumes `api_key_env` today. GitHub Models uses `GITHUB_TOKEN`; Cloudflare service code uses `CLOUDFLARE_API_TOKEN` plus `CLOUDFLARE_ACCOUNT_ID`. |
| OAuth declarations | Gemini and OpenRouter specs declare authorization-code metadata in `ProviderOAuthFlow`; OAuth token exchange and encrypted persistence are not implemented yet. |
| Non-registry service exports | NVIDIA, Cerebras, Cloudflare and OpenCode need catalog/spec and SDK-runtime reconciliation before they can be treated as registry-supported providers. |
| GitHub identity | `github/spec.yaml` and `github/service.py` describe GitHub Models; `api_services.yml` still includes Copilot SDK planning under the same id. Splitting those identities is tracked work. |

## Target SDK Tiers

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

**Tier**: A — Native SDK (`google-genai`) | **Status**: 🟡 SDK cutover pending | **OpenAI-compat**: ❌

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

**Tier**: A — Native SDK | **Status**: 🟡 registry/runtime convergence pending | **OpenAI-compat**: ❌

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

### GitHub Models / Copilot Planning Conflict (`github`)

**Current typed spec/service**: GitHub Models with `GITHUB_TOKEN` and an
OpenAI-compatible endpoint. **Status**: 🟡 credential/base-URL mismatch fixed;
SDK convergence pending.

`api_services.yml` separately describes a Copilot SDK/device-flow target under
the same id. `provider-catalog-spec-coverage` must split the provider identity
before any Copilot OAuth/device-flow implementation is wired.

---

### AI21 (`ai21`)

**Tier**: B — OpenAI-compat (`base_url="https://api.ai21.com/studio/v1"`) | **Status**: 🟡 SDK/runtime convergence pending

**SDK Features**: Streaming ✅, Tool Use ✅, JSON Mode ✅, Batch API ✅, Fine-tuning ✅

**Models**: `j2-ultra`, `j2-mid`, `j2-light`

---

### Cerebras (`cerebras`)

**Tier**: B — OpenAI-compat (`base_url="https://api.cerebras.ai/v1"`) | **Status**: 🟡 SDK/runtime convergence pending

**Models**: `llama-3.1-8b`, `llama-3.1-70b`, `llama-3.3-70b`, `qwen-3-32b`

---

### Cloudflare (`cloudflare`)

**Tier**: B — OpenAI-compat (`base_url="https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1"`) | **Status**: 🟡 SDK/runtime convergence pending

**Requires**: `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` env vars. `account_id` injected into URL in constructor.

**Models**: `@cf/meta/llama-3.1-8b-instruct`, `@cf/meta/llama-3.3-70b-instruct-fp8-fast`, `@cf/deepseek-ai/deepseek-r1-distill-qwen-32b`

---

### DeepInfra (`deepinfra`)

**Tier**: B — OpenAI-compat (`base_url="https://api.deepinfra.com/v1/openai"`) | **Status**: 🟡 SDK/runtime convergence pending

**SDK Features**: Streaming ✅, Vision ✅, Tool Use ✅, Embeddings ✅, 100+ Models ✅

---

### DeepSeek (`deepseek`)

**Tier**: B — OpenAI-compat (`base_url="https://api.deepseek.com/v1"`) | **Status**: 🟡 SDK/runtime convergence pending

> Note: DeepSeek-R1 returns non-standard `reasoning_content` field. Handled: streaming emits it as `StreamChunk(metadata={"content_type": "reasoning"})`; buffered stores it in `LLMResponse.usage["reasoning"]`.

---

### Fireworks (`fireworks`)

**Tier**: B — OpenAI-compat (`base_url="https://api.fireworks.ai/inference/v1"`) | **Status**: 🟡 SDK/runtime convergence pending

---

### Groq (`groq`)

**Tier**: B — OpenAI-compat | **Status**: 🟡 SDK/runtime convergence pending

---

### Lambda API (`lambda_api`)

**Tier**: B — OpenAI-compat | **Status**: 🟡 SDK/runtime convergence pending

---

### Mistral (`mistral`)

**Tier**: B — OpenAI-compat | **Status**: 🟡 SDK/runtime convergence pending

---

### Nscale (`nscale`)

**Tier**: B — OpenAI-compat | **Status**: 🟡 SDK/runtime convergence pending

---

### OpenRouter (`openrouter`)

**Tier**: B — OpenAI-compat (`base_url="https://openrouter.ai/api/v1"`) | **Status**: 🟡 SDK/runtime convergence pending

---

### Perplexity (`perplexity`)

**Tier**: B — OpenAI-compat | **Status**: 🟡 SDK/runtime convergence pending

---

### SambaNova (`sambanova`)

**Tier**: B — OpenAI-compat | **Status**: 🟡 SDK/runtime convergence pending

---

### Together (`together`)

**Tier**: B — OpenAI-compat | **Status**: 🟡 SDK/runtime convergence pending

---

### xAI (`xai`)

**Tier**: B -> A migration (`OpenAI-compat` fallback -> official `xai-sdk`) | **Status**: 🟡 Phase 16 integration chain queued

**Open gaps**:
- `xai-config-base-url-yaml` — keep endpoint precedence deterministic for fallback and compatibility mode
- `xai-sdk-client-dependency-pin` — pin and gate official `xai-sdk` usage (`v1.13.0` observed in upstream releases, 2026-05-16)
- `xai-sdk-async-client-bridge` — add provider-side AsyncClient lifecycle and gRPC error mapping
- `xai-sdk-chat-stream-bridge` — map chat stream/sample outputs into CSS `StreamChunk` contract
- `xai-get-models-list` — drive model metadata from `client.models.list_language_models()` with deterministic fallback
- `xai-sdk-server-side-tools-usage` — add permission-aware support for xAI server-side tools (`web_search`, `x_search`, `code_execution`)
- `xai-sdk-telemetry-policy` — bridge xAI telemetry/retry/timeout controls into CSS observability/config policy

---

### OpenCode (`opencode`)

**Tier**: C — Custom In-House | **Status**: 🟡 registry/runtime convergence pending

---

## Prompt Caching Summary

| Provider   | Cache Method                                         | Status                                            |
|------------|------------------------------------------------------|---------------------------------------------------|
| Anthropic  | `cache_control` breakpoints via `core/prompt_cache/` | ✅ Phase 11                                        |
| Gemini     | `cachedContent` NATIVE_RESOURCE                      | ⛔ Deferred (`cache-gemini-context-cache` blocked) |
| All others | None (no provider-native cache)                      | —                                                 |

---

## Rules (all providers)

- Transport: use the declared Python SDK route when an SDK owner is defined; retain `aiohttp` for explicit custom HTTP providers only, and never use `httpx`.
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
| `src/css/api_services/xai/service.py` | `xAIApiService._default_base_url()`, `get_models()`, and official `AsyncClient` initialization; chat stream bridge and tool/telemetry mapping remain planned. |
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
| `xai-config-base-url-yaml`, `xai-sdk-client-dependency-pin`, `xai-sdk-async-client-bridge` | done | Official dependency, configured base URL, and direct `AsyncClient` initialization are in place. |
| `xai-sdk-chat-stream-bridge`, `xai-get-models-list`, `xai-sdk-server-side-tools-usage`, `xai-sdk-telemetry-policy` | pending | Finish official call flow and model discovery while preserving explicit fallback behavior and permission/telemetry guarantees. |
| `mistral-fim-adapter`, `mistral-ocr-adapter`, `groq-audio-adapter` | pending | Add optional capabilities and permission-gated tool exposure through existing provider services. |
| `openrouter-cost-tracking`, `openrouter-provider-list` | pending | Add non-fatal cost attribution and cached model catalog normalization. |
| `provider-sdk-runtime-consolidation`, `provider-catalog-spec-coverage` | pending | Replace copied provider REST execution with canonical SDK routes and reconcile unregistered providers/GitHub identity ownership. |
| `auth-provider-oauth-flows` | pending | Implement encrypted OAuth/device-flow credential handling after `auth-secrets-settings`; API-key execution remains current. |
| `audit42-api-services-duplicate-fragments` | pending | Remove duplicated provider service bodies after SDK-runtime consolidation. |
| `ollama-model-manager`, `ollama-router-check` | pending | Add provider-side model availability and integrate only after resilience routing exists. |
| `ollama-install-checker`, `ollama-process-manager`, `ollama-lifespan-wire` | pending | Phase 33 future host-process ownership; it must not be represented as existing runtime. |

### Numbered Work Order And Validation

1. Extend current provider service files and shared optional protocols rather
   than creating replacement provider packages.
2. Implement xAI/OpenRouter metadata and capability paths; xAI now requires
   official `xai-sdk` integration (AsyncClient, model list API, tool and
   telemetry wiring) with explicit compatibility fallback.
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

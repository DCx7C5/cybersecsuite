# @sdks — Unified SDK Architecture

**Location**: `src/css/core/sdks/`
**Status**: 🟡 Partial — Phase 10 unified gateway is implemented in part but is not the active provider runtime.

## Purpose

Target unified provider SDK abstraction layer. Runtime agent and proxy calls
currently go through `css.api_services.registry.ProviderRegistry`, not
`CSSLLMClient`; provider execution is not consolidated yet. The target layer
supports 4 adapter types:
- **NativeSDK**: full SDK features for Anthropic/OpenAI
- **HttpProvider**: YAML-driven HTTP clients for all providers
- **OllamaAdapter**: local HTTP client for Ollama
- **BrowserRelayAdapter**: browser plugin bridge (bypass API keys)

## Files

| File | Contents |
|------|----------|
| `registry.py` | `SDKRegistry` — singleton, lazy-load + cache, thundering-herd protection, factory support |
| `css_client.py` | `CSSLLMClient` — unified router; `UniversalLLMClient` — legacy alias |
| `adapters/__init__.py` | Adapter package init |
| `adapters/anthropic.py` | `AnthropicNativeAdapter` — wraps `anthropic.AsyncAnthropic` with prompt_caching, computer_use, extended_thinking |
| `__init__.py` | Public exports |

## Key Classes

### SDKRegistry
- Singleton registry for SDK provider classes/factories
- `register(provider_id, sdk_class_or_factory)` — register a provider
- `get(provider_id, **kwargs)` — lazy-load + cache with concurrent init protection
- `clear_cache(provider_id)` — invalidate cached instances
- `list_registered()` — enumerate registered providers
- Supports both class and factory-function registration
- Backed by `BaseRegistry[BaseApiServiceClient]`

### CSSLLMClient
- `get_sdk(provider_id, **kwargs)` — route to registered SDK
- `clear_cache(provider_id)` — invalidate SDK cache
- `list_registered()` — list registered providers

### UniversalLLMClient
- Backward-compatible alias for `CSSLLMClient`

## Global Functions

| Function | Purpose |
|----------|---------|
| `register_sdk(provider_id, sdk_class)` | Register globally |
| `get_sdk(provider_id, **kwargs)` | Get/cache SDK globally |
| `clear_sdk_cache(provider_id)` | Clear cached SDKs |
| `list_registered_sdks()` | List all registered |

## Integration Points

- `core/types/__init__.py` re-exports all public symbols from this module
- `core/types/base_client.py` defines `BaseApiServiceClient` base class
- `core/types/base_protocols.py` defines `LLMAdapter` Protocol
- Phase 10 T10.2–T10.5: NativeSDK, HTTP, Ollama, Browser Relay adapters
- Phase 10 T10.6: `UnifiedLLMClient` routing across all adapter types
- Phase 10 T10.7: provider-priority browser relay + DeepSeek adapter + web-LLM relay path

## File Inventory

| File | Status |
|------|--------|
| `registry.py` | ✅ DONE — SDK singleton + lazy-load + thundering-herd |
| `css_client.py` | ✅ DONE — CSSLLMClient + UniversalLLMClient alias |
| `model_mapper.py` | ✅ DONE — ModelNameMapper with 20+ canonical mappings |
| (moved) | `register_adapter_tools()` lives in `modules/tools/adapter_bridge.py` (bridges core sdks → module tools) |
| `adapters/__init__.py` | ✅ Exports all adapter types |
| `adapters/anthropic.py` | ✅ DONE — AnthropicNativeAdapter |
| `adapters/openai.py` | ✅ DONE — OpenAINativeAdapter |
| `adapters/http_provider.py` | ✅ DONE — HttpProviderAdapter (YAML-driven, OpenAI + Anthropic format) |
| `adapters/ollama.py` | ✅ DONE — OllamaAdapter |
| `adapters/browser_relay.py` | ✅ DONE — BrowserRelayAdapter with active polling, timeout/cancel, and failed-result normalization |
| `adapters/deepseek.py` | ✅ DONE — DeepSeek adapter with reasoning-content normalization and SDK registration |

## Phase 10 Todo Status

- `sdk-native-anthropic-adapter` — ✅ DONE (2026-05-09)
- `sdk-native-openai-adapter` — ✅ DONE (2026-05-09)
- `sdk-http-adapter-openai-compat` — ✅ DONE (2026-05-09)
- `sdk-http-adapter-proprietary` — ✅ DONE (2026-05-09)
- `sdk-model-name-mapper` — ✅ DONE (2026-05-09)
- `sdk-ollama-adapter` — ✅ DONE (2026-05-09)
- `sdk-builtin-tools-registry` — ✅ DONE (2026-05-09)
- `sdk-unified-client` — 📋 reopened (2026-05-26): `SDKRegistry` has no
  registered providers and cannot route `CSSLLMClient` calls yet.
- `sdk-replace-queryexecutor` — 📋 reopened (2026-05-26): QueryExecutor now
  uses provider-agnostic `AgentExecutor`, but that active route still reaches
  `api_services.ProviderRegistry`, not `CSSLLMClient`.
- `sdk-browser-relay-adapter` — ✅ DONE (2026-05-26)
- `sdk-browser-relay-polling` — ✅ DONE (2026-05-26)
- `sdk-deepseek-adapter` — ✅ DONE (2026-05-26)
- `sdk-browser-relay-provider-priority` — ✅ DONE (2026-05-26)
- `sdk-browser-relay-web-llm-relay` — ✅ DONE (2026-05-26)

## Browser Relay Priority Contract (T10.7)

Current planning contract for browser-plugin backend provider priority:

1. `github`
2. `codex`
3. `openai`
4. `deepseek`
5. `nvidia`
6. web relay path (currently `chat.openai.com` / `chatgpt.com` supported surface)

## Phase 16 Capability Expansion

Phase 16 extends the unified client rather than bypassing it with
provider-specific call paths. Capabilities must be expressed through shared
types/protocols, then translated inside supporting adapters.

### Capability Groups

| Group | Required capability | Primary owners/dependencies |
|-------|---------------------|-----------------------------|
| Reasoning and context | `ThinkingConfig`, preflight token estimation, and `ContextManagementConfig`/compaction event handling. | `core/types`, `core/events`, router. |
| Batch and background | `BatchAdapter`/`BatchJob` for Anthropic/OpenAI batch work; `BackgroundJob` and OpenAI background responses. | Tasks/session persistence and event completion. |
| Provider-native tools | Anthropic computer use, code execution, web search/fetch, shell/editor tools registered as builtin tools. | `modules/tools`; explicit Phase 15 permissions and Phase 14 interceptor hooks required. |
| Retrieval and caching | Cohere/Together rerank; Gemini persistent context caching. | Retrieval/cache contracts and telemetry. |
| Memory bridge | Anthropic memory tool implemented over canonical `core/memory` services. | Memory API and explicit tool grants. |
| Model lifecycle and cost | Ollama pull/list/delete/availability; OpenRouter exact generation cost/provider attribution. | Model registry, router, OTEL/cache. |
| Specialty adapter functions | Mistral OCR/FIM, Groq audio, xAI official SDK integration (AsyncClient/chat/models/tools/telemetry). | Shared optional protocols plus provider adapters. |
| Claude SDK bridge | Map Claude agent hooks/session operations to CSS event, permission, task, and session contracts. | `core/events`, permissions, sessions/tasks. |

### Foundation Work Order

| Sequence | Work | Reason |
|----------|------|--------|
| A | `thinking-config-struct` -> `thinking-config-adapter` -> `thinking-model-metadata`; `token-count-method` -> router use; `context-mgmt-struct` -> adapter use. | Provides routing and request-level contracts used by other features. |
| B | `batch-api-protocol` -> provider implementations; `background-job-struct` -> OpenAI background implementation. | High-value asynchronous capabilities with limited coupling. |
| C | Native-tool registry -> grants -> hooks -> isolated computer-use session. | Must wait for enforceable permissions. |
| D | Rerank, Gemini cache, memory-tool bridge. | Consumes stable retrieval/cache/memory owners. |
| E | Ollama lifecycle, OpenRouter accounting, specialty adapters, Claude hook/session bridge, xAI official SDK completion chain. | Provider-specific work after shared protocols are stable. |

### Non-Negotiable Contracts

- `UnifiedLLMClient` remains the caller-facing gateway for completion,
  streaming, token estimation, batch/background entry points, and capability
  routing.
- Unsupported provider features must fail explicitly or be omitted through
  capability discovery; adapters must not silently pretend support.
- Provider-native tools never imply permission: every execution passes through
  tool grants and before/after interception.
- Context compaction, tool use, background completion, model download, rerank,
  memory mutation, and generation-cost attribution emit observability events.
- SDK feature availability must be re-verified against installed/current SDK
  versions when implementation starts; the original capability audit is a
  planning input, not a permanent API guarantee.

### T16.15 xAI Official SDK Chain

Execution under `Phase 16 — Provider SDK Features / T16.15` is now explicitly:

1. `xai-config-base-url-yaml` + `xai-sdk-client-dependency-pin`
2. `xai-sdk-async-client-bridge`
3. `xai-sdk-chat-stream-bridge`
4. `xai-get-models-list`
5. `xai-sdk-server-side-tools-usage` + `xai-sdk-telemetry-policy`

This chain must preserve the existing `BaseApiServiceClient` stream contract
and explicit fallback behavior while moving the primary implementation to
official `xai-sdk` primitives.

## Executable Pending Contract (2026-05-26)

### Exact Phase 10 Files And Symbols

| Path | Current or planned symbol |
|------|---------------------------|
| `src/css/core/sdks/css_client.py` | Existing `CSSLLMClient`; integration point for relay selection. |
| `src/css/core/sdks/registry.py` | Existing `SDKRegistry`, `register_sdk()`, `get_sdk()`. |
| `src/css/core/sdks/adapters/http_provider.py` | Existing `HttpProviderAdapter`. |
| `src/css/core/sdks/adapters/deepseek.py` | `DeepSeekAdapter` wrapping the existing DeepSeek API service and preserving reasoning metadata. |
| `src/css/core/sdks/adapters/browser_relay.py` | `BrowserRelayAdapter` transport with queued-request polling and normalized relay outcomes. |
| `src/css/modules/llm_proxy/browser_plugin.py` | Browser-plugin relay endpoints (`/api/plugin/register`, `/heartbeat`, `/inject`, `/inject/next`, `/result`, `/result/{request_id}`). |
| `src/css/core/sdks/relay_router.py` | `RelayProviderPolicy` + `RelayAttempt` ordered fallback policy with deterministic attempt tracking. |
| `src/css/core/sdks/__init__.py` | Stable exports after adapter/router implementation. |

### Live Todo Map

| Todo ID | Status | Execution order |
|---------|--------|-----------------|
| `provider-sdk-runtime-consolidation` | pending | Reconcile competing `api_services`/`core.sdks` adapter and registry ownership before claiming unified routing. |
| `sdk-unified-client` | pending | Register canonical adapters in `SDKRegistry` after convergence and prove offline provider resolution. |
| `sdk-replace-queryexecutor` | pending | Route QueryExecutor through the canonical unified client only after the unified client is functional. |
| `sdk-browser-relay-adapter` | done | Relay adapter and backend plugin endpoints implemented with bounded TTL state. |
| `sdk-browser-relay-polling` | done | Active result polling/bridge contract over queued relay requests with completed/failed/expired/unknown lifecycle handling. |
| `sdk-deepseek-adapter` | done | Dedicated registered DeepSeek adapter with streaming and buffered reasoning normalization. |
| `sdk-browser-relay-provider-priority` | done | Ordered provider policy in `relay_router.py` wired into `CSSLLMClient` with typed attempt metadata. |
| `sdk-browser-relay-web-llm-relay` | done | Web relay slot wired through browser-plugin backend with explicit supported-target detection and typed unsupported-page failures. |

1. Reconcile the active `api_services.ProviderRegistry` route with the
   currently unregistered `SDKRegistry` route and select one executable
   provider gateway.
2. Express fallback order `github`, `codex`, `openai`, `deepseek`, `nvidia`,
   `web_relay` as data in `RelayProviderPolicy`, recording typed failed/skipped
   attempts.
3. Validate deterministic priority, unavailable-provider skipping,
   fallthrough/winner metadata, polling, web relay routing, import exports,
   `ruff`, `basedpyright`, and the `core/sdks` dependency scan.

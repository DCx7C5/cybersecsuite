# @sdks — Unified SDK Architecture

**Location**: `src/css/core/sdks/`
**Status**: 🔧 Phase 10 — Unified SDK Architecture (active)

## Purpose

Unified provider SDK abstraction layer. All LLM provider access goes through this module. Supports 4 adapter types:
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
| BrowserRelayAdapter | 📋 deferred (Phase 10 backlog) |
| `adapters/deepseek.py` | 📋 pending — dedicated DeepSeek adapter surface (T10.7) |

## Phase 10 Todo Status

- `sdk-native-anthropic-adapter` — ✅ DONE (2026-05-09)
- `sdk-native-openai-adapter` — ✅ DONE (2026-05-09)
- `sdk-http-adapter-openai-compat` — ✅ DONE (2026-05-09)
- `sdk-http-adapter-proprietary` — ✅ DONE (2026-05-09)
- `sdk-model-name-mapper` — ✅ DONE (2026-05-09)
- `sdk-ollama-adapter` — ✅ DONE (2026-05-09)
- `sdk-builtin-tools-registry` — ✅ DONE (2026-05-09)
- `sdk-unified-client` — ✅ DONE (2026-05-09)
- `sdk-replace-queryexecutor` — ✅ DONE (2026-05-09) — already refactored to provider-agnostic AgentExecutor
- `sdk-browser-relay-adapter` — 📋 deferred (Phase 10 backlog)
- `sdk-browser-relay-polling` — 📋 deferred (Phase 10 backlog)
- `sdk-deepseek-adapter` — 📋 pending (Phase 10 T10.7)
- `sdk-browser-relay-provider-priority` — 📋 pending (Phase 10 T10.7)
- `sdk-browser-relay-web-llm-relay` — 📋 pending (Phase 10 T10.7)

## Browser Relay Priority Contract (T10.7)

Current planning contract for browser-plugin backend provider priority:

1. `github`
2. `codex`
3. `openai`
4. `deepseek`
5. `nvidia`
6. web relay path (`grok.com` / `docs.claude.com` strategy)

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
| Specialty adapter functions | Mistral OCR/FIM, Groq audio, xAI discovery/config completion. | Shared optional protocols plus provider adapters. |
| Claude SDK bridge | Map Claude agent hooks/session operations to CSS event, permission, task, and session contracts. | `core/events`, permissions, sessions/tasks. |

### Foundation Work Order

| Sequence | Work | Reason |
|----------|------|--------|
| A | `thinking-config-struct` -> `thinking-config-adapter` -> `thinking-model-metadata`; `token-count-method` -> router use; `context-mgmt-struct` -> adapter use. | Provides routing and request-level contracts used by other features. |
| B | `batch-api-protocol` -> provider implementations; `background-job-struct` -> OpenAI background implementation. | High-value asynchronous capabilities with limited coupling. |
| C | Native-tool registry -> grants -> hooks -> isolated computer-use session. | Must wait for enforceable permissions. |
| D | Rerank, Gemini cache, memory-tool bridge. | Consumes stable retrieval/cache/memory owners. |
| E | Ollama lifecycle, OpenRouter accounting, specialty adapters, Claude hook/session bridge, xAI completion. | Provider-specific work after shared protocols are stable. |

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

## Executable Pending Contract (2026-05-26)

### Exact Phase 10 Files And Symbols

| Path | Current or planned symbol |
|------|---------------------------|
| `src/css/core/sdks/css_client.py` | Existing `CSSLLMClient`; integration point for relay selection. |
| `src/css/core/sdks/registry.py` | Existing `SDKRegistry`, `register_sdk()`, `get_sdk()`. |
| `src/css/core/sdks/adapters/http_provider.py` | Existing `HttpProviderAdapter`. |
| `src/css/core/sdks/adapters/deepseek.py` | Planned dedicated DeepSeek adapter. |
| `src/css/core/sdks/adapters/browser_relay.py` | Planned `BrowserRelayAdapter` transport implementation. |
| `src/css/core/sdks/relay_router.py` | Planned `RelayProviderPolicy`, `RelayAttempt`, provider-priority selection/fallback. |
| `src/css/core/sdks/__init__.py` | Stable exports after adapter/router implementation. |

### Live Todo Map

| Todo ID | Status | Execution order |
|---------|--------|-----------------|
| `sdk-browser-relay-adapter`, `sdk-browser-relay-polling` | pending | Implement relay request/result transport first. |
| `sdk-deepseek-adapter` | pending | Add dedicated registered provider adapter. |
| `sdk-browser-relay-provider-priority` | pending | Implement the ordered policy in `relay_router.py`, then call it from `CSSLLMClient`. |
| `sdk-browser-relay-web-llm-relay` | pending | Add the web relay endpoint only after the policy and relay transport exist. |

1. Preserve the current adapters/registry/client as the gateway and add only
   the missing adapter/router modules.
2. Express fallback order `github`, `codex`, `openai`, `deepseek`, `nvidia`,
   `web_relay` as data in `RelayProviderPolicy`, recording typed failed/skipped
   attempts.
3. Validate deterministic priority, unavailable-provider skipping,
   fallthrough/winner metadata, polling, web relay routing, import exports,
   `ruff`, `basedpyright`, and the `core/sdks` dependency scan.

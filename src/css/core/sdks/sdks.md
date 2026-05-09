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

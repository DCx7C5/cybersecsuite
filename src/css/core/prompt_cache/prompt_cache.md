# core/prompt_cache - Cross-Provider Prompt Caching Plan
Prompt caching remains a separate owner from general `core/cache`; any later
package relocation requires explicit source/import migration.

**Location target**: `src/css/core/prompt_cache/`
**Status**: Planned Phase 11 surface; package implementation is not yet validated as present.

## Purpose

Prompt caching is separate from general `core/cache` KV caching. It coordinates request-shaped caching around the unified LLM client and provider-native cache capabilities.

## Execution Flow

```text
UnifiedLLMClient request
  -> exact Redis response cache lookup
  -> prepare provider-native cache hints where supported
  -> adapter completion/stream execution
  -> parse provider-native cache usage
  -> store buffered complete response in Redis
  -> emit cache/usage telemetry
```

## Cache Tiers

| Tier | Coverage | Required behavior |
|------|----------|-------------------|
| Exact response cache | all providers | Redis key over provider, model, messages and request-affecting parameters |
| Native provider cache | supported providers | use native request shaping and parse cache usage |
| Semantic cache | later work only | do not assume it exists during Phase 11 |

## Provider Contract

| Provider | Native behavior to support |
|----------|----------------------------|
| Anthropic | automatic top-level `cache_control` by default; explicit block breakpoints only for mixed-cadence layouts; parse cache read/write input tokens |
| OpenAI | automatic prefix caching plus optional cache-key/retention hints; parse cached tokens |
| DeepSeek | automatic cache hit/miss usage parsing |
| Gemini | explicit cached-content resource remains separately gated |
| Other remote providers | exact Redis response cache only unless verified later |
| Ollama / browser relay | exact-response caching may avoid repeat execution/injection; no assumed provider billing savings |

## Required Types and Services

- `CachingCapability` metadata on LLM adapters
- `CacheStats` embedded in normalized LLM responses
- `PromptCacheManager` around adapter execution
- optional Anthropic explicit-breakpoint injector
- automatic native cache usage parser
- OpenObserve metrics for cache hit/miss/native savings

## Phase 11 Todos

| ID | Status | Requirement |
|----|--------|-------------|
| `cache-caching-capability-enum` | pending | capability metadata on adapters |
| `cache-response-stats-struct` | pending | normalized cache usage/result type |
| `cache-prompt-cache-manager` | pending | manager coordinating exact and native caches |
| `cache-redis-exact-match` | pending | exact response cache for every provider |
| `cache-redis-streaming-buffer` | pending | store complete buffered streams |
| `cache-anthropic-breakpoint-injector` | pending | optional explicit Anthropic layouts |
| `cache-automatic-native-tracking` | pending | Anthropic/OpenAI/DeepSeek usage parsing |
| `cache-gemini-context-cache` | blocked | Deferred Gemini resource lifecycle; do not implement until explicit quota/billing ownership is approved. |
| `cache-cost-savings-tracker` | pending | estimate savings from usage/pricing |
| `cache-metrics-openobserve` | pending | observability events |

## Integration Points

- `core/sdks`: unified adapter entry point and response types
- `core/cache`: Redis/general caching primitives, without merging ownership
- `modules/llm_proxy`: local compatibility calls must pass through prompt caching
- QoL controls: cache key must include output-control hash when enabled

## Executable File And Validation Contract

| Path | Planned symbols / responsibility |
|------|----------------------------------|
| `src/css/core/prompt_cache/manager.py` | `PromptCacheManager` request wrapping and cache/native orchestration. |
| `src/css/core/prompt_cache/types.py` | `CachingCapability`, `CacheStats` normalized values. |
| `src/css/core/prompt_cache/exact_cache.py` | Redis exact-match keys, buffered stream storage, QoL toggle hash input. |
| `src/css/core/prompt_cache/native_tracking.py` | Anthropic/OpenAI/DeepSeek native usage parsing. |
| `src/css/core/prompt_cache/anthropic.py` | Optional explicit Anthropic breakpoint shaping. |
| `src/css/core/prompt_cache/metrics.py` | Savings and OpenObserve-safe cache metrics. |
| `src/css/core/prompt_cache/gemini_cache.py` | Blocked future Gemini native-resource implementation only. |

1. Implement capability/stats values, manager, and exact cache before native
   provider shaping or metrics.
2. Include request-affecting QoL hashes in exact keys and persist buffered
   stream results only after successful completion.
3. Leave `gemini_cache.py` absent while its tracker row is blocked; a
   `NATIVE_RESOURCE` request must fail explicitly in the Phase 11 surface.
4. Validate key separation, native usage parsing, stream buffering, failure
   isolation, metrics redaction, blocked Gemini behavior, and dependency
   direction through the unified client.

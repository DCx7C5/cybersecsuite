# core/prompt_cache - Cross-Provider Prompt Caching Plan
Prompt caching remains a separate owner from general `core/cache`; any later
package relocation requires explicit source/import migration.

**Location**: `src/css/core/prompt_cache/`
**Status**: PARTIAL Phase 11 implementation; 9/11 todos done, metrics transport pending, Gemini blocked/deferred

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
| `cache-caching-capability-enum` | ✅ DONE | capability metadata on adapters |
| `cache-response-stats-struct` | ✅ DONE | normalized cache usage/result type |
| `cache-prompt-cache-manager` | ✅ DONE | manager coordinating exact and native caches |
| `cache-redis-exact-match` | ✅ DONE | exact response cache for every provider |
| `cache-redis-streaming-buffer` | ✅ DONE | stream wrapper now passes through provider chunks unchanged, assembles canonical `LLMResponse`, stores only successful completions, and supports cached stream replay |
| `cache-anthropic-breakpoint-injector` | ✅ DONE | optional explicit Anthropic layouts |
| `cache-automatic-native-tracking` | ✅ DONE | Anthropic/OpenAI/DeepSeek usage parsing |
| `cache-gemini-context-cache` | ❌ BLOCKED | Deferred Gemini resource lifecycle to Phase 12; explicit quota/billing approval required |
| `cache-cost-savings-tracker` | ✅ DONE | estimate savings from usage/pricing |
| `cache-metrics-openobserve` | PENDING | OpenObserve transport is not wired; exporter retains events until Phase 35 telemetry client/stream work lands |

## Integration Points

- `core/sdks`: unified adapter entry point and response types
- `core/cache`: Redis/general caching primitives, without merging ownership
- `modules/llm_proxy`: local compatibility calls must pass through prompt caching
- QoL controls: cache key must include output-control hash when enabled

## Executable File And Validation Contract

| Path | Status | Responsibility |
|------|--------|-----------------|
| `src/css/core/prompt_cache/__init__.py` | ✅ DONE | Module exports: CachingCapability, ResponseCacheStats, PromptCacheManager, etc. |
| `src/css/core/prompt_cache/types.py` | ✅ DONE | `CachingCapability` enum (5 levels), `ResponseCacheStats` msgspec struct, `CacheCapabilityMetadata` TypedDict |
| `src/css/core/prompt_cache/manager.py` | ✅ DONE | `PromptCacheManager` orchestration: tier selection, message preparation, cache key computation, cost estimation |
| `src/css/core/prompt_cache/exact_match_cache.py` | ✅ DONE | `ExactMatchPromptCache`: Redis O(1) lookup, get/set/delete/clear operations, TTL support |
| `src/css/core/prompt_cache/streaming_buffer.py` | ✅ DONE | Canonical `StreamChunk`/`LLMResponse` assembly, success-only cache storage, and pass-through stream buffering |
| `src/css/core/prompt_cache/native_cache_tracking.py` | ✅ DONE | `NativeCacheDetector`: Anthropic/OpenAI/DeepSeek cache hit parsing, `NativeCacheTracker`: aggregation |
| `src/css/core/prompt_cache/anthropic_breakpoints.py` | ✅ DONE | `inject_cache_breakpoints`: ephemeral cache control tokens, `estimate_message_tokens`: heuristic sizing |
| `src/css/core/prompt_cache/cost_savings_tracker.py` | ✅ DONE | `CostSavingsTracker`: cumulative tracking by provider/source, hourly trends, summary reporting |
| `src/css/core/prompt_cache/metrics_exporter.py` | PARTIAL | `OpenObserveMetricsExporter` retains unsent events by returning `False`; actual OpenObserve transport remains pending |
| `src/css/core/types/base_protocols.py` | ✅ DONE | Extended `LLMAdapter` with `cache_capability` property |

Validation checklist:
✅ Key separation by provider/model/messages/system_prompt
✅ Tier selection decision tree (NONE→Tier3, EXACT_ONLY→Tier1, NATIVE_AUTO→Tier2, RESOURCE→Tier3-deferred)
✅ Stream buffering finalization and Redis storage contract repair
✅ Native cache usage parsing (Anthropic, OpenAI, DeepSeek)
✅ Cost estimation with per-provider ratios
PENDING OpenObserve transport and metrics stream integration
✅ Exception handling with Rule 70 compliance
✅ Type hints fully annotated (Rule 66 compliance)

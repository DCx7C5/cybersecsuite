# core/resilience - Retry and Failure Handling

**Location**: `src/css/core/resilience/`
**Status**: Existing retry runtime plus planned Phase 13 routing/resilience expansion.

## Purpose

`core/resilience` owns reusable provider failure handling:

- retry configuration and retryable error classification
- provider-aware retry strategy selection
- async execution wrapping for API clients
- future circuit-breaker and rate-limit coordination required by provider routing

It does not own provider selection policy or model catalogs.

## Current Code Reality

| File | Responsibility |
|------|----------------|
| `config.py` | `RetryConfig`, `RetryStrategy`, `RetryableErrorType` |
| `detection.py` | maps providers to SDK-owned or wrapper-owned retries |
| `orchestrator.py` | async retry execution and attempt/result reporting |
| `retry_wrapper.py` | wraps provider clients with retry orchestration |

## Phase 13 Execution Contract

Routing sits between the unified LLM client and adapters:

```text
request -> choose targets/strategy -> budget gate -> circuit breaker
        -> rate limiter -> adapter call -> usage/cost record -> fallback
```

The retained Phase 13 requirements are:

| Concern | Required implementation |
|---------|-------------------------|
| Strategy selection | `PRIORITY`, `ROUND_ROBIN`, `COST_OPTIMIZED`, `WEIGHTED`, `RANDOM`, `LEAST_USED`, `FILL_FIRST`, `P2C`, `STRICT_RANDOM`, `LKGP`, `CONTEXT_OPTIMIZED`, `CONTEXT_RELAY`, `AUTO` |
| Tier selection | ordered `ProviderTier` list from local/light models through frontier fallback; security, hardware and budget filters apply |
| Resilience | per-target circuit breaker and budget guard |
| Throttling | token-bucket RPM/TPM provider limits with learned response-header updates |
| Accounting | pre-request token estimation plus per-request usage/cost/latency persistence |
| Integration | unified client routing entry point and local triage-assisted target selection |

### Provider Tier Contract

`PROVIDER_TIER_LIST` is ordered from least expensive/local to frontier
fallback. `S_PLUS` is always the final entry; add new tiers before it and
renumber ranks by list position.

| Rank | Label | Representative models | Complexity ceiling | Runtime |
|------|-------|-----------------------|--------------------|---------|
| 0 | `LOCAL_MINIMAL` | `qwen3:0.6b`, `llama3.2:1b` | `SIMPLE` | Ollama, CPU only |
| 1 | `LOCAL_LIGHT` | `qwen3:1.7b`, `llama3.2:3b`, `phi3:mini` | `MODERATE` | Ollama, 4 GB VRAM |
| 2 | `LOCAL_STANDARD` | `qwen3:4b`, `mistral:7b`, `llama3.1:8b` | `MODERATE` | Ollama, 8 GB VRAM |
| 3 | `LOCAL_CAPABLE` | `qwen3:8b`, `llama3.1:8b-q8`, `deepseek-r1:8b` | `COMPLEX` | Ollama, 16 GB VRAM |
| 4 | `FREE_CLOUD` | Gemini Flash Lite, Groq/Together free offerings | `MODERATE` | HTTP, free |
| 5 | `BUDGET_CLOUD` | Gemini Flash, DeepSeek Chat, Grok Mini, Mistral Small | `COMPLEX` | HTTP, low cost |
| 6 | `STANDARD_CLOUD` | GPT-4o Mini, Claude Haiku, Gemini Pro, Mistral Large | `COMPLEX` | HTTP or native |
| 7 | `ADVANCED_CLOUD` | GPT-4o, Claude Sonnet, Gemini Pro, Grok | `CRITICAL` | HTTP or native |
| 8 | `PREMIUM_CLOUD` | GPT-4.5, Claude Sonnet, Gemini Pro, o3-mini | `CRITICAL` | Native |
| 9 | `ELITE_CLOUD` | Claude Opus, GPT-5, o3, Gemini Ultra | `CRITICAL` | Native |
| 10 | `S_PLUS` | frontier/deep-thinking models | `CRITICAL` | Native, unstable API guard |

| Request complexity | Minimum rank |
|--------------------|--------------|
| `TRIVIAL` / `SIMPLE` | 0, with cloud fallback if local unavailable |
| `MODERATE` | 1 |
| `COMPLEX` | 5 |
| `CRITICAL` | 7 |
| `SECURITY_CRITICAL` level 9+ | 9 |

Routing must skip local tiers when hardware requirements are unmet, skip
targets exceeding remaining budget using estimated tokens, and fall forward
through higher tiers on failure. S+ is the terminal fallback.

### Phase 13 Work Order

| Stage | Required result |
|-------|-----------------|
| Foundation | `ComboTarget`, `ComboConfig`, strategy and complexity enums |
| Selection | all 13 strategy implementations and tier resolver |
| Guards | per-target circuit breaker, per-combo budget guard, RPM/TPM limiter |
| Accounting | token counter and persisted usage/cost/latency record |
| Routing | `ComboRouter`, registry and triage-assisted fallback chain |
| Wiring | unified-client integration and routing/budget/circuit-breaker REST endpoints |

## Integration Points

| Component | Relationship |
|-----------|--------------|
| `core/sdks` | adapter calls to be guarded/routed |
| `api_services/*` | current retry-wrapper consumers |
| `modules/llm_proxy` | proxy requests must not bypass resilience |
| `modules/triage` | optional local classification feeding provider choice |
| `core/events` / OTEL | failures, retries, latency and fallback observations |

## Placement Decision

The module-owned response strategy stage remains in `modules/strategies`; the
redundant root `core/routing.py` facade was removed during
documentation/source ownership cleanup. Phase 13 provider-routing components
belong below `src/css/core/resilience/routing/` as a dedicated subpackage.
They must remain distinct from response injection strategy routing.

## Executable Routing Contract

### Exact Planned Files And Symbols

| Path | Symbols / responsibility |
|------|--------------------------|
| `src/css/core/resilience/routing/strategy.py` | `Strategy`, `ProviderTier`, `PROVIDER_TIER_LIST`. |
| `src/css/core/resilience/routing/models.py` | `ComboTarget`, `ComboConfig`, `ResolvedTarget`. |
| `src/css/core/resilience/routing/strategies.py` | `_apply_strategy()` and deterministic per-combo strategy state. |
| `src/css/core/resilience/routing/circuit_breaker.py` | `CircuitBreaker` state and recovery guard. |
| `src/css/core/resilience/routing/budget.py` | `BudgetGuard` per-combo spend guard. |
| `src/css/core/resilience/routing/rate_limiter.py` | `RateLimiter` provider token-bucket guard. |
| `src/css/core/resilience/routing/token_counter.py` | `TokenCounter` best-effort input estimate. |
| `src/css/core/resilience/routing/usage_tracker.py` | `UsageTracker`, `UsageRecord` request accounting. |
| `src/css/core/resilience/routing/triage.py` | `RequestComplexity`, `TriageMetrics`, `analyze_complexity()`. |
| `src/css/core/resilience/routing/tier_selector.py` | `TierSelector.filter()`. |
| `src/css/core/resilience/routing/qwen_triage.py` | `QwenTriageRouter`. |
| `src/css/core/resilience/routing/registry.py` | `ComboRegistry`. |
| `src/css/core/resilience/routing/router.py` | `ComboRouter.route()`. |
| `src/css/core/resilience/routing/endpoints.py` | Admin-only routing API router. |
| `src/css/modules/llm_proxy/client.py` | Planned `UnifiedLLMClient.complete()` / `stream()` integration owner. |

### Live Todo Map

| Todo IDs | Live status | Execution dependency |
|----------|-------------|----------------------|
| `routing-strategy-enum`, `routing-combo-target-model` | done | Foundation value types and ordered tiers first. |
| `routing-strategy-resolver` | done | `_apply_strategy()` implemented with all 13 strategy branches and deterministic state dictionaries. |
| `routing-tier-selector` | done | `TierSelector.filter()` enforces complexity, hardware, budget, security, and `S_PLUS` fallback chain rules. |
| `routing-triage-complexity`, `routing-token-counter` | pending | Remaining pure selection/classification logic. |
| `routing-circuit-breaker`, `routing-budget-guard`, `routing-rate-limiter`, `routing-usage-tracker` | pending | Isolated runtime guards and accounting. |
| `routing-combo-registry`, `routing-combo-router`, `routing-qwen-triage-router` | pending | Configuration and routed request execution. |
| `routing-unified-client-wire`, `routing-rest-endpoints` | pending | Public client/API wiring after router behavior is tested. |

### Validation Sequence

1. Implement foundation structs/enums and verify imports plus stable tier
   ordering with `S_PLUS` last.
2. Unit-test pure selection, token estimation, and each stateful guard before
   constructing `ComboRouter`.
3. Test routed fallback with fake adapters, budget/rate/circuit failure paths,
   and best-effort usage persistence.
4. Only then mount API/client integrations; run route discovery, dependency
   scans, `ruff`, `basedpyright`, and focused request-path tests.

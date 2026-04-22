# Stub Implementation & MCP Cleanup — May 2026

## Summary

Deleted the redundant `routing.py` module and fully implemented all remaining stub tools
in the `cybersec` MCP server. Tool count: **88 → 78** (routing.py removed, 8 stubs → live).

---

## Changes

### Deleted

- **`src/csmcp/cybersec/routing.py`** — 10 all-stub tools removed.
  All were redundant with or superseded by `proxy.py`, which already provides live
  equivalents backed by `ai_proxy.routing.combo`. Name collisions (`simulate_route`,
  `explain_route`) also resolved by this deletion.
- Import and concat entry for `_routing_tools` removed from `src/csmcp/cybersec/__init__.py`.

### Implemented (stubs → live)

#### `health.py` — 3 tools (was stub, now live)
Backed by `ai_proxy.providers.registry`, `ai_proxy.routing.combo`,
`ai_proxy.services.usage_tracker`, `ai_proxy.services.rate_limiter`.

- `get_health` — uptime, circuit breakers, provider availability, service status
- `get_provider_metrics` — per-provider success rate, token/cost totals, circuit breaker and rate limit state
- `get_session_snapshot` — full session cost/usage summary, recent requests, open circuit breakers, budget map

#### `quo_pricing.py` — 3 tools (was stub, now live)
Backed by `ai_proxy.services.usage_tracker` and `ai_proxy.providers.registry`.

- `check_quota` — rate limit and budget quota per provider; shows budget remaining
- `cost_report` — cost breakdown by provider, sorted by spend; includes recent request log
- `list_models_catalog` — full model catalog with context window, cost per 1M tokens, availability

#### `web_search.py` — 1 tool (was stub, now live)
Routes to first available engine from env keys. Priority: Perplexity → Serper → Brave → Tavily.
Falls back gracefully with a clear error if no API key is set.

- `web_search` — real search via `httpx`; returns title, URL, snippet, engine, rank

Supported env vars: `PERPLEXITY_API_KEY`, `SERPER_API_KEY`, `BRAVE_API_KEY`, `TAVILY_API_KEY`

#### `sync.py` — 1 tool (was stub, now live)
Backed by `ai_proxy.providers.registry.load_custom_providers`.

- `sync_pricing` — reloads provider and pricing config from `~/.cybersecsuite/providers.yaml`
  (or `CYBERSEC_PROVIDERS_CONFIG`); returns count of providers loaded and elapsed ms

### Documentation Updated

- `docs/mcp/tools.md` — 88 → 78 tools, routing.py section removed, all status badges updated
- `docs/mcp/overview.md` — 120 → 110 total, 88 → 78 cybersec, routing.py row removed
- `docs/README.md` — all tool counts corrected (110 total: 78 + 5 + 27)
- `src/csmcp/cybersec/__init__.py` — docstring updated to "78 tools"

---

## Tool Count Summary

| Module          | Before | After | Notes                           |
|-----------------|--------|-------|---------------------------------|
| `routing.py`    | 10     | —     | Deleted (all stubs, redundant)  |
| `health.py`     | 3 stub | 3 live | Real ai_proxy backend          |
| `quo_pricing.py`| 3 stub | 3 live | Real usage_tracker + registry  |
| `web_search.py` | 1 stub | 1 live | httpx + 4 search engines       |
| `sync.py`       | 1 stub | 1 live | load_custom_providers           |
| **Total**       | **88** | **78** | 0 stubs remain                 |

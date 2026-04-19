# OmniRoute MCP Server Reference

## Overview
The OmniRoute MCP server is a self-contained TypeScript server at `src/omniroute_mcp/server.ts` that provides 27 tools for AI gateway intelligence. It communicates with the OmniRoute AI routing gateway via HTTP.

Key facts:
- Version: 1.9.0 (cybersecsuite-embedded)
- Runtime: Bun (TypeScript executed natively, no compilation)
- Transport: MCP stdio (via @modelcontextprotocol/sdk)
- Base URL: OMNIROUTE_BASE_URL (default http://localhost:20128)
- Authentication: Optional Bearer token via OMNIROUTE_API_KEY
- Self-contained: Zero cross-repo imports. All utilities inlined.
- Audit: Optional SQLite logging to ~/.omniroute/storage.sqlite

## Configuration

### mcp.json entry
```json
{
  "omniroute": {
    "command": "bun",
    "args": ["run", "${workspaceFolder}/src/omniroute_mcp/server.ts"],
    "env": {
      "OMNIROUTE_BASE_URL": "http://localhost:20128",
      "OMNIROUTE_API_KEY": "",
      "OMNIROUTE_MCP_ENFORCE_SCOPES": "false"
    },
    "cwd": "${workspaceFolder}/src/omniroute_mcp"
  }
}
```

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| OMNIROUTE_BASE_URL | http://localhost:20128 | OmniRoute gateway URL |
| OMNIROUTE_API_KEY | (empty) | Bearer token for auth |
| OMNIROUTE_MCP_ENFORCE_SCOPES | false | Enable scope-based tool access |

### Dependencies (package.json)
- @modelcontextprotocol/sdk — MCP protocol implementation
- zod — Schema validation for tool parameters
- better-sqlite3 — Audit logging (optional, graceful degradation)

## Tools Reference (27 total)

### Essential Tools (9)

#### omniroute_get_health
Get OmniRoute health status, uptime, memory usage, and circuit breaker states.
- Parameters: none
- Returns: { status, uptime_seconds, memory_mb, circuit_breakers, version }

#### omniroute_list_combos
List all configured model combos (routing chains) with their strategies and targets.
- Parameters: none
- Returns: Array of combo objects with id, name, strategy, targets[], enabled

#### omniroute_get_combo_metrics
Get detailed performance metrics for a specific combo.
- Parameters: combo_id (string, required)
- Returns: { combo_id, total_requests, success_rate, avg_latency_ms, p50, p95, p99 }

#### omniroute_switch_combo
Activate or deactivate a model combo.
- Parameters: combo_id (string, required), enabled (boolean, required)
- Returns: { combo_id, enabled, previous_state }

#### omniroute_check_quota
Check remaining API quota for a specific provider.
- Parameters: provider (string, required)
- Returns: { provider, remaining_requests, remaining_tokens, reset_at }

#### omniroute_route_request
Send a chat completion request through OmniRoute's intelligent routing.
- Parameters: messages (array, required), model (string, optional), strategy (string, optional)
- Returns: Standard OpenAI-compatible chat completion response

#### omniroute_cost_report
Get cost breakdown by period, provider, and model.
- Parameters: period (string: "1h"|"24h"|"7d"|"30d", optional)
- Returns: { total_cost, by_provider: {}, by_model: {}, period }

#### omniroute_list_models_catalog
List all available AI models across all providers with capabilities.
- Parameters: provider (string, optional filter)
- Returns: Array of model objects with id, provider, context_window, pricing

#### omniroute_web_search
Perform web search via configured search provider (Serper/Brave/Perplexity/Exa/Tavily).
- Parameters: query (string, required), num_results (number, optional, default 5)
- Returns: Array of search results with title, url, snippet

### Advanced Tools (11)

#### omniroute_simulate_route
Dry-run routing simulation — shows which provider would be selected without executing.
- Parameters: messages (array, required), strategy (string, optional)
- Returns: { selected_provider, reason, alternatives[], estimated_cost }

#### omniroute_set_budget_guard
Set a session-level budget with configurable action when exceeded.
- Parameters: budget_usd (number, required), action (string: "degrade"|"block"|"alert", required)
- Returns: { budget_usd, action, current_spend }

#### omniroute_set_routing_strategy
Update the routing strategy at runtime.
- Parameters: strategy (string, required), combo_id (string, optional)
- Returns: { strategy, applied_to }

#### omniroute_set_resilience_profile
Configure circuit breaker, retry, and timeout settings.
- Parameters: circuit_breaker_threshold (number), retry_max (number), timeout_ms (number)
- Returns: Updated resilience profile

#### omniroute_test_combo
Live-test each provider in a combo to verify connectivity and latency.
- Parameters: combo_id (string, required)
- Returns: Array of { provider, status, latency_ms, error? }

#### omniroute_get_provider_metrics
Get detailed provider metrics: latency percentiles, success rate, quota usage.
- Parameters: provider (string, required)
- Returns: { provider, requests, success_rate, latency: {p50, p95, p99}, quota }

#### omniroute_best_combo_for_task
Recommend the best combo for a specific task type.
- Parameters: task_type (string: "coding"|"analysis"|"creative"|"chat"|"math", required)
- Returns: { recommended_combo, reason, alternatives[] }

#### omniroute_explain_route
Explain why a request was routed to a specific provider.
- Parameters: request_id (string, required)
- Returns: { provider, strategy, factors[], score, alternatives[] }

#### omniroute_get_session_snapshot
Get full session analytics: requests, costs, providers used, errors.
- Parameters: none
- Returns: { session_id, total_requests, total_cost, providers_used, error_rate }

#### omniroute_db_health_check
Diagnose and optionally repair database drift.
- Parameters: repair (boolean, optional, default false)
- Returns: { status, issues[], repaired[] }

#### omniroute_sync_pricing
Sync model pricing from external sources.
- Parameters: provider (string, optional filter)
- Returns: { synced_count, providers[], last_sync }

### Memory Tools (3)

#### omniroute_memory_search
Search stored memories by type and content.
- Parameters: query (string, required), type (string: "factual"|"episodic"|"procedural"|"semantic", optional)
- Returns: Array of memory objects with id, content, type, relevance_score

#### omniroute_memory_add
Store a new memory.
- Parameters: content (string, required), type (string: "factual"|"episodic"|"procedural"|"semantic", required), metadata (object, optional)
- Returns: { id, content, type, created_at }

#### omniroute_memory_clear
Clear memories by type and/or age.
- Parameters: type (string, optional), older_than_days (number, optional)
- Returns: { cleared_count }

### Skill Tools (4)

#### omniroute_skills_list
List all registered skills with their status.
- Parameters: none
- Returns: Array of skill objects with id, name, enabled, description

#### omniroute_skills_enable
Enable or disable a specific skill.
- Parameters: skill_id (string, required), enabled (boolean, required)
- Returns: { skill_id, enabled }

#### omniroute_skills_execute
Execute a skill with input.
- Parameters: skill_id (string, required), input (string, required)
- Returns: Skill execution result (varies by skill)

#### omniroute_skills_executions
Get skill execution history.
- Parameters: skill_id (string, optional), limit (number, optional, default 20)
- Returns: Array of execution records with id, skill_id, input, output, duration_ms

## Architecture

```
Claude Code (stdio)
       │
       ▼
  MCP Server (server.ts, Bun runtime)
       │
       ├── Essential Tools ──→ OmniRoute HTTP API (:20128)
       │                        ├── /api/health
       │                        ├── /api/combos
       │                        ├── /api/quota
       │                        ├── /v1/chat/completions
       │                        └── /api/cost
       │
       ├── Advanced Tools ───→ OmniRoute HTTP API (:20128)
       │                        ├── /api/simulate
       │                        ├── /api/budget
       │                        ├── /api/strategy
       │                        └── /api/metrics
       │
       ├── Memory Tools ────→ OmniRoute HTTP API (:20128)
       │                        ├── GET /api/memory
       │                        ├── POST /api/memory
       │                        └── DELETE /api/memory
       │
       ├── Skill Tools ─────→ OmniRoute HTTP API (:20128)
       │                        ├── GET /api/skills
       │                        ├── PATCH /api/skills/:id
       │                        └── POST /api/skills/execute
       │
       └── Audit Logger ────→ ~/.omniroute/storage.sqlite
                                (mcp_tool_audit table)
```

## Scope Enforcement
When OMNIROUTE_MCP_ENFORCE_SCOPES=true, each tool is assigned a scope level:
- **essential**: Always allowed
- **advanced**: Requires elevated access
- **memory**: Requires memory access
- **skills**: Requires skill management access

Default (false): All tools accessible without scope checks.

## Audit Logging
Every tool invocation is logged to SQLite with:
- tool_name, arguments (JSON), result status, timestamp, duration_ms
- Table: mcp_tool_audit (auto-created if missing)
- Non-blocking: audit failures never affect tool execution
- Location: ~/.omniroute/storage.sqlite

## Migration from External Repo
Previously, the OmniRoute MCP server lived in a sibling `../OmniRoute` repository and imported internal modules. As of v1.9.0, all dependencies are inlined:
- `resolveOmniRouteBaseUrl` — URL resolution utility (inlined)
- `normalizeQuotaResponse` — quota response normalization (inlined)
- `getComboModelString/Provider/StepTarget` — combo step helpers (inlined)
- Memory tools — previously used internal DB imports, now use HTTP API
- Skill tools — previously used internal DB imports, now use HTTP API

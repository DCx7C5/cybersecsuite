# Plan: src/ Cleanup & Architecture Flowchart

**Date:** 2026-04-22  
**Status:** Pending

## Problem

Several issues in `src/` found during audit:
1. Root-level scripts (`fix_skills.py`, `worktree-session-manager.py`) belong in `scripts/`
2. `src/dashboard/api/opensearch_stats.py` is misnamed — it serves OpenObserve stats
3. `src/hooks/*.md` doc files are living inside a Python package directory, should be in `docs/`
4. Dead/stale files: `.bak` file, unused `persist_call()`, stale `schema.sql`, dead `src/db/opensearch/` module, duplicate `src/a2a/checks/` package
5. No Mermaid architecture flowchart exists

## Approach

Surgical moves/renames/deletes with reference updates. Then create the flowchart.

---

## Todos

| ID | Task |
|----|------|
| `move-scripts` | Move `fix_skills.py` + `worktree-session-manager.py` → `scripts/`; update all references |
| `rename-oo-stats` | `src/dashboard/api/opensearch_stats.py` → `openobserve_stats.py`; update import |
| `move-hook-docs` | Move 6 `src/hooks/*.md` files → `docs/hooks/` |
| `remove-dead-code` | Delete `.bak`, dead `persist_call()`, stale `schema.sql`, `src/db/opensearch/`, `src/a2a/checks/` |
| `mermaid-chart` | Create `docs/architecture/flowchart.md` with full Mermaid diagram |
| `changelog` | `docs/changelog/src-cleanup-2026-04-22.md` |

## File Reference Map

### move-scripts
- Move: `fix_skills.py` → `scripts/fix_skills.py`
- Move: `worktree-session-manager.py` → `scripts/worktree-session-manager.py`
- Update: `tests/test_worktree_manager.py` (line 28, 553) — path from `parent.parent / "worktree-session-manager.py"` → `parent.parent / "scripts" / "worktree-session-manager.py"`
- Update: `tests/test_llm_orchestrator.py` (line 428) — same path change
- Update: `scripts/gwt-aliases.sh` (line 16) — path in echo
- Update: `src/llm/db.py` (line 4) — comment only

### rename-oo-stats
- `git mv src/dashboard/api/opensearch_stats.py src/dashboard/api/openobserve_stats.py`
- Update: `src/dashboard/api/__init__.py` line: `from dashboard.api.opensearch_stats` → `openobserve_stats`

### move-hook-docs
- `mkdir docs/hooks/`
- Move 6 files: `RootCommandExecuted.md`, `SessionEnd.md`, `SessionStart.md`, `YaraRuleGeneration.md`, `YaraRuleOptimization.md`, `YaraRuleTesting.md`

### remove-dead-code
- `rm src/dashboard/templates/_panels.py.bak`
- Remove `persist_call()` function from `src/llm/db.py`
- `rm src/llm/schema.sql` (references dropped `llm_calls` table)
- `rm -r src/db/opensearch/` (Wazuh-only; `sync_audit_log` references dropped table; not imported by live code)
- `rm -r src/a2a/checks/` (duplicate of `src/checks/`; only difference is import namespace)
- Update: `src/manage/_commands.py` — change `from a2a.checks.integrity` → `from checks.integrity`

## Notes
- `src/manage.py` is a documented shim — stays at `src/manage.py`
- Duplicate model pairs (`artifact`/`artifacts`, `cve`/`cve_entry`, `ioc`/`ioc_entry`) are intentional — different classes with different purposes — leave them
- `src/db/intel_loader.py` is a backwards-compat shim — leave it
- `worktree-session-manager.py` at root is expected by tests via `parent.parent / "scripts" / ...` after move

---

## Mermaid Flowchart — Complete Layer Breakdown

Every layer to represent (top → bottom / outside → inside):

### Layer 0 — External Clients
- Browser Plugin (`src/browser-plugin/`) — background.js, content.js, popup
- Claude Code / OpenAI-compatible clients (curl, SDK, third-party)
- TypeScript agent node process (`src/agent_ts/`)

### Layer 1 — ASGI Entry (`src/proxy/asgi.py`)
- `POST /v1/*` — AI proxy
- `GET /api/*` — Dashboard REST
- `GET /sse/*` — Server-Sent Events
- `GET /a2a/*` — A2A agent-to-agent protocol
- `GET /` — Dashboard HTML

### Layer 2 — AI Proxy (`src/ai_proxy/`)
- `routes.py` — request intake + response dispatch
- `qol_controls/` — QoL output-control injection (scope cascade: session → project)
- `routing/combo.py` — 13 routing strategies, circuit breaker, budget guard
- `translators/core.py` — OpenAI ↔ Anthropic ↔ Gemini format translation
- `executors/` — anthropic_sdk, bedrock, foundry, vertex, playwright
- `services/rate_limiter.py` — token-bucket per-provider RPM/TPM
- `services/token_counter.py` — pre-flight token estimation (Anthropic SDK)
- `services/usage_tracker.py` — in-memory cost + latency log
- `providers/registry.py` — 60 provider configs

### Layer 3 — A2A Protocol (`src/a2a/`)
- `server.py` — HTTP A2A task handler
- `cybersec_agent.py` — concrete CybersecA2AAgent (CVE, IOC, MITRE, signing)
- `agent_sdk.py` — bridges to `claude_agent_sdk.query()`; loads .md agent definitions; session continuity; memory-enhanced streaming
- `registry.py` — discovers remote A2A agents by skill
- `task_store.py` — in-memory task lifecycle store

### Layer 4 — Claude Agent SDK (external `claude_agent_sdk`)
- `query()` — multi-turn conversation engine
- `ClaudeAgentOptions` / `AgentDefinition`
- `HookMatcher` — hook dispatch
- Messages: `SystemMessage`, `AssistantMessage`, `ResultMessage`
- `BetaLocalFilesystemMemoryTool`
- `tool_runner`
- `.claude/agents/*.md` — 33 specialist agent definitions

### Layer 5 — Agent Runner (`src/agent/`)
- `runner.py` — `AgentRunner` multi-turn ClaudeSDKClient wrapper
- `client_pool.py` — pool of SDK clients
- `streaming.py` — SSE adapter (text/tool_use/tool_result/result/error)
- `session_linking.py` — links DB sessions ↔ SDK session IDs
- `sessions.py` — session management
- `hooks.py` — hook registration helpers
- `options_manager.py` — agent option builder

### Layer 6 — MCP Server (`src/csmcp/`)
- `_sdk_compat.py` — `@tool` decorator, `SdkMcpServer` shim (real SDK or fallback)
- `cybersec/server.py` — `mcp.server.Server` stdio bridge (for Claude Code `mcp.json`)
- 56 cybersec tools across 15 categories (findings, proxy, routing, cache, session, cases, PoC, DB, intelligence, layers, memory, QoL, sync, health, web search)
- `dystopian_server.py` + `dystopian.py` — 5 Ed25519/BLAKE2b/AES-GCM crypto tools

### Layer 7 — Hooks (`src/hooks/`, `src/agent_ts/hooks/`, `.claude/hooks/`)
- `hooks/sdk_hooks.py` — Python `HookMatcher` hooks (audit, path safety checks)
- `hooks/ipc_receiver.py` — Unix socket `/tmp/cybersecsuite-hooks.sock`; receives from TypeScript
- `hooks/session_start.py`, `session_end.py`, `root_command_executed.py`
- `hooks/threat_detected.py`, `user_prompt_submit.py`, `termmate_idle.py`
- `hooks/yara_rule_generator.py`, `yara_rule_optimizer.py`, `yara_rule_tester.py`
- `src/agent_ts/hooks/` — TypeScript hook side: `css_first_setup.ts`, `config.ts`, `session.ts`, `setup.ts`, `tasks.ts`, `team.ts`
- `src/agent_ts/ipc.ts` — TypeScript → Unix socket → Python IPC bridge

### Layer 8 — Dashboard (`src/dashboard/`, `src/ts_api/`, `src/frontend/`)
- `routes.py` — Starlette route mounting
- `api/` — 40+ REST handlers
- `api/sse.py` — SSE event stream
- `api/ts_proxy.py` — proxies to `src/ts_api/` Node server
- `templates/` — Jinja2 server-side HTML (via `template_engine/`)
- `src/ts_api/server.ts` — Node.js Express API (memory, stream, structured, thinking, tools routes)
- `src/frontend/` — React Vite SPA (App.tsx, main.tsx)

### Layer 9 — SDK / Scope (`src/cybersecsuite/`, `src/template_engine/`)
- `CyberSecSuiteSDK` — scope manager: `session()`, `resume()`, `set()`, `render()`
- `_context.py` → `template_engine/context.py` — 4-scope deep-merge: `~/.claude` → `~/.cybersecsuite` → `.claude/` → `.css/sessions/<id>/`
- `_session_io.py` — `session-manifest.json`, `.last_session`, `latest` symlink
- `template_engine/session_scope.py` — `CYBERSEC_SESSION_SCOPE` resolver, path helpers
- `template_engine/renderer.py` — Jinja2 `ChoiceLoader`, `_SilentUndefined`, custom filters
- `template_engine/discovery.py` — template filesystem discovery

### Layer 10 — LLM Client (`src/llm/`)
- `orchestrator.py` — `open_session()`, `close_session()`, lifecycle
- `client.py` — Anthropic SDK thin wrapper
- `db.py` — `llm_sessions` PG writes; `cost_report()`
- `pricing.py` — per-model cost calculation
- `otel.py` — OpenTelemetry integration

### Layer 11 — Cryptography (`src/crypto/`)
- `ssl_signer.py` — RSA-2048 signature generation/verification
- `key_manager.py` — password-protected key lifecycle
- `artifact_manager.py` — artifact CRUD + auto-sign
- `vault.py` — file-based encrypted secret storage
- `cache.py` — key cache
- `cli_integration.py` — `manage.py ssl-*` commands

### Layer 12 — Memory (`src/memory/`)
- `backends/obsidian.py` + `obsidian_async.py` — Obsidian vault read/write
- `canvas/generator.py` + `canvas_validate.py` — Obsidian Canvas JSON gen/validation
- `vault/manager.py` — vault CRUD
- `vault/hot_cache.py` — in-memory vault cache

### Layer 13 — Telemetry (`src/telemetry/`)
- `store.py` — `MetricsStore` ring buffer, `p50/p95/p99`
- `collector.py` — metric aggregation
- `middleware.py` — Starlette request timing middleware
- `decorators.py` — `@record_latency` etc.

### Layer 14 — Database (`src/db/`)
- `bootstrap.py` — Tortoise ORM init, asyncpg
- `models/` — 41 models (scope, forensic, intelligence, compliance, accounts, etc.)
- `intel/bootstrap.py` — intel seeding + OO write path
- `seeds/` — MITRE, CVE, CWE, CAPEC, NIST
- `migration/scope_v2.py` — scope path migration

### Layer 15 — Accounts (`src/accounts/`)
- `manager.py` — account CRUD
- `registry.py` — provider account registry
- `sync.py` — account sync

### Layer 16 — Marketplace (`src/marketplace/`)
- `models.py`, `registry.py`, `seed.py`

### Layer 17 — Startup (`src/startup/first_run.py`)
- First-run DB init check, sentinel creation

### Layer 18 — Infrastructure (Docker Compose)
- PostgreSQL 16 (asyncpg, Tortoise ORM) — port 5432
- Redis (session cache) — port 6379
- OpenObserve (observability sink) — port 5080; streams: audit-logs, api-usage, llm-calls, intel-update-log
- OpenSearch (Wazuh-only, not yet wired) — port 9200
- dbus notifier (`src/dbus/notifier.py`)

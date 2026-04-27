# Module Map

File-by-file breakdown of the CyberSecSuite source tree.

---

## `src/` — Application Source

```
src/
├── proxy/                  ASGI application
│   └── asgi.py               Starlette app, mount map, startup/shutdown lifecycle
│
├── a2a/                    A2A protocol + agent SDK bridge
│   ├── agent.py              BaseA2AAgent (stream + execute)
│   ├── server.py             A2AServer (Starlette router, JSON-RPC dispatch)
│   ├── client.py             A2AClient (async HTTP for remote agents)
│   ├── registry.py           AgentRegistry (skill-based lookup)
│   ├── agent_loader.py       .claude/agents/*.md YAML frontmatter parser
│   ├── agent_sdk.py          SDK bridge (caching, model routing, MCP wiring)
│   ├── cybersec_agent.py     CybersecA2AAgent (orchestrator, 5 skills)
│   ├── task_store.py         In-memory + DB task state machine
│   ├── models.py             Pydantic A2A protocol models
│   └── enums.py              TaskState, MessageRole, PartType, AuthScheme
│
├── agent/                  Agent execution runtime
│   ├── runner.py             AgentRunner (multi-turn, mode support)
│   ├── sessions.py           SessionManager (case mapping, forking)
│   ├── streaming.py          SSE adapter for SDK async generators
│   └── hooks.py              SDK-level hooks (security, audit, IOC, cost)
│
├── ai_proxy/               Multi-provider AI routing
│   ├── routes.py             OpenAI-compatible /v1/* endpoints
│   ├── routing/
│   │   └── combo.py          13 routing strategies + circuit breaker + QoL injection hook
│   ├── qol_controls/         QoL output-control injection (Phase 1)
│   │   ├── models.py           QoLToggle (8 toggles), QoLSettings, 5 builtin presets
│   │   ├── prompts.py          Prompt fragments; build_fragment_block (cached)
│   │   └── manager.py          QoLManager: inject_into_request, estimate_tokens, telemetry
│   ├── providers/
│   │   ├── registry.py       ProviderConfig loader
│   │   └── _providers.py     60 built-in provider definitions
│   ├── services/
│   │   ├── rate_limiter.py   Per-provider RPM/TPM token bucket
│   │   └── usage_tracker.py  Token + cost tracking (DB-backed)
│   ├── translators/          Request/response format adapters (OpenAI↔Anthropic↔Gemini)
│   └── executors/            Async HTTP execution with retry + circuit breaker
│
├── csmcp/                  MCP tool package
│   ├── _sdk_compat.py        @tool decorator, SdkMcpServer shim, create_sdk_mcp_server()
│   ├── cybersec/             87 tools across 24 modules
│   │   ├── server.py           Stdio entry point (uv run python -m csmcp.cybersec.server)
│   │   ├── helpers.py          Scope utils, sdk_result(), sdk_error()
│   │   ├── findings.py         add_finding, add_ioc, query_findings, update_risk_register
│   │   ├── db.py               db_healthcheck, bootstrap_intelligence
│   │   ├── intelligence.py     suggest_mitre, get_project_memory
│   │   ├── layers.py           share_to_layers, get_layer_value
│   │   ├── cache.py            cache_lookup/store/analytics/invalidate
│   │   ├── proxy.py            proxy_chat/providers/models/usage/cost + routing tools (10)
│   │   ├── session.py          session_snapshot, agent_registry, best_provider
│   │   ├── cases.py            case_open, case_status
│   │   ├── poc.py              query_pocs, add_poc
│   │   ├── routing.py          combo_list/metrics/switch/test, route_request, ... (10)
│   │   ├── quo_pricing.py      check_quota, cost_report, list_models_catalog
│   │   ├── ai_memory.py        memory_search, memory_add, memory_clear
│   │   ├── web_search.py       web_search
│   │   ├── sync.py             sync_pricing
│   │   ├── health.py           get_health, get_provider_metrics, get_session_snapshot
│   │   ├── template.py         template rendering tool
│   │   ├── skill_manager.py    skill listing/search/execution
│   │   ├── vault_tool.py       vault read/write/list/delete/status
│   │   ├── canvas_tool.py      canvas create/update/read/list/delete/export
│   │   ├── tool_toggles.py     tool enable/disable/status/list
│   │   ├── structured_extract.py structured data extraction tools
│   │   ├── thinking_tool.py    extended thinking tool
│   │   ├── tool_search.py      tool discovery/search
│   │   ├── agents_beta.py      agent management tools (beta, 10 tools)
│   │   └── qol_tools.py        QoL output controls — qol_get/set/reset/presets (4 tools)
│   └── dystopian.py          5 crypto tools (Ed25519, signing, verification)
│
│   ├── server.ts             29 tools, self-contained (~1100 lines)
│   ├── package.json          @modelcontextprotocol/sdk, zod, better-sqlite3
│   └── tsconfig.json         Bun-compatible (moduleResolution: bundler)
│
├── crypto/                 Cryptographic utilities
│   ├── key_manager.py        Ed25519 key generation, Argon2id encryption, rotation
│   ├── artifact_manager.py   BLAKE2b hashing + Ed25519 signing/verification
│   ├── ssl_signer.py         TLS certificate generation
│   └── ...                   cache, config, pydantic_models, template_renderer
│
├── dashboard/              Monitoring dashboard (Starlette)
│   ├── routes.py             40+ endpoints (REST + SSE)
│   ├── api/                  9+ endpoint modules
│   │   ├── core.py             overview, providers, usage, health, crypto
│   │   ├── agents.py           a2a, agents, routing, factory, agent-query
│   │   ├── agent_stream.py     streaming chat start/stop + SSE bridge
│   │   ├── forensic.py         findings, iocs, yara, network, intel, audit, compliance, NIST
│   │   ├── ops.py              cases, tasks, task lifecycle, PoCs
│   │   ├── tables.py           db counts, models, generic table, prompts, telemetry
│   │   ├── settings.py         GET/PATCH settings with access control
│   │   ├── team_builder.py     team agents, skills, teams
│   │   ├── openobserve_stats.py stream health + stats
│   │   ├── sse.py              /sse/cases, /sse/tasks, /sse/health, /sse/telemetry
│   │   └── qol.py              GET|POST|DELETE /api/qol, /api/qol/presets
│   ├── _schema.py            Tortoise model introspector
│   └── templates/            HTML dashboard assembler (base, tabs, panels, JS)
│
├── db/                     Database layer (Tortoise ORM + asyncpg)
│   ├── bootstrap.py          init_tortoise_async(), health check, DB creation
│   ├── settings.py           Connection config from env vars
│   ├── seeds/                Live seeders (MITRE, NVD, CWE, CAPEC)
│   └── models/               44 ORM models across 30+ files
│
├── telemetry/              In-process metrics
│   ├── store.py              MetricsStore (ring buffer, p50/p95/p99, dual-write)
│   ├── middleware.py         ASGI TelemetryMiddleware (path normalization)
│   └── collector.py          TelemetryCollector (15s polling, rolling history)
│
├── openobserve/            OpenObserve integration
│   ├── client.py             Async singleton connection
│   ├── streams.py            Stream management
│   └── writer.py             Buffered bulk writer (100 docs / 5s flush)
│
├── opensearch/             OpenSearch integration (optional)
│   ├── client.py             Async singleton, index templates
│   └── writer.py             Buffered bulk writer
│
├── hooks/                  Filesystem event hooks (subprocess-based)
│   └── ...                   30+ Python modules, 15+ event types
│
└── manage.py               CLI dispatcher
```

---

## `.claude/` — Agent & Harness Config

```
.claude/
├── agents/                 Agent definitions (18 active)
│   ├── AGENT_FACTORY.md      Agent factory (creates new agents)
│   ├── DEV_SUB_AGENTS.md     Developer sub-agent definitions
│   ├── encoding-specialist.md Encoding analysis specialist
│   ├── teams/                3 team compositions
│   │   ├── blue-team.md        Defensive investigation team
│   │   ├── red-team.md         Offensive simulation team
│   │   └── purple-team.md      Combined offense + defense
│   └── sub_agents/           12 specialist sub-agents
│       ├── cybersec-agent.md
│       ├── code-reviewer.md
│       ├── frontend-design.md
│       ├── firmware-analyst.md
│       ├── logfile-analyst.md
│       ├── postgres-db-engineer.md
│       ├── python-code-reviewer.md
│       ├── python-developer.md
│       ├── reverse-engineer.md
│       ├── settings-analyst.md
│       ├── token-optimizer.md
│       └── watchdog.md
├── skills/                 922 SKILL.md across 24+ domains
├── hooks/                  10 workspace-level hooks
└── settings.json           Agent config, hooks, MCP, proxy settings
```

---

## Root Config Files

| File               | Purpose                                              |
|--------------------|------------------------------------------------------|
| `mcp.json`         | MCP server wiring (3 servers: cybersec, dystopian + playwright-stealth) |
| `docker-compose.yml` | 6 services (postgres, dashboard, redis, openobserve, wazuh, ollama) |
| `pyproject.toml`   | Python 3.14, uv, dependencies                        |
| `Makefile`         | Dev commands                                         |
| `.env`             | Environment secrets (copy from `.env.example`)       |

---

## Database Models (44 models, 65 tables)

| Domain                 | Count | Key Models                                                                     |
|------------------------|-------|--------------------------------------------------------------------------------|
| **Scope**              | 4     | Workspace, Project, Session, ScopedEntry (abstract)                            |
| **Investigation**      | 6     | Finding, IOC, Risk, Baseline, WatchlistItem, SharedEntry                       |
| **Intel — MITRE**      | 3     | MitreTechniqueIntel, MitreThreatActorIntel, MitreSoftwareFamilyIntel           |
| **Intel — Vulns**      | 3     | CVEIntel, CWEIntel, CapecAttackPatternIntel                                    |
| **Intel — Compliance** | 2     | NistCsfControl (185 controls), NistAiRmfControl (72 controls)                  |
| **Forensics**          | 5     | ForensicProject, ForensicSession, IOCEntry, ForensicWatchlistItem, ClearedItem |
| **Network**            | 7     | Network, Host, IPAddress, Domain, Certificate, NetworkConnection, Machine      |
| **Hardware**           | 5     | CPUInfo, MemoryModule, NetworkInterface, InterfaceAddress, StorageDrive        |
| **Artifacts**          | 2     | Artifact (versioned + signed), ArtifactSignatureLog                            |
| **Audit**              | 3     | AuditLog (immutable), ApiUsageLog (UUID PK), CaseIntake                        |
| **Other**              | 4     | Vulnerability, POCIntel, Tag, YaraRule                                         |

---

## Verified Import Analysis (2026-04-27)

### Critical Entrypoints (DO NOT REMOVE)

**proxy/asgi.py** — ASGI application entrypoint
- **Used by**:
  - `Makefile`: `uvicorn proxy.asgi:app --port 8000`
  - `src/ai_proxy/cli.py`: uvicorn entrypoint reference
  - `tests/test_dashboard_routing.py`: `from proxy.asgi import app`
  - Docker Compose: `cybersec-proxy` service
- **Status**: ESSENTIAL. Removing breaks entire backend.

**api/routes/*.py** — Worker management API endpoints
- **Used by**:
  - `tests/test_worker_api_crud.py`: `from api.routes.workers import router`
  - `tests/test_worker_batch.py`: `from api.routes.worker_batch import router, _process_batch_operation`
  - `tests/test_worker_metrics.py`: `from api.routes.worker_metrics import router`
  - `tests/test_worker_lifecycle.py`: `from api.routes.worker_lifecycle import router`
  - `tests/test_worker_history.py`: `from api.routes.worker_history import router`
- **Status**: ACTIVE. Phase 5+ worker API implementation.

### Active Dependencies (KEEP)

**dbus/notifier.py** — Desktop notifications
- **Used by**: `src/hooks/sdk_hooks.py` (optional import, fails gracefully if DBus unavailable)
- **Status**: ACTIVE. Used for SDK hook notifications.

**memory/* — Session state & vault storage**
- **Used by**:
  - `src/csmcp/cybersec/canvas_tool.py` (memory/vault, memory/canvas)
  - `src/csmcp/cybersec/vault_tool.py` (memory/vault)
- **Status**: ACTIVE. Canvas and vault tool integration.

### Docker Compose Health Checks

- **cybersec-proxy**: HTTP `/health` (8000)
- **cybersec-dashboard**: HTTP root (8000)
- **cybersec-postgres**: `pg_isready` check
- **cybersec-redis**: `redis-cli ping`
- **cybersec-ollama**: HTTP `/api/tags`
- **cybersec-openobserve**: HTTP `/healthz`

**Restart after code changes**:
```bash
# Python backend changes (proxy/*, api/*, db/*, ai_proxy/*)
docker-compose restart cybersec-proxy

# Frontend changes (src/frontend/*)
docker-compose restart cybersec-dashboard

# Full restart if needed
docker-compose down && docker-compose up -d
```

### Size Inventory

| Component | Size | Type |
|-----------|------|------|
| frontend/node_modules | 318MB | Reinstallable (npm ci) |
| agent_ts/node_modules | 263MB | Reinstallable (npm ci) |
| src/db | 2.1MB | Core database models |
| src/ai_proxy | 516KB | Core routing engine |
| src/hooks | 224KB | Lifecycle event system |
| All other Python | ~50KB | Utilities, integration |

**Total**: ~320MB (node_modules dominate; Python code is minimal)

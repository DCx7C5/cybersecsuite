# CyberSecSuite — MEMORY.md

_Last updated: 2026-04-19 (Dashboard: context-aware header, sidebar recategorization, agent factory UI, template API, generate endpoint)_

## Architecture

```
Claude Code / agent_sdk.py
        │  ANTHROPIC_BASE_URL=http://localhost:8000/v1
        ▼
  ASGI /v1/*  (AI Proxy — 60 providers, 13 strategies, cost-optimized default)
        │
  ┌─────┴──────┐
  │ /dashboard | SPA + 41 REST + 4 SSE routes
  │ /a2a       | A2A JSON-RPC → CybersecA2AAgent → SDK → .claude/agents/ → Proxy
  │ /health    | DB health (200/503)
  └────────────┘
  MCP (stdio): cybersec (31 tools) + dystopian-crypto (5 tools) + omniroute (27 tools) = 63 total
```

**Ports**: 8000 ASGI ✅ · 5432 PostgreSQL ✅ · 6379 Redis ✅ · 9200 OpenSearch ✅ · 5601 OS Dashboards ✅ · 20128 OmniRoute · 8080 alt ⚠️ · 8433 TLS ⚠️

**settings.json**: `.claude/settings.json` (NOT `settings.json`) · `agent: cybersec-agent` · `default_strategy: cost-optimized` · `hooks_dir: src/hooks/` · 10 workspace hooks (PreToolUse→PostCompact)

**Docker socket** (fixed `21f6cd96`): `CYBERSEC_DB_HOST: /tmp` — asyncpg reads host as directory, appends `/.s.PGSQL.5432`. `bootstrap.py` always passes `port` in config dict.

---

## Codebase Map

### src/ key files
| Path                      | Purpose                                                                                                        |
|---------------------------|----------------------------------------------------------------------------------------------------------------|
| `proxy/asgi.py`           | ASGI mount map, TelemetryMiddleware                                                                            |
| `manage.py`               | CLI dispatcher (`uv run python -m manage <cmd>`)                                                               |
| `csmcp/`                  | MCP package: `cybersec/` (31 tools, 8 submodules) + `dystopian.py` (5 tools)                                   |
| `agent/`                  | AgentRunner, SessionManager, streaming, hooks (Phase H)                                                        |
| `a2a/`                    | A2A JSON-RPC server, orchestrator, agent_sdk bridge, registry                                                  |
| `ai_proxy/`               | 60 providers (`registry.py` 1163L), routing (`combo.py` 574L), translators                                     |
| `crypto/`                 | Ed25519, BLAKE2b-256, Argon2id (mem=262144, iters=4), AES-256-GCM                                              |
| `db/`                     | 30+ model files, 40+ ORM models, 65 tables, `cybersec_forensics` DB                                            |
| `db/browser_forensics.py` | `BrowserForensicFinding` CRUD — `log_finding_async()`, `count_findings_by_severity()`, `get_recent_findings()` |
| `a2a/checks/`             | Integrity checks — FK, fixtures, config paths (moved from `src/checks/` in Phase M.3, commit `4a52b219`)       |
| `telemetry/`              | Ring-buffer metrics, p50/p95/p99, ASGI middleware, SSE collector — dual-write to OpenSearch ✅                  |
| `opensearch/`             | Async client singleton, index templates (telemetry/audit/api-usage), buffered bulk writer (100 docs/5s)        |

**src/csmcp/ rename**: `src/mcp/` → `src/csmcp/` (Phase H) — avoided naming conflict with pip `mcp` v1.26.0. `mcp_server.py` (1288L FastMCP) DELETED.

### src/dashboard/ (66+ routes)
| File                       | Lines | Purpose                                                                                                                                                            |
|----------------------------|-------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `routes.py`                | ~150  | Route wiring (66 routes)                                                                                                                                           |
| `_html.py`                 | 4     | Shim — imports `build_dashboard_html()` from `templates/`                                                                                                          |
| `templates/__init__.py`    | 25    | `build_dashboard_html()` assembler                                                                                                                                 |
| `templates/_components.py` | 71    | `stat_card`, `mini_card`, `stat_grid`, `tab_panel`, `simple_panel`, `section_h3/h4`, `table_slot`                                                                  |
| `templates/_base.py`       | ~760  | CSS (JetBrains Darcula palette, IDE statusbar, pagination fix, .af-check), `head()`, `header()`, `context_bar()` — replaces deprecated `stats_row()`/`tiers_row()` |
| `templates/_tabs.py`       | ~70   | `tab_bar()` — 26 items in 7 groups (PLATFORM/AI PROXY/AGENTS/OPERATIONS/FORENSICS/DATA/SETTINGS); removed providers/factory/agents-registry tabs                   |
| `templates/_panels.py`     | ~820  | `all_panels()` — 26 panel fns; `_agent_craft()` has full factory section; `_workflows()` separate                                                                  |
| `templates/_js.py`         | ~2050 | All JS: SSE, team builder, settings CRUD, explorer, agent query, MCP installer, hooks CRUD, context bar, `afLoadTemplates()`, `afGenerate()`                       |
| `api/core.py`              | 153   | overview, providers, usage, health, crypto                                                                                                                         |
| `api/agents.py`            | ~150  | a2a, agents (from .claude/agents/**/*.md), routing, factory, agent-query                                                                                           |
| `api/forensic.py`          | 396   | findings, iocs, yara, network, intel, audit, compliance, NIST                                                                                                      |
| `api/ops.py`               | 183   | cases, tasks, task lifecycle, PoCs                                                                                                                                 |
| `api/tables.py`            | 148   | db counts, investigations, models, generic table, prompts, telemetry                                                                                               |
| `api/settings.py`          | 55    | `GET/PATCH /api/settings` — editable: env/agent/proxy/asgi/cache/security/hooks_dir                                                                                |
| `api/settings_toggles.py`  | ~350  | All toggle/installer APIs: MCPs (project+global), skills, plugins, global summary, MCP install/remove, hooks CRUD                                                  |
| `api/team_builder.py`      | 310   | `GET /api/team-agents` · `GET /api/skills` · `GET/POST /api/teams` · `PUT/DELETE /api/teams/{name}`                                                                |
| `api/agent_crud.py`        | ~420  | `POST /api/agents/crud` · `GET/PUT/DELETE /api/agents/crud/{name}` · `POST /api/agents/generate` — factory generate endpoint                                       |
| `api/workflows.py`         | 247   | `GET/POST /api/workflows` · `GET/DELETE /api/workflows/{id}` — multi-step pipeline                                                                                 |
| `api/opensearch_stats.py`  | 47    | `GET /api/opensearch` — cluster health + per-index doc count/size                                                                                                  |
| `api/sse.py`               | 153   | /sse/cases · /sse/tasks · /sse/health · /sse/telemetry                                                                                                             |
| `_schema.py`               | 149   | Tortoise model introspector — 83 models                                                                                                                            |

**26 tabs in 7 groups** (commit `1f22e496`):
- **PLATFORM**: Health · Telemetry
- **AI PROXY**: Usage & Cost · Routing · Crypto
- **AGENTS**: Agent Craft · Team Builder · Agent Query · Workflows
- **OPERATIONS**: Cases · Tasks · PoCs · A2A Proto
- **FORENSICS**: Investigations · Findings · IOCs · YARA Rules · Network · Intel Feed · Audit Log · Compliance
- **DATA**: DB Counts · OpenSearch · Explorer
- **SETTINGS**: Settings

> ⚠️ Removed tabs: Providers, Factory (standalone), Agent Registry — consolidated/replaced.
- **SETTINGS**: Settings

**Context bar**: `#context-bar` div sits between topbar and content. Hidden by default (`display:none`). JS `_updateContextBar(tabName)` fetches tab-specific stats lazily, calls `_showCtxStats()` which sets `bar.style.display='flex'`. Cache per-tab in `_ctxCache` (invalidated by `refresh()`). Stats slots: `#ctx-s1..5`.

**Settings tab** (2 scope panes — 🌐 Global / 📁 Project):
- **Global scope**: MCP server toggles + Install MCP form + Remove button · Plugin toggles · Hooks manager (list + add/remove) · Env vars (read-only) · Summary
- **Project scope**: MCP server toggles · Skill domain toggles (26 domains) · Env vars (read-only) · Agent & Proxy config · Custom env editor · Hooks display

**Agent registry** (fixed `ba06006c`): `api_agents` scans `.claude/agents/**/*.md` directly — NO A2A protocol, NO fake URLs. Returns 37 agents (1 orchestrator, 36 specialists) with real frontmatter (name/description/role/model/tools/file).

**Key settings endpoints**:
| Endpoint | Method | Purpose |
|---|---|---|
| `/api/settings/mcps` | GET/PATCH | Project MCP enable/disable |
| `/api/settings/skills` | GET/PATCH | Skill domain enable/disable |
| `/api/settings/plugins` | GET/PATCH | Global plugin enable/disable |
| `/api/settings/global` | GET | Global ~/.claude summary |
| `/api/settings/global-mcps` | GET/PATCH | Global MCP enable/disable |
| `/api/settings/global-env` | GET | Global env vars (masked) |
| `/api/settings/project-env` | GET | Project env vars |
| `/api/settings/install-mcp` | POST | Install MCP to ~/.claude/settings.json |
| `/api/settings/remove-mcp` | DELETE | Remove MCP from ~/.claude/settings.json |
| `/api/settings/hooks` | GET/POST/DELETE | List/add/remove hooks in ~/.claude/settings.json |

**Key endpoints**: `GET /api/models` · `GET /api/tables/{model}` · `POST /api/agent-query` · `GET /api/settings` · `PATCH /api/settings` · `GET /api/team-agents` · `GET /api/skills` · `GET/POST /api/teams` · `POST /api/agents/crud` · `POST /api/agents/generate` · `GET /api/settings/agent-templates` · `POST /api/workflows` · `GET /api/opensearch`

**Agent factory endpoints**:
| Endpoint | Method | Purpose |
|---|---|---|
| `/api/settings/agent-templates` | GET | List `.claude/agents/templates/*.md` stems (31 templates) |
| `/api/agents/generate` | POST | Factory: generate structured agent markdown from FACTORY_VARS |

`POST /api/agents/generate` body: `{type, name, description, model, maxTurns, tools, templates, research, project_context, extra_instructions, save}`. Returns `{content, agent, file?, saved?}`. Builds: frontmatter → Chapter 1 Role/Mission → Chapter 2 Core Principles → Template content → Research sections → Project context block → Extra instructions → Delegation matrix (orchestrators only).

**Design system** (JetBrains New UI Darcula palette):
| Token | Value | Usage |
|---|---|---|
| `--bg` | `#1e1f22` | Window background |
| `--surface` | `#2b2d30` | Editor / card background |
| `--surface-2` | `#313438` | Panel background |
| `--border` | `#3d3f43` | All borders |
| `--accent` | `#3574f0` | Active/focus/buttons (JB blue) |
| `--cyan` | `#6897bb` | Info/numbers (JB info blue) |
| `--amber` | `#cb902e` | Warnings (JB orange) |
| `--red` | `#c75450` | Errors (JB red) |
| `--violet` | `#9876aa` | Keywords (JB purple) |
| `--success` | `#6a9955` | Success/strings (JB green) |
| `--text-primary` | `#cdd1d9` | Default text |
| `--text-muted` | `#808590` | Secondary text |

Status bar: fixed bottom bar (24px, accent blue) showing current tab name + live clock. Sidebar: 240px, 7 groups, 12px font, IDE-like tree style.

**Team Builder tab**: Agent Browser (filterable table of 37 agents), Skill Browser (26 domains × 942 skills), Team Composer (save to .claude/agents/teams/).

**Agent Craft tab** (enhanced, commit `1f22e496`):
- Create form: name/model/maxTurns/description/tools/mcpServers/instructions → `POST /api/agents/crud`
- Edit/Delete with protected agents guard (`cybersec-agent`, `AGENT_FACTORY`)
- **Factory Mode** (`<details>` collapsible):
  - Type selector: `specialist` / `orchestrator` / `team`
  - Model + MaxTurns
  - Template checkboxes: loaded from `GET /api/settings/agent-templates` → 31 templates from `.claude/agents/templates/*.md`
  - Research checkboxes: MITRE ATT&CK · CVE Database · Tool Docs · API Reference
  - Toggles: Include project context · Save to .claude/agents/
  - Extra instructions textarea
  - Generate button → `afGenerate()` → `POST /api/agents/generate`
  - Preview `<pre>` shows generated markdown

**Workflows tab**: Step builder → POST /api/workflows. Topological execution with `{{step_id}}` interpolation.

**renderTable() pattern**: `renderTable(containerId, schema, rows)` — schema: `{key, label, type}` where type = string|number|bool|datetime|json.

**Known DB model skips**: `db.models.forensic` (SessionPhase.INIT missing) · `db.models.yara_rule` (YaraRuleSource.IOC_DERIVED missing) — `_schema.py` silently skips on import error.

### .claude/ system
| Component   | Summary                                                                                                                                                                                                                         |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `agents/`   | 48 agents: 37 main specialists + 3 team modes (blue/red/purple) + 8 sub-agents · model tiers: Haiku, Sonnet, Opus                                                                                                               |
| `hooks/`    | 32 .py files: 10 settings.json-wired + 12 custom event handlers (via `emit()`) + 10 utility modules                                                                                                                             |
| `commands/` | **DISSOLVED** — all 8 converted to SKILL.md entries (see skills/)                                                                                                                                                               |
| `skills/`   | 942 SKILL.md across 26 domains — includes 8 former commands (forensics/hunting/apt-hunt, forensics/browser/hunt, forensics/memory/dump, forensics/network/apt-hunt, ops/mode-switch, ops/setup, ops/test-config, ops/team-task) |

**Two execution paths** — NEVER conflate:
- **Agent SDK** (internal): `query()` → `http://localhost:8000/v1` → 63 MCP tools (36 in-process + 27 omniroute stdio)
- **A2A Protocol** (external): `POST /a2a` JSON-RPC → `CybersecA2AAgent` → `run_agent_query()` → SDK → Proxy

**mcp.json servers**: `cybersec` (31 tools, `python -m csmcp.cybersec.server`) · `dystopian-crypto` (5 tools) · `omniroute` (27 tools, bun, self-contained at `src/omniroute_mcp/server.ts`) · `kerneldev` (external)

---

## Stack & Conventions

- **Python 3.14** · **`uv`** — never `pip install`
- **Tortoise ORM** + PostgreSQL (asyncpg) — `localhost:5432/cybersec_forensics`
- **Starlette ASGI** + uvicorn port 8000
- **Pydantic v2** · **claude-agent-sdk** @ v0.1.61
- **Subagents CANNOT call subagents** — never `"Agent"` in `AgentDefinition.tools`
- SSL certs: `~/.omniroute/certs/` · Keys: `/etc/dystopian/crypto/cert/private`

**MCP tool pattern**:
```python
@tool("name", "desc", {"param": {"type": "string"}})
async def _fn(args: dict) -> dict:
    return sdk_result({"key": value})
```

---

## Investigation Phases

| Phase | Name               | Agent                   |
|-------|--------------------|-------------------------|
| 0     | Case Opening       | cybersec-agent          |
| 1     | Reconnaissance     | cybersec-agent          |
| 2     | Deep Scan          | filesystem-analyst      |
| 3     | Network Analysis   | network-analyst         |
| 4     | Persistence Hunt   | persistence-analyst     |
| 5     | Memory Forensics   | memory-analyst          |
| 6     | IOC Correlation    | cybersec-analyst        |
| 7     | Threat Attribution | threat-modeler          |
| 8     | Artifact Signing   | cybersec-agent (crypto) |

---

## NIST Fixtures (`data/fixtures/`)

- **nist_csf_2.json** — 185 subcategories, 6 functions (GV/ID/PR/DE/RS/RC). Model: `NistCsfControl`. CLI: `seed-nist-csf`.
- **nist_ai_rmf.json** — 72 subcategories, 4 functions (Govern/Map/Measure/Manage). Model: `NistAiRmfControl`. CLI: `seed-nist-ai-rmf`.
- **DB fixtures** (7): mitre_techniques, mitre_actors, mitre_software, cwe_entries, capec_entries, cve_entries (68 CVEs, 2014-2025), poc_entries
- **Live seed commands** (httpx, NVD v2 — commit `21f6cd96`):
  - `seed-nvd-cves` — NVD API v2 (2000/page), `--severity CRITICAL|HIGH|MEDIUM|LOW`, `--max N`, `--start-year`, `--incremental`, `--api-key`
  - `seed-cwe` — all CWEs from MITRE JSON (httpx)
  - `seed-capec` — all CAPECs from MITRE (httpx)
  - `seed-mitre` — live ATT&CK (techniques+actors+software from MITRE GitHub, httpx)
  - `seed-mitre-fixtures` — 30 canonical fixture entries only (replaces old duplicate)

---

## OmniRoute Integration ✅

**Status**: Self-contained server embedded in CyberSecSuite (session `69854c5c`).

- `src/omniroute_mcp/server.ts` — **fully self-contained** TypeScript MCP server (version `1.9.0`, ~1100 lines)
  - Zero cross-repo imports — no longer depends on sibling `../OmniRoute` repo
  - All OmniRoute helpers inlined: `resolveOmniRouteBaseUrl`, `normalizeQuotaResponse`, combo step helpers
  - Memory tools (3) → HTTP calls to `/api/memory/*`
  - Skill tools (4) → HTTP calls to `/api/skills/*`
  - Audit logger, scope enforcement, runtime heartbeat all inlined
  - 27 tools total: 9 essential + 11 advanced + 3 memory + 4 skills
- `src/omniroute_mcp/package.json` — deps: `@modelcontextprotocol/sdk`, `zod`, `better-sqlite3`
- `src/omniroute_mcp/tsconfig.json` — Bun-compatible (`moduleResolution: bundler`)
- `mcp.json`: `omniroute` entry now uses `cwd: ${workspaceFolder}/src/omniroute_mcp`, `args: ["run", "${workspaceFolder}/src/omniroute_mcp/server.ts"]`
- Tools: health, combos, routing, quota, cost, models, web_search, simulate_route, budget_guard, resilience, provider metrics, session snapshot, pricing sync, memory (3), skills (4), explain route, db health, and more
- `docs/configuration.md`: OmniRoute env vars + OpenSearch env vars added, port reference updated

### Architecture Audit (2026-04-19)

Full 7-layer architectural audit completed with corrected numbers:
- **Layer 1 (ASGI)**: 160-line asgi.py with mount map. AI proxy: 60 providers, 13 strategies, 855-line _providers.py
- **Layer 2 (MCP)**: 63 tools total (31 cybersec + 5 dystopian + 27 omniroute). SDK compat shim at `_sdk_compat.py`
- **Layer 3 (A2A + Agents)**: 48 agents. A2A JSON-RPC: 6 methods. 4 security hooks
- **Layer 4 (Database)**: 40+ models, 65 tables. Seeds: MITRE, NVD, CWE, CAPEC, NIST CSF 2.0, NIST AI RMF 1.0
- **Layer 5 (Dashboard)**: 41 endpoints (37 REST + 4 SSE). Ring-buffer metrics with p50/p95/p99
- **Layer 6 (Skills)**: 942 SKILL.md across 26 domains
- **Layer 7 (Hooks)**: 30 hook modules, 10 wired in settings.json

New documentation created:
- `docs/layer-integration.md`: 7-layer integration guide with ASCII diagrams, 12 integration points
- `docs/omniroute-mcp.md`: Complete 27-tool OmniRoute MCP reference
- `docs/architecture.md`: Full rewrite with accurate numbers and updated module map

---

## OpenSearch Integration ✅

**Status**: Complete. Committed `b216c970`.

| Index                                | Interval       | Source                                        |
|--------------------------------------|----------------|-----------------------------------------------|
| `cybersecsuite-telemetry-YYYY.MM.DD` | daily rollover | `MetricsStore.record()` dual-write            |
| `cybersecsuite-audit-YYYY.MM.DD`     | daily rollover | `migrate-audit` CLI: PG → OS → DROP TABLE     |
| `cybersecsuite-api-usage-YYYY.MM.DD` | daily rollover | `migrate-api-usage` CLI: PG → OS → DROP TABLE |

**Stack**: `opensearch-py[async]>=2.7` · single-node · security disabled · bulk writer 100 docs/5s flush · non-fatal try/except throughout

**Fast-forward**: `uv run python -m manage migrate-audit` (or `migrate-api-usage`) → batch fetch → bulk index → count verify → confirm prompt → DROP TABLE CASCADE

---

## Roadmap

### ✅ Phase P — Dashboard Context Header + Sidebar Recat + Agent Factory (2026-04-19)

| Sub  | What                                                                                                | Status |
|------|-----------------------------------------------------------------------------------------------------|--------|
| P.1  | Sidebar recategorized: 7 groups (PLATFORM/AI PROXY/AGENTS/OPERATIONS/FORENSICS/DATA/SETTINGS)       | ✅      |
| P.2  | Removed static stats header (providers/models/requests/tokens/cost/FREE/STD/PREMIUM)                | ✅      |
| P.3  | Context-aware header: `#context-bar` with per-tab stats fetched lazily, cached in `_ctxCache`       | ✅      |
| P.4  | Removed irrelevant tabs: Providers, Agent Registry, Factory (standalone)                            | ✅      |
| P.5  | Agent Craft factory UI: type selector, template checkboxes, research checkboxes, project ctx toggle | ✅      |
| P.6  | `GET /api/settings/agent-templates` — lists 31 templates from `.claude/agents/templates/`           | ✅      |
| P.7  | `POST /api/agents/generate` — deterministic factory: frontmatter + chapter body from FACTORY_VARS   | ✅      |
| P.8  | `afLoadTemplates()` + `afGenerate()` JS functions wired to factory UI                               | ✅      |
| P.9  | Fixed `context_bar()` CSS conflict (display:none wins, JS sets flex on demand)                      | ✅      |
| P.10 | Fixed `_panels.py` syntax error: missing closing `)` on `_agent_craft()`, `_workflows()` was merged | ✅      |
| P.11 | Fixed JS init: activates `tab-health` not removed `tab-providers`                                   | ✅      |

**Commits**: `28e9666e` (palette/sidebar) → `1f22e496` (factory UI/API/context bar fix)
**Tests**: 87 passed, 23 skipped — no regressions
**Pending**: `AGENT_FACTORY.md` deterministic rewrite (structured FACTORY_VARS JSON input, strict chapter pipeline)

---

### ✅ Phase N (Remaining) — Completed (2026-04-19)

#### N.4 — Test Coverage ✅
- Rewrote `test_ai_proxy.py` → real `RateLimiter`/`UsageTracker` API, skipped `CircuitBreaker` (not implemented)
- Rewrote `test_telemetry.py` → `TelemetryEvent(name=, value=, labels=)`, async `record_event`/`get_snapshot`, `MetricsStore` direct tests
- Fixed `test_poc_model.py` → removed `autouse=True`, `@pytest.mark.anyio`, `skipif` Python ≥3.14
- Result: **62 passed, 25 skipped, 0 failures** (commits `41d759f1`)

#### N.5 — MEMORY.md Sync ✅
- Agents: 45 total (34 main + 11 sub-agents)
- Skills: 985 SKILL.md files across 24+ domains
- MCP tools: 36 total (31 cybersec + 5 dystopian-crypto)

#### N.6 — pyproject.toml Cleanup ✅
- Removed `pytest>=9.0.2` from `[dependencies]` (already in `[dependency-groups.test]`)
- Removed `claude>=0.4.11` (wrong package — we use `claude-agent-sdk`)
- Removed `tortoise>=0.1.1` (wrong package — we use `tortoise-orm[asyncpg]`)
- Bumped test dep `pytest>=8.3` → `pytest>=9.0`
- `uv lock` removed 3 stale packages (`atlastk`, `claude`, `tortoise`)

#### N.1 — Pending Changes (deferred)
- Some untracked files (`.github/`, `.memory/`) exist but are non-blocking

#### N.2 — browser_profiles.py (deferred)
- File exists but needs hardening (context manager, type hints, tests)

#### N.3 — Sub-Agent Quality Gate (deferred)
- Review/align 11 sub-agent `.md` files, update `docs/agents.md`

---

### ✅ Phase O — A2A Simplification + SDK Direct Routing (2026-04-19)

> Redundante Python-Agent-Wrappers entfernt. SDK liest `.claude/agents/*.md` direkt, per-agent Model-Routing durch AI Proxy.

| Sub | What                                                                        | Status |
|-----|-----------------------------------------------------------------------------|--------|
| O.1 | Delete `orchestrator.py` + `dev_agents.py`, clean `__init__.py` + `asgi.py` | ✅      |
| O.2 | `_handle_generic()` fallback in `cybersec_agent.py`                         | ✅      |
| O.3 | Per-agent model routing (`AgentDefinition.model` → `options.model` → Proxy) | ✅      |
| O.4 | `_copy_options_with()` — shallow-copy before mutation (race fix)            | ✅      |
| O.5 | OmniRoute 27 tools embedded as self-contained src/omniroute_mcp/            | ✅      |
| O.6 | Docs: `docs/agent-sdk-integration.md`, `README.md`, `architecture.md`       | ✅      |
| O.7 | Stale references cleaned: hooks, `hooks.json`, `CLAUDE.md`, `scope.md`      | ✅      |

**Commit**: `ae723c1d` — 25 files, +1521/−972

**Architecture (simplified)**:
```
.claude/agents/*.md → agent_loader → agent_sdk → AI Proxy → 60 providers
                        ↑ model: from frontmatter
```

---

### ✅ Phase N — A2A ↔ Agent SDK Integration Fixes (2026-04-19)

> 7 konkrete Defekte behoben. Alle Änderungen in `src/a2a/`.

| # | Defekt                                                                   | Fix                                                                                                 | Datei                               |
|---|--------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|-------------------------------------|
| 1 | `build_agent_options()` liest alle `.md` + MCP-Init bei jedem Aufruf neu | Module-level `_OPTIONS_CACHE` + `_AGENT_DEFS_CACHE`; `clear_caches()` für Tests                     | `agent_sdk.py`                      |
| 2 | `run_agent_query()`: fragile `"Use the X agent to: Y"` Dispatch          | `AgentDefinition.prompt` als `[AGENT CONTEXT]...[/AGENT CONTEXT]` Block im Prompt — deterministisch | `agent_sdk.py`                      |
| 3 | SDK `session_id` nie zurück zu `Task.session_id` propagiert              | `_session_out: dict` Parameter; alle Skill-Handler schreiben `task.session_id` nach Aufruf          | `agent_sdk.py`, `cybersec_agent.py` |
| 4 | `BaseA2AAgent.stream()` blockiert, gibt nur einen Chunk                  | Zuerst `TaskState.WORKING` yielden, dann finalen Zustand                                            | `agent.py`                          |
| 5 | `_extract_text()` in 3 Klassen dupliziert                                | `@staticmethod` auf `BaseA2AAgent`; Subklassen-Duplikate entfernt                                   | `agent.py`, `cybersec_agent.py`     |
| 6 | Beliebiges `[:500]`-Truncation in allen Handlern                         | Truncation vollständig entfernt                                                                     | `cybersec_agent.py`                 |
| 7 | `PythonDeveloperAgent`/`CppDeveloperAgent` kein `try/except`             | Beide `execute()` in `try/except → _fail()` gewrappt                                                | `dev_agents.py`                     |

**Geänderte Dateien**:
- `src/a2a/agent_sdk.py` — Caching, `_session_out`, `[AGENT CONTEXT]`-Dispatch, `clear_caches()`
- `src/a2a/agent.py` — `_extract_text()` auf BaseClass, WORKING-Signal
- `src/a2a/cybersec_agent.py` — Session-Threading in allen 4 Handlern, kein Truncation, `Any` import
- `src/a2a/dev_agents.py` — try/except, session threading, `_get_text` → `_extract_text`
- `src/a2a/__init__.py` — `build_agent_definitions`, `clear_caches` exportiert

---


- Phases 0–7, A–M.1: config, seeds, skills taxonomy, MCP split (36 tools), A2A wiring, telemetry, PoC model, linting (0 ruff errors), hooks wiring (10), agent-sdk migration, `dashboard/api/` package split
- Phase K.1 — `renderTable()` JS component + Explorer tab
- Phase K.2 — Cases/Tasks/PoCs converted to renderTable
- Phase K.3 — Providers/Usage/Crypto/A2A converted to renderTable
- Phase K.4 — 7 new forensic tabs: Findings/IOCs/YARA/Network/Intel/Audit/Compliance
- Phase K.5 — Agent Query panel: agent selector, context enrichment, conversation history
- Phase K.6 — Split `_html.py` (1194L) → `templates/` package: `_components.py`, `_base.py`, `_tabs.py`, `_panels.py`, `_js.py`; `.stat-card` CSS added
- Phase K.7 — Settings tab: `GET/PATCH /api/settings`, editable env/agent/proxy fields, hooks read-only view
- Phase K.8 — Team Builder tab: Agent Browser (48 agents), Skill Browser (942 skills/26 domains), Team Composer (phase→agent JSON)
- Phase G — SSE frontend wiring: `initSSE()` wires 4 EventSource streams; `refresh()` 22→19 endpoints; Telemetry tab (26th) with p50/p95/p99/rps table
- **OpenSearch integration** ✅ — `src/opensearch/` package (client, indices, buffered writer); docker-compose services (9200/5601); telemetry dual-write; `migrate-audit`/`migrate-api-usage` CLI commands; 27th dashboard tab with cluster health + index stats
- **Infrastructure fixes** ✅ (commit `21f6cd96`) — Docker PG socket `/tmp`; `bootstrap.py` always passes port; `session_start.py` reads `.claude/settings.json`; all seed files migrated `aiohttp`→`httpx`; NVD API v1 (retired)→v2 with `--severity` filter + 2000/page; removed `aiohttp` from pyproject.toml; fixed duplicate `seed_mitre_command` → `seed_mitre_fixtures_command`
- **Hook fixes** ✅ (commit `68b40f5d`) — `user_prompt_submit.py`: fixed `audit()` called with 2 args (accepts 1 dict), added proper stdin JSON guard, emit context when mode/phase available; `termmate_idle.py`: catch `(json.JSONDecodeError, ValueError, EOFError)` not just `TypeError`; `hooks.json`: fixed stale paths missing `src/` prefix
- **OmniRoute MCP** ✅ (commit `7519585b`) — self-contained at `src/omniroute_mcp/server.ts` (27 tools, bun stdio); `docs/omniroute-mcp.md` reference
- **Skills asset sync** ✅ (commit `cff9518d`) — INDEX.md: 933→942 skills, 25→26 domains; devices/ domain added; forensics/+4, ops/+4; MAPPER.md counts updated
- **Docs sweep** ✅ — README: 15-tab→27-tab, 933→942 skills, 11 hooks; architecture.md: OpenSearch in diagram + ports table; deployment.md: 5 services + ports; mcp-tools.md: 34→65 tools + OmniRoute section; quickstart.md: tool counts; MEMORY.md synced
- Commands audit — dissolved `commands/` into 8 SKILL.md entries in `skills/`
- Ruff clean — `exclude = [".claude"]` added to pyproject.toml; `src/` + `tests/` → 0 errors
- **Fixture caching** ✅ (commit `3659b80e`) — `cwe_full.py`, `capec_full.py`, `mitre_full.py`, `nvd.py` all cache to `data/fixtures/*.json`; NIST fixtures moved to `src/db/fixtures/` (committed); `seed_poc()` loads from `poc_entries.json`; fixed all 3 broken model imports (CWE→CWEIntel, CAPEC→CapecAttackPatternIntel, MITRE*→Mitre*Intel)
- **ACP agent** ✅ (commit `1c11f50a`) — `src/acp_agent/` package, JSON-RPC 2.0 over stdio, ACP protocol for JetBrains AI Assistant; `~/.jetbrains/acp.json` configured
- CVE fixture — expanded from 30 → 68 entries (DirtyCOW, SMBGhost, PwnKit, Log4Shell variants, RegreSSHion, etc.)
- `BrowserForensicFinding` model — created `db/models/browser_forensic.py` (table `browser_forensic_findings`), registered in MODEL_MODULES, fixed `datetime.utcnow()` → `datetime.now(timezone.utc)`, fixed `.annotate()` dict access via `.values()`

### ✅ Phase K — Complete (25-tab dashboard)

### ✅ Phase M.4 — `_commands.py` fixes (commit `10f6420d`)
- Added `seed_all_command()` — chains all fixture-based seeds (NIST CSF, AI RMF, MITRE, CWE, CAPEC, PoC); wired as `"seed-all"` in `manage.py`
- Fixed `migrate_api_usage_command`: uncommented `execute_script(DROP TABLE IF EXISTS api_usage_log CASCADE)` — was dead code with false ✅ message
- Removed `_print_intel_components()` dead code (never called)
- `session_start.py` was already wired in `settings.json` SessionStart

### ✅ src-layout import fix (commit `c4faae08`)
- `pyproject.toml`: `packages = ["src"]` → explicit list `["src/a2a", "src/agent", ...]`
  so hatchling editable install writes `src/` (not project root) to `.pth`
- `manage/__init__.py`: moved all CLI logic here (imports, show_usage, main, _run_main, main_sync) using relative `._commands` imports
- `manage/__main__.py`: new 5-line entry point — `python -m manage` now works
- `manage.py`: slimmed to 17-line shim; `python src/manage.py` still works
- `cybersecsuite` installed script (`manage:main_sync`) now resolves correctly

---

## ACP Agent (JetBrains AI Assistant) ✅

**Status**: Complete (commit `1c11f50a`). Registered in `~/.jetbrains/acp.json`.

**Module**: `src/acp_agent/` — JSON-RPC 2.0 over stdio with Content-Length framing (LSP-style)

| File                        | Purpose                                                            |
|-----------------------------|--------------------------------------------------------------------|
| `src/acp_agent/__init__.py` | Package marker                                                     |
| `src/acp_agent/__main__.py` | Entry: `python -m acp_agent`                                       |
| `src/acp_agent/server.py`   | Full ACP protocol server — initialize, session/new, session/prompt |

**ACP methods implemented**:
- `initialize` → returns protocol version + capabilities
- `session/new` → creates UUID session, returns `sessionId`
- `session/prompt` → streams `session/update` notifications + final `PromptResponse`

**Bridges to**: `CYBERSEC_PROXY_URL` (default `http://localhost:8000/v1`) via httpx streaming

**Entry point**: `cybersec-acp = "acp_agent.server:main"` in pyproject.toml scripts

**`~/.jetbrains/acp.json`**:
```json
{
  "default_mcp_settings": { "use_custom_mcp": true, "use_idea_mcp": true },
  "agent_servers": {
    "CyberSecSuite": {
      "command": "/usr/bin/uv",
      "args": ["run", "--project", "/home/daen/Projects/cybersecsuite", "python", "-m", "acp_agent"],
      "env": { "CYBERSEC_PROXY_URL": "http://localhost:8000/v1", "CYBERSEC_MODEL": "claude-sonnet-4-5" }
    }
  }
}
```

**To use in JetBrains**: Settings → AI Assistant → Agents → refresh list → select "CyberSecSuite"

---

## HTTP Client Convention

**httpx throughout** — `aiohttp` removed from pyproject.toml (commit `21f6cd96`).
- Seeds: `httpx.AsyncClient(timeout=60.0)` · `resp.status_code` · `resp.json()`
- Proxy executor + A2A client: persistent `httpx.AsyncClient`
- Rate delay for NVD: 6.5s without API key · 0.6s with key (50 req/30s)

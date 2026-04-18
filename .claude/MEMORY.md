# CyberSecSuite — MEMORY.md

_Last updated: 2026-04-18_

## Architecture

```
Claude Code / agent_sdk.py
        │  ANTHROPIC_BASE_URL=http://localhost:8000/v1
        ▼
  ASGI /v1/*  (AI Proxy — 60 providers, 13 strategies, cost-optimized default)
        │
  ┌─────┴──────┐
  │ /dashboard | SPA + 36 REST + 4 SSE routes
  │ /a2a       | A2A JSON-RPC → OrchestratorAgent → 33 sub-agents
  │ /health    | DB health (200/503)
  └────────────┘
  MCP (stdio): cybersec (31 tools) + dystopian-crypto (5 tools) = 36 total
```

**Ports**: 8000 ASGI ✅ · 5432 PostgreSQL ✅ · 6379 Redis ✅ · 9200 OpenSearch ✅ · 5601 OS Dashboards ✅ · 8080 alt ⚠️ · 8433 TLS ⚠️

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
| `db/`                     | 45 model files, 83 Tortoise ORM model classes, `cybersec_forensics` DB                                         |
| `db/browser_forensics.py` | `BrowserForensicFinding` CRUD — `log_finding_async()`, `count_findings_by_severity()`, `get_recent_findings()` |
| `checks/`                 | Integrity checks — FK, fixtures, config paths                                                                  |
| `telemetry/`              | Ring-buffer metrics, p50/p95/p99, ASGI middleware, SSE collector — dual-write to OpenSearch ✅    |
| `opensearch/`             | Async client singleton, index templates (telemetry/audit/api-usage), buffered bulk writer (100 docs/5s) |

**src/csmcp/ rename**: `src/mcp/` → `src/csmcp/` (Phase H) — avoided naming conflict with pip `mcp` v1.26.0. `mcp_server.py` (1288L FastMCP) DELETED.

### src/dashboard/ (41 routes)
| File                       | Lines | Purpose                                                                                                |
|----------------------------|-------|--------------------------------------------------------------------------------------------------------|
| `routes.py`                | 68    | Route wiring                                                                                           |
| `_html.py`                 | 4     | Shim — imports `build_dashboard_html()` from `templates/`                                              |
| `templates/__init__.py`    | 25    | `build_dashboard_html()` assembler                                                                     |
| `templates/_components.py` | 71    | `stat_card`, `mini_card`, `stat_grid`, `tab_panel`, `simple_panel`, `section_h3/h4`, `table_slot`      |
| `templates/_base.py`       | 86    | CSS (+ `.stat-card` rules), `head()`, `header()`, `stats_row()`, `tiers_row()`                         |
| `templates/_tabs.py`       | 46    | `tab_bar()` — 27 tab items as a list                                                                   |
| `templates/_panels.py`     | 415   | `all_panels()` — 27 panel fns using components                                                         |
| `templates/_js.py`         | 1215  | `_JS` — SSE wiring (initSSE, 4 EventSource) + team builder + settings CRUD + explorer + agent query JS + OpenSearch |
| `api/core.py`              | 153   | overview, providers, usage, health, crypto                                                             |
| `api/agents.py`            | 215   | a2a, agents, routing, factory, agent-query                                                             |
| `api/forensic.py`          | 396   | findings, iocs, yara, network, intel, audit, compliance, NIST                                          |
| `api/ops.py`               | 183   | cases, tasks, task lifecycle, PoCs                                                                     |
| `api/tables.py`            | 148   | db counts, investigations, models, generic table, prompts, telemetry                                   |
| `api/settings.py`          | 55    | `GET/PATCH /api/settings` — editable: env/agent/proxy/asgi/cache/security/hooks_dir                    |
| `api/team_builder.py`      | 130   | `GET /api/team-agents` (33 agents) · `GET /api/skills?domain=&q=` (941 skills) · `GET /api/teams`      |
| `api/opensearch_stats.py`  | 47    | `GET /api/opensearch` — cluster health + per-index doc count/size                                      |
| `api/sse.py`               | 153   | /sse/cases · /sse/tasks · /sse/health · /sse/telemetry                                                 |
| `_schema.py`               | 149   | Tortoise model introspector — 83 models                                                                |

**27 tabs**: Providers · Usage & Cost · Agents · Routing · Factory · Prompts · Health · Crypto · A2A · Investigations · DB Counts · Cases · Tasks · PoCs · Findings · IOCs · YARA · Network · Intel · Audit · Compliance · Agent Query · Settings · Team Builder · Telemetry · **OpenSearch** · Explorer

**Key endpoints**: `GET /api/models` · `GET /api/tables/{model}` · `POST /api/agent-query` · `GET /api/settings` · `PATCH /api/settings` · `GET /api/team-agents` · `GET /api/skills` · `GET /api/teams` · `GET /api/opensearch`

**Team Builder tab**: Agent Browser (filterable table of 33 agents), Skill Browser (27 domains × 941 skills, domain select + search), Team Composer (add phases → assign agents → generate/copy JSON).

**Settings tab**: Agent & Proxy (editable), Env Variables (add/remove/save rows), Hooks (read-only renderTable). PATCH validates against editable/readonly key sets — forbidden keys → 400.

**OpenSearch tab**: Cluster health badge (green/yellow/red), node/shard counts, total docs. Index table showing all `cybersecsuite-*` indices with doc count + size in MB. `loadOpenSearch()` fetches `GET /api/opensearch`. Refresh button.

**renderTable() pattern**: `renderTable(containerId, schema, rows)` — schema: `{key, label, type}` where type = string|number|bool|datetime|json. Pre-format badge HTML as strings before passing.

**Known DB model skips**: `db.models.forensic` (SessionPhase.INIT missing) · `db.models.yara_rule` (YaraRuleSource.IOC_DERIVED missing) — `_schema.py` silently skips on import error.

### .claude/ system
| Component   | Summary                                                                                                                                                                                                                         |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `agents/`   | 34 agents: 33 specialists + AGENT_FACTORY · teams/: blue/red/purple · model tiers: Haiku (3), Sonnet (28), Opus (3)                                                                                                             |
| `hooks/`    | 32 .py files: 10 settings.json-wired + 12 custom event handlers (via `emit()`) + 10 utility modules                                                                                                                             |
| `commands/` | **DISSOLVED** — all 8 converted to SKILL.md entries (see skills/)                                                                                                                                                               |
| `skills/`   | 941 SKILL.md across 26 domains — includes 8 former commands (forensics/hunting/apt-hunt, forensics/browser/hunt, forensics/memory/dump, forensics/network/apt-hunt, ops/mode-switch, ops/setup, ops/test-config, ops/team-task) |

**Two execution paths** — NEVER conflate:
- **Agent SDK** (internal): `query()` → `http://localhost:8000/v1` → 36 MCP tools
- **A2A Protocol** (external): `POST /a2a` JSON-RPC → OrchestratorAgent → `execute()`

**mcp.json servers**: `cybersec` (31 tools, `python -m csmcp.cybersec.server`) · `dystopian-crypto` (5 tools) · `kerneldev` (external)

---

## Stack & Conventions

- **Python 3.14** · **`uv`** — never `pip install`
- **Tortoise ORM** + PostgreSQL (asyncpg) — `localhost:5432/cybersec_forensics`
- **Starlette ASGI** + uvicorn port 8000
- **Pydantic v2** · **claude-agent-sdk** @ v0.1.61
- **Subagents CANNOT call subagents** — never `"Agent"` in `AgentDefinition.tools`
- SSL certs: `~/.omniroute/certs/` · Keys: `/etc/dystopian-crypto/keys`

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

## OmniRoute Integration

**PENDING** (`omniroute-integrate`). External MCP at `/home/daen/Projects/OmniRoute/open-sse/mcp-server/` — 19 tools (`omniroute_*`). Register in `mcp.json`. Env: `OMNIROUTE_API_KEY`, `OMNIROUTE_BASE_URL=http://localhost:8888`.

---

## OpenSearch Integration ✅

**Status**: Complete. Committed `b216c970`.

| Index                                | Interval       | Source                                       |
|--------------------------------------|----------------|----------------------------------------------|
| `cybersecsuite-telemetry-YYYY.MM.DD` | daily rollover | `MetricsStore.record()` dual-write           |
| `cybersecsuite-audit-YYYY.MM.DD`     | daily rollover | `migrate-audit` CLI: PG → OS → DROP TABLE    |
| `cybersecsuite-api-usage-YYYY.MM.DD` | daily rollover | `migrate-api-usage` CLI: PG → OS → DROP TABLE |

**Stack**: `opensearch-py[async]>=2.7` · single-node · security disabled · bulk writer 100 docs/5s flush · non-fatal try/except throughout

**Fast-forward**: `uv run python -m manage migrate-audit` (or `migrate-api-usage`) → batch fetch → bulk index → count verify → confirm prompt → DROP TABLE CASCADE

---

## Roadmap

### ✅ Done
- Phases 0–7, A–M.1: config, seeds, skills taxonomy, MCP split (36 tools), A2A wiring, telemetry, PoC model, linting (0 ruff errors), hooks wiring (10), agent-sdk migration, `dashboard/api/` package split
- Phase K.1 — `renderTable()` JS component + Explorer tab
- Phase K.2 — Cases/Tasks/PoCs converted to renderTable
- Phase K.3 — Providers/Usage/Crypto/A2A converted to renderTable
- Phase K.4 — 7 new forensic tabs: Findings/IOCs/YARA/Network/Intel/Audit/Compliance
- Phase K.5 — Agent Query panel: agent selector, context enrichment, conversation history
- Phase K.6 — Split `_html.py` (1194L) → `templates/` package: `_components.py`, `_base.py`, `_tabs.py`, `_panels.py`, `_js.py`; `.stat-card` CSS added
- Phase K.7 — Settings tab: `GET/PATCH /api/settings`, editable env/agent/proxy fields, hooks read-only view
- Phase K.8 — Team Builder tab: Agent Browser (33 agents), Skill Browser (941 skills/27 domains), Team Composer (phase→agent JSON)
- Phase G — SSE frontend wiring: `initSSE()` wires 4 EventSource streams; `refresh()` 22→19 endpoints; Telemetry tab (26th) with p50/p95/p99/rps table
- **OpenSearch integration** ✅ — `src/opensearch/` package (client, indices, buffered writer); docker-compose services (9200/5601); telemetry dual-write; `migrate-audit`/`migrate-api-usage` CLI commands; 27th dashboard tab with cluster health + index stats
- **Infrastructure fixes** ✅ (commit `21f6cd96`) — Docker PG socket `/tmp`; `bootstrap.py` always passes port; `session_start.py` reads `.claude/settings.json`; all seed files migrated `aiohttp`→`httpx`; NVD API v1 (retired)→v2 with `--severity` filter + 2000/page; removed `aiohttp` from pyproject.toml; fixed duplicate `seed_mitre_command` → `seed_mitre_fixtures_command`
- Commands audit — dissolved `commands/` into 8 SKILL.md entries in `skills/`
- Ruff clean — `exclude = [".claude"]` added to pyproject.toml; `src/` + `tests/` → 0 errors
- CVE fixture — expanded from 30 → 68 entries (DirtyCOW, SMBGhost, PwnKit, Log4Shell variants, RegreSSHion, etc.)
- `BrowserForensicFinding` model — created `db/models/browser_forensic.py` (table `browser_forensic_findings`), registered in MODEL_MODULES, fixed `datetime.utcnow()` → `datetime.now(timezone.utc)`, fixed `.annotate()` dict access via `.values()`

### ✅ Phase K — Complete (25-tab dashboard)

### Pending
- Phase E — Anthropic skills asset sync (copy LICENSE/scripts/refs/assets into .claude/skills/)
- Phase M.3 — consolidate `a2a/` and `checks/`
- Phase N — update all 10 docs + README
- OmniRoute integration (mcp.json + allowed_tools)

---

## HTTP Client Convention

**httpx throughout** — `aiohttp` removed from pyproject.toml (commit `21f6cd96`).
- Seeds: `httpx.AsyncClient(timeout=60.0)` · `resp.status_code` · `resp.json()`
- Proxy executor + A2A client: persistent `httpx.AsyncClient`
- Rate delay for NVD: 6.5s without API key · 0.6s with key (50 req/30s)

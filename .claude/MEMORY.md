# CyberSecSuite — MEMORY.md

_Last updated: 2026-04-19 (ACP agent + fixture caching complete)_

## Architecture

```
Claude Code / agent_sdk.py
        │  ANTHROPIC_BASE_URL=http://localhost:8000/v1
        ▼
  ASGI /v1/*  (AI Proxy — 60 providers, 13 strategies, cost-optimized default)
        │
  ┌─────┴──────┐
  │ /dashboard | SPA + 36 REST + 4 SSE routes
  │ /a2a       | A2A JSON-RPC → CybersecA2AAgent → SDK → .claude/agents/ → Proxy
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
| `a2a/checks/`             | Integrity checks — FK, fixtures, config paths (moved from `src/checks/` in Phase M.3, commit `4a52b219`)       |
| `telemetry/`              | Ring-buffer metrics, p50/p95/p99, ASGI middleware, SSE collector — dual-write to OpenSearch ✅                  |
| `opensearch/`             | Async client singleton, index templates (telemetry/audit/api-usage), buffered bulk writer (100 docs/5s)        |

**src/csmcp/ rename**: `src/mcp/` → `src/csmcp/` (Phase H) — avoided naming conflict with pip `mcp` v1.26.0. `mcp_server.py` (1288L FastMCP) DELETED.

### src/dashboard/ (41 routes)
| File                       | Lines | Purpose                                                                                                             |
|----------------------------|-------|---------------------------------------------------------------------------------------------------------------------|
| `routes.py`                | 68    | Route wiring                                                                                                        |
| `_html.py`                 | 4     | Shim — imports `build_dashboard_html()` from `templates/`                                                           |
| `templates/__init__.py`    | 25    | `build_dashboard_html()` assembler                                                                                  |
| `templates/_components.py` | 71    | `stat_card`, `mini_card`, `stat_grid`, `tab_panel`, `simple_panel`, `section_h3/h4`, `table_slot`                   |
| `templates/_base.py`       | 86    | CSS (+ `.stat-card` rules), `head()`, `header()`, `stats_row()`, `tiers_row()`                                      |
| `templates/_tabs.py`       | 46    | `tab_bar()` — 27 tab items as a list                                                                                |
| `templates/_panels.py`     | 415   | `all_panels()` — 27 panel fns using components                                                                      |
| `templates/_js.py`         | 1215  | `_JS` — SSE wiring (initSSE, 4 EventSource) + team builder + settings CRUD + explorer + agent query JS + OpenSearch |
| `api/core.py`              | 153   | overview, providers, usage, health, crypto                                                                          |
| `api/agents.py`            | 215   | a2a, agents, routing, factory, agent-query                                                                          |
| `api/forensic.py`          | 396   | findings, iocs, yara, network, intel, audit, compliance, NIST                                                       |
| `api/ops.py`               | 183   | cases, tasks, task lifecycle, PoCs                                                                                  |
| `api/tables.py`            | 148   | db counts, investigations, models, generic table, prompts, telemetry                                                |
| `api/settings.py`          | 55    | `GET/PATCH /api/settings` — editable: env/agent/proxy/asgi/cache/security/hooks_dir                                 |
| `api/team_builder.py`      | 130   | `GET /api/team-agents` (33 agents) · `GET /api/skills?domain=&q=` (941 skills) · `GET /api/teams`                   |
| `api/opensearch_stats.py`  | 47    | `GET /api/opensearch` — cluster health + per-index doc count/size                                                   |
| `api/sse.py`               | 153   | /sse/cases · /sse/tasks · /sse/health · /sse/telemetry                                                              |
| `_schema.py`               | 149   | Tortoise model introspector — 83 models                                                                             |

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
| `skills/`   | 942 SKILL.md across 26 domains — includes 8 former commands (forensics/hunting/apt-hunt, forensics/browser/hunt, forensics/memory/dump, forensics/network/apt-hunt, ops/mode-switch, ops/setup, ops/test-config, ops/team-task) |

**Two execution paths** — NEVER conflate:
- **Agent SDK** (internal): `query()` → `http://localhost:8000/v1` → 65 MCP tools (36 local + 29 omniroute)
- **A2A Protocol** (external): `POST /a2a` JSON-RPC → `CybersecA2AAgent` → `run_agent_query()` → SDK → Proxy

**mcp.json servers**: `cybersec` (31 tools, `python -m csmcp.cybersec.server`) · `dystopian-crypto` (5 tools) · `kerneldev` (external) · `omniroute` (29 tools, bun, port 20128)

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

## OmniRoute Integration ✅

**Status**: Complete (commit `2b633887`). 29 tools via `bun run server.ts`.

- `mcp.json`: registered `omniroute` server (bun, cwd=`../OmniRoute`, env `OMNIROUTE_BASE_URL=http://localhost:20128`)
- Tools: health, combos, routing, quota, cost, models, cache, memory (3), skills (4), explain route, db health
- `docs/configuration.md`: OmniRoute env vars + OpenSearch env vars added, port reference updated

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

### 🔴 Phase N — Pending (Next Session — 2026-04-19)

> **Status**: Uncommitted local changes exist. All items below need implementation + commit.

#### N.1 — Commit Pending Changes
- [ ] **`asgi.py` logging improvements** — `root_logger.getChild("asgi")`, structured log calls in `_on_startup`, `_on_shutdown`, `health` — already coded, needs `git add src/proxy/asgi.py && git commit`
- [ ] **`docker-compose.yml` security fix** — `OPENSEARCH_INITIAL_ADMIN_PASSWORD` placeholder changed to `change_me` — commit
- [ ] **`PROPOSAL_MEM.md` deletion** — file deleted, stage `git rm PROPOSAL_MEM.md`
- [ ] **New untracked files to stage and commit**:
  - `.claude/agents/sub_agents/python-developer.md`
  - `.claude/agents/sub_agents/python-code-reviewer.md`
  - `.claude/agents/sub_agents/watchdog.md`
  - `.claude/skills/devices/` (ssd/, usb/ domains)
  - `.github/` directory (workflows)
  - `.memory/` directory (audit.jsonl, root_commands.jsonl, violations.jsonl)
  - `src/db/browser_profiles.py` — BrowserCookiesDB ORM wrapper for Firefox/Chrome/Brave SQLite
  - `src/db/seeds/__init__.py`

#### N.2 — `src/db/browser_profiles.py` — Complete & Harden
- [ ] Add missing `"""` docstring opening line (file starts without triple-quote)
- [ ] Context manager (`with sqlite3.connect()`) instead of manual `conn.close()` — resource leak risk
- [ ] Add `BrowserHistoryDB`, `BrowserDownloadsDB` classes (Chrome/Firefox/Brave parity)
- [ ] Type hints throughout (PEP 484/526 mandatory)
- [ ] Wire into `db/models/__init__.py` or `db/__init__.py` — currently unregistered
- [ ] Write tests in `tests/test_browser_profiles.py`

#### N.3 — Sub-Agent Quality Gate
- [ ] Review `.claude/agents/sub_agents/python-developer.md` — align capabilities with mode instructions
- [ ] Review `.claude/agents/sub_agents/python-code-reviewer.md` — check review checklist completeness
- [ ] Review `.claude/agents/sub_agents/watchdog.md` — verify hook integration points
- [ ] Add new sub-agents to `MEMORY.md` agent count (currently: 34 agents total)
- [ ] Update `docs/agents.md` with new sub-agent entries

#### N.4 — Test Coverage Gate (Current: ~19% pass rate)
- [ ] Fix 34 failing DB async tests — need PostgreSQL running or proper mocking in conftest.py
- [ ] Fix 4 ERROR tests in `test_ai_proxy.py` — `ComboRouter` export missing
- [ ] Un-skip crypto tests — `KeyManager` and `ArtifactManager` APIs now stable
- [ ] Un-skip Agent SDK tests — `AgentRunner`, `SessionRecord` now available
- [ ] Add `tests/test_browser_profiles.py` — cover `BrowserCookiesDB` happy path + errors
- [ ] Target: ≥60% coverage gate via `uv run --group test pytest --cov=src --cov-report=term-missing`

#### N.5 — MEMORY.md Sync
- [ ] Update agent count (34 → check actual after N.3)
- [ ] Update skills count after new `devices/` domain (942 → verify)
- [ ] Update MCP tool count if new tools added
- [ ] Update `_Last updated_` timestamp after N.1 commit

#### N.6 — pyproject.toml Cleanup
- [ ] Move `pytest>=9.0.2` from `[dependencies]` to `[dependency-groups.test]` — currently in wrong section
- [ ] Verify `claude>=0.4.11` and `tortoise>=0.1.1` in `[dependencies]` are not duplicates
- [ ] Run `uv lock` after cleanup

---

### ✅ Phase O — A2A Simplification + SDK Direct Routing (2026-04-19)

> Redundante Python-Agent-Wrappers entfernt. SDK liest `.claude/agents/*.md` direkt, per-agent Model-Routing durch AI Proxy.

| Sub | What | Status |
|-----|------|--------|
| O.1 | Delete `orchestrator.py` + `dev_agents.py`, clean `__init__.py` + `asgi.py` | ✅ |
| O.2 | `_handle_generic()` fallback in `cybersec_agent.py` | ✅ |
| O.3 | Per-agent model routing (`AgentDefinition.model` → `options.model` → Proxy) | ✅ |
| O.4 | `_copy_options_with()` — shallow-copy before mutation (race fix) | ✅ |
| O.5 | OmniRoute 29 tools included via `all_servers()` — confirmed | ✅ |
| O.6 | Docs: `docs/agent-sdk-integration.md`, `README.md`, `architecture.md` | ✅ |
| O.7 | Stale references cleaned: hooks, `hooks.json`, `CLAUDE.md`, `scope.md` | ✅ |

**Commit**: `ae723c1d` — 25 files, +1521/−972

**Architecture (simplified)**:
```
.claude/agents/*.md → agent_loader → agent_sdk → AI Proxy → 60 providers
                        ↑ model: from frontmatter
```

---

### ✅ Phase N — A2A ↔ Agent SDK Integration Fixes (2026-04-19)

> 7 konkrete Defekte behoben. Alle Änderungen in `src/a2a/`.

| # | Defekt | Fix | Datei |
|---|--------|-----|-------|
| 1 | `build_agent_options()` liest alle `.md` + MCP-Init bei jedem Aufruf neu | Module-level `_OPTIONS_CACHE` + `_AGENT_DEFS_CACHE`; `clear_caches()` für Tests | `agent_sdk.py` |
| 2 | `run_agent_query()`: fragile `"Use the X agent to: Y"` Dispatch | `AgentDefinition.prompt` als `[AGENT CONTEXT]...[/AGENT CONTEXT]` Block im Prompt — deterministisch | `agent_sdk.py` |
| 3 | SDK `session_id` nie zurück zu `Task.session_id` propagiert | `_session_out: dict` Parameter; alle Skill-Handler schreiben `task.session_id` nach Aufruf | `agent_sdk.py`, `cybersec_agent.py` |
| 4 | `BaseA2AAgent.stream()` blockiert, gibt nur einen Chunk | Zuerst `TaskState.WORKING` yielden, dann finalen Zustand | `agent.py` |
| 5 | `_extract_text()` in 3 Klassen dupliziert | `@staticmethod` auf `BaseA2AAgent`; Subklassen-Duplikate entfernt | `agent.py`, `cybersec_agent.py` |
| 6 | Beliebiges `[:500]`-Truncation in allen Handlern | Truncation vollständig entfernt | `cybersec_agent.py` |
| 7 | `PythonDeveloperAgent`/`CppDeveloperAgent` kein `try/except` | Beide `execute()` in `try/except → _fail()` gewrappt | `dev_agents.py` |

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
- Phase K.8 — Team Builder tab: Agent Browser (33 agents), Skill Browser (941 skills/27 domains), Team Composer (phase→agent JSON)
- Phase G — SSE frontend wiring: `initSSE()` wires 4 EventSource streams; `refresh()` 22→19 endpoints; Telemetry tab (26th) with p50/p95/p99/rps table
- **OpenSearch integration** ✅ — `src/opensearch/` package (client, indices, buffered writer); docker-compose services (9200/5601); telemetry dual-write; `migrate-audit`/`migrate-api-usage` CLI commands; 27th dashboard tab with cluster health + index stats
- **Infrastructure fixes** ✅ (commit `21f6cd96`) — Docker PG socket `/tmp`; `bootstrap.py` always passes port; `session_start.py` reads `.claude/settings.json`; all seed files migrated `aiohttp`→`httpx`; NVD API v1 (retired)→v2 with `--severity` filter + 2000/page; removed `aiohttp` from pyproject.toml; fixed duplicate `seed_mitre_command` → `seed_mitre_fixtures_command`
- **Hook fixes** ✅ (commit `68b40f5d`) — `user_prompt_submit.py`: fixed `audit()` called with 2 args (accepts 1 dict), added proper stdin JSON guard, emit context when mode/phase available; `termmate_idle.py`: catch `(json.JSONDecodeError, ValueError, EOFError)` not just `TypeError`; `hooks.json`: fixed stale paths missing `src/` prefix
- **OmniRoute MCP** ✅ (commit `2b633887`) — `mcp.json` `omniroute` server (29 tools, bun, port 20128); `docs/configuration.md` env vars + port table
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

| File                        | Purpose                                                      |
|-----------------------------|--------------------------------------------------------------|
| `src/acp_agent/__init__.py` | Package marker                                               |
| `src/acp_agent/__main__.py` | Entry: `python -m acp_agent`                                 |
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

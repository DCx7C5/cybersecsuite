# CyberSecSuite — MEMORY.md

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

**Ports**: 8000 ASGI ✅ · 5432 PostgreSQL ✅ · 8080 alt ⚠️ · 8433 TLS ⚠️

**settings.json key values**: `agent: cybersec-agent` · `default_strategy: cost-optimized` · `hooks_dir: src/hooks/` · 10 workspace hooks (PreToolUse→PostCompact)

---

## Codebase Map

### src/ key files
| Path | Purpose |
|---|---|
| `proxy/asgi.py` | ASGI mount map, TelemetryMiddleware |
| `manage.py` | CLI dispatcher (`uv run python -m manage <cmd>`) |
| `csmcp/` | MCP package: `cybersec/` (31 tools, 8 submodules) + `dystopian.py` (5 tools) |
| `agent/` | AgentRunner, SessionManager, streaming, hooks (Phase H) |
| `a2a/` | A2A JSON-RPC server, orchestrator, agent_sdk bridge, registry |
| `ai_proxy/` | 60 providers (`registry.py` 1163L), routing (`combo.py` 574L), translators |
| `crypto/` | Ed25519, BLAKE2b-256, Argon2id (mem=262144, iters=4), AES-256-GCM |
| `db/` | 45 model files, 83 Tortoise ORM model classes, `cybersec_forensics` DB |
| `db/browser_forensics.py` | `BrowserForensicFinding` CRUD — `log_finding_async()`, `count_findings_by_severity()`, `get_recent_findings()` |
| `checks/` | Integrity checks — FK, fixtures, config paths |
| `telemetry/` | Ring-buffer metrics, p50/p95/p99, ASGI middleware, SSE collector |

**src/csmcp/ rename**: `src/mcp/` → `src/csmcp/` (Phase H) — avoided naming conflict with pip `mcp` v1.26.0. `mcp_server.py` (1288L FastMCP) DELETED.

### src/dashboard/ (36 routes)
| File | Lines | Purpose |
|---|---|---|
| `routes.py` | 63 | Route wiring |
| `_html.py` | 4 | Shim — imports `build_dashboard_html()` from `templates/` |
| `templates/__init__.py` | 25 | `build_dashboard_html()` assembler |
| `templates/_components.py` | 71 | `stat_card`, `mini_card`, `stat_grid`, `tab_panel`, `simple_panel`, `section_h3/h4`, `table_slot` |
| `templates/_base.py` | 86 | CSS (+ `.stat-card` rules), `head()`, `header()`, `stats_row()`, `tiers_row()` |
| `templates/_tabs.py` | 40 | `tab_bar()` — 23 tab items as a list |
| `templates/_panels.py` | 294 | `all_panels()` — 23 panel fns using components |
| `templates/_js.py` | 860 | `_JS` constant — raw JS extracted verbatim |
| `api/core.py` | 153 | overview, providers, usage, health, crypto |
| `api/agents.py` | 215 | a2a, agents, routing, factory, agent-query |
| `api/forensic.py` | 396 | findings, iocs, yara, network, intel, audit, compliance, NIST |
| `api/ops.py` | 183 | cases, tasks, task lifecycle, PoCs |
| `api/tables.py` | 148 | db counts, investigations, models, generic table, prompts, telemetry |
| `api/sse.py` | 153 | /sse/cases · /sse/tasks · /sse/health · /sse/telemetry |
| `_schema.py` | 149 | Tortoise model introspector — 82 models |

**23 tabs**: Providers · Usage & Cost · Agents · Routing · Factory · Prompts · Health · Crypto · A2A · Investigations · DB Counts · Cases · Tasks · PoCs · Explorer · Findings · IOCs · YARA · Network · Intel · Audit · Compliance · Agent Query

**Key endpoints**: `GET /api/models` · `GET /api/tables/{model}` · `POST /api/agent-query` ({agent, prompt, context_table?, row_ids?})

**renderTable() pattern**: `renderTable(containerId, schema, rows)` — schema: `{key, label, type}` where type = string|number|bool|datetime|json. Pre-format badge HTML as strings before passing.

**Known DB model skips**: `db.models.forensic` (SessionPhase.INIT missing) · `db.models.yara_rule` (YaraRuleSource.IOC_DERIVED missing) — `_schema.py` silently skips on import error.

### .claude/ system
| Component | Summary |
|---|---|
| `agents/` | 34 agents: 33 specialists + AGENT_FACTORY · teams/: blue/red/purple · model tiers: Haiku (3), Sonnet (28), Opus (3) |
| `hooks/` | 32 .py files: 10 settings.json-wired + 12 custom event handlers (via `emit()`) + 10 utility modules |
| `commands/` | **DISSOLVED** — all 8 converted to SKILL.md entries (see skills/) |
| `skills/` | 941 SKILL.md across 26 domains — includes 8 former commands (forensics/hunting/apt-hunt, forensics/browser/hunt, forensics/memory/dump, forensics/network/apt-hunt, ops/mode-switch, ops/setup, ops/test-config, ops/team-task) |

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

| Phase | Name | Agent |
|---|---|---|
| 0 | Case Opening | cybersec-agent |
| 1 | Reconnaissance | cybersec-agent |
| 2 | Deep Scan | filesystem-analyst |
| 3 | Network Analysis | network-analyst |
| 4 | Persistence Hunt | persistence-analyst |
| 5 | Memory Forensics | memory-analyst |
| 6 | IOC Correlation | cybersec-analyst |
| 7 | Threat Attribution | threat-modeler |
| 8 | Artifact Signing | cybersec-agent (crypto) |

---

## NIST Fixtures (`data/fixtures/`)

- **nist_csf_2.json** — 185 subcategories, 6 functions (GV/ID/PR/DE/RS/RC). Model: `NistCsfControl`. CLI: `seed-nist-csf`.
- **nist_ai_rmf.json** — 72 subcategories, 4 functions (Govern/Map/Measure/Manage). Model: `NistAiRmfControl`. CLI: `seed-nist-ai-rmf`.
- **DB fixtures** (7): mitre_techniques, mitre_actors, mitre_software, cwe_entries, capec_entries, cve_entries (68 CVEs, 2014-2025), poc_entries

---

## OmniRoute Integration

**PENDING** (`omniroute-integrate`). External MCP at `/home/daen/Projects/OmniRoute/open-sse/mcp-server/` — 19 tools (`omniroute_*`). Register in `mcp.json`. Env: `OMNIROUTE_API_KEY`, `OMNIROUTE_BASE_URL=http://localhost:8888`.

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
- Commands audit — dissolved `commands/` into 8 SKILL.md entries in `skills/`
- Ruff clean — `exclude = [".claude"]` added to pyproject.toml; `src/` + `tests/` → 0 errors
- CVE fixture — expanded from 30 → 68 entries (DirtyCOW, SMBGhost, PwnKit, Log4Shell variants, RegreSSHion, etc.)
- `BrowserForensicFinding` model — created `db/models/browser_forensic.py` (table `browser_forensic_findings`), registered in MODEL_MODULES, fixed `datetime.utcnow()` → `datetime.now(timezone.utc)`, fixed `.annotate()` dict access via `.values()`

### 🚧 Active — Phase K (Dashboard)
7. Settings dashboard (read/edit settings.json)
8. Team builder + Task chain builder + Skill browser

### Pending
- Phase M.3 — consolidate `a2a/` and `checks/`
- Phase N — update all 10 docs + README
- Phase G — SSE frontend wiring (replace polling)
- OmniRoute integration (mcp.json + allowed_tools)

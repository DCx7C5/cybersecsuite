# CyberSecSuite — MEMORY.md (Updated 2026-04-18 01:30 UTC)

---

## CRITICAL ARCHITECTURE — READ FIRST

### Claude → ASGI Proxy → Provider routing

Claude Code (and `agent_sdk.py`) routes ALL Claude API calls through the local ASGI proxy.

```
Claude Code / claude-agent-sdk query()
        │  ANTHROPIC_BASE_URL=http://localhost:8000/v1
        ▼
  ASGI /v1/* (AI Proxy, OpenAI-compat)
        │  AI Proxy routing (combo.py, 13 strategies)
        ├── Anthropic (default)
        ├── OpenAI / Gemini / Groq / Mistral / DeepSeek / XAI / Together / OpenRouter
        └── default_strategy: "cost-optimized"
```

**`agent_sdk.py` — must set base_url in `ClaudeAgentOptions`:**
```python
opts = ClaudeAgentOptions(
    allowed_tools=allowed,
    agents=agents,
    base_url=os.environ.get("ANTHROPIC_BASE_URL", "http://localhost:8000/v1"),
    api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
)
```

### ASGI Mount Map (`src/proxy/asgi.py`)
| Path                      | What                                          |
|---------------------------|-----------------------------------------------|
| `/health`                 | DB health check (200/503)                     |
| `/dashboard/*`            | Dashboard UI + 16 REST + 4 SSE endpoints      |
| `/v1/*`                   | AI Proxy (OpenAI-compat) ← Claude routes here |
| `/a2a/*`, `/.well-known/` | A2A JSON-RPC 2.0 server                       |

### settings.json (`.claude/settings.json`)
```json
{
  "agent": "cybersec-agent",
  "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" },
  "proxy": { "enabled": true, "default_strategy": "cost-optimized" },
  "asgi": { "host": "127.0.0.1", "port": 8000, "alt_port": 8080, "tls_port": 8433 },
  "mcp": { "servers": ["cybersec", "dystopian"], "tool_prefix": "mcp__" }
}
```

`"agent": "cybersec-agent"` → Claude Code auto-loads `.claude/agents/cybersec-agent.md` as orchestrator.

---

## Session Progress

### Done ✅
- Full codebase audit — ground truth established
- **Phase 0** — agent frontmatter, ports, docker, settings, deleted dead middleware
- **Docs** — 16 docs written (README, docs/, module READMEs, committed 7217dff)
- MEMORY.md synced + plan.md removed (committed c6a6792)

### Not Done / Stub / Incomplete
| File                         | Issue                                            | Phase    |
|------------------------------|--------------------------------------------------|----------|
| `src/mcp/__init__.py` (0L)   | Empty                                            | Phase A  |
| `src/mcp/cybersec/`          | Not created (tool split)                         | Phase A  |
| `src/mcp/dystopian.py`       | Not created                                      | Phase A  |
| `mcps/dystopian-crypto-mcp/` | Empty directory                                  | Phase A  |
| `src/a2a/dev_agents.py`      | 6 execute() stubs                                | Phase A2 |
| `src/a2a/cybersec_agent.py`  | ORM-only, no AI                                  | Phase A2 |
| `src/a2a/agent_sdk.py`       | No base_url, 2 inline tools                      | Phase A2 |
| `tests/`                     | Only `__init__.py`, no tests                     | Phase B  |
| `.claude/hooks/*.py`         | 18 files, never audited                          | Phase A  |
| `.claude/commands/*`         | 6 forensics commands, not reviewed               | Phase A  |
| `.claude/skills/*/SKILL.md`  | 780 skills across 20 domains, fully restructured | ✅ Done   |
| `src/telemetry/`             | Not created                                      | Phase E  |
| Extended dashboard           | 8 new tabs, task builder                         | Phase E  |

---

## Codebase Map

### Root
| File                 | Lines | Purpose                                                                 |
|----------------------|-------|-------------------------------------------------------------------------|
| `mcp_server.py`      | 1288  | FastMCP stdio — 29 tools (source of truth → split to src/mcp/cybersec/) |
| `mcp.json`           | 87    | 5 MCP servers for Claude Code CLI                                       |
| `pyproject.toml`     | —     | Python 3.14, uv, all deps                                               |
| `Makefile`           | —     | `make serve`, `make test`, etc.                                         |
| `Dockerfile`         | —     | EXPOSE 8000 8080 8433, uvicorn CMD                                      |
| `docker-compose.yml` | —     | ASGI + PostgreSQL, healthcheck → 8000/health                            |
| `.aiignore`          | —     | AI tool ignore patterns                                                 |
| `.gitignore`         | —     | Standard Python gitignore (*.log, .venv, etc.)                          |

### src/
| File                  | Lines | Purpose                                               |
|-----------------------|-------|-------------------------------------------------------|
| `src/proxy/asgi.py`   | 116   | ASGI app, env-driven ports, mounts all sub-apps       |
| `src/manage.py`       | 329   | CLI management (`manage.py serve`, `case-open`, etc.) |
| `src/logger.py`       | 30    | Structured logger                                     |
| `src/mcp/__init__.py` | 0     | EMPTY — needs `all_servers()`, `allowed_tools()`      |

### src/a2a/
| File                | Lines | Purpose                                      |
|---------------------|-------|----------------------------------------------|
| `agent_sdk.py`      | 304   | SDK bridge (needs base_url + MCP pkg update) |
| `agent_loader.py`   | 272   | Loads `.claude/agents/*.md` → AgentCards     |
| `orchestrator.py`   | 353   | A2A task orchestration                       |
| `dev_agents.py`     | 349   | Dev agent stubs (needs SDK wiring)           |
| `cybersec_agent.py` | 327   | CybersecAgent (ORM-only, needs SDK wiring)   |
| `server.py`         | 236   | A2A JSON-RPC server                          |
| `client.py`         | 205   | A2A client                                   |
| `registry.py`       | 257   | AgentRegistry — remote A2A discovery         |
| `task_store.py`     | 157   | In-memory + DB task store                    |
| `models.py`         | 215   | A2A Pydantic models                          |
| `enums.py`          | —     | A2A enums                                    |
| `agent.py`          | —     | BaseA2AAgent                                 |

### src/ai_proxy/
| File                        | Lines | Purpose                                                   |
|-----------------------------|-------|-----------------------------------------------------------|
| `routes.py`                 | 224   | OpenAI-compat `/v1/*` endpoints                           |
| `providers/registry.py`     | 1001  | 9 providers, model lists, cost metadata, auth types       |
| `routing/combo.py`          | 574   | 13-strategy routing engine, circuit breaker, budget guard |
| `translators/core.py`       | 275   | Request/response translation between formats              |
| `services/rate_limiter.py`  | 159   | Rate limiting per provider                                |
| `services/usage_tracker.py` | 139   | Token usage tracking                                      |
| `executors/base.py`         | 256   | Base executor for async provider calls                    |
| `executors/playwright.py`   | 270   | Playwright-based browser AI provider                      |
| `cli.py`                    | 273   | CLI for provider management, usage, cost reports          |

### src/crypto/ (8 files, complete ✅)
Ed25519 signing, BLAKE2b-256, Argon2id (mem=262144, iters=4), AES-256-GCM.
Keys: `/etc/dystopian-crypto/keys`. Certs: `~/.omniroute/certs/`.
| File | Lines |
|------|-------|
| `pydantic_models.py` | 494 |
| `artifact_manager.py` | 376 |
| `key_manager.py` | 362 |
| `ssl_signer.py` | 277 |
| `template_renderer.py` | 228 |
| `cache.py` | 270 |
| `config.py` | 253 |
| `cli_integration.py` | 299 |

### src/db/ (40+ models, complete ✅)
PostgreSQL via Tortoise ORM (asyncpg). DB: `cybersec_forensics`.
Key models: Investigation, Finding, IOC, YaraRule, NetworkEvent, ComplianceRecord, AuditLog, ApiUsageLog, A2ATask, Artifact, MitreTechnique, CVE, CAPEC, CWE, ThreatProfile, and 25+ more.
Shell scripts: `init_db.sh`, `init_session.sh`, `backup_db.sh`.

### src/dashboard/routes.py (1178L)
16 REST endpoints + 3 SSE endpoints. All HTML inline in `_DASHBOARD_HTML` string.
Current tabs: Cases, Sessions, Agents, Providers, Strategies, Tools, Tasks, Findings, IOCs, Network, Intel, Compliance, Audit.

### .claude/ system
| Component    | Files                                                     | Status                       |
|--------------|-----------------------------------------------------------|------------------------------|
| `agents/`    | 32 agents + AGENT_FACTORY + 3 teams                       | ✅ all consistent frontmatter |
| `hooks/`     | 18 hook .py files + hooks.json (18 events)                | ⚠️ NEVER AUDITED             |
| `commands/`  | 6 forensics commands + config.py                          | ⚠️ NEVER AUDITED             |
| `skills/`    | **780 SKILL.md** across 20 domains, single-word leaf dirs | ✅ RESTRUCTURED (2026-04-18)  |
| `templates/` | artifact.md, baselines/ (kernel/network/persistence)      | Not reviewed                 |

#### hooks.json — 18 events registered
`FirstInit`, `PreToolCall`, `PostToolUse`, `SessionStart`, `SessionEnd`, `AgentStart`, `AgentEnd`, `PhaseStart`, `PhaseEnd`, `InvestigationStart`, `InvestigationEnd`, `IOCDiscovered`, `EvidenceCollected`, `FindingConfirmed`, `ModeSwitch`, `PermissionViolation`, `RootCommandExecuted`, `BaselineUpdated`

#### hooks/_utils.py — shared utilities (ensure_structure, get_project_dir, get_session_dir, audit, emit, hook_context)

---

## mcp_server.py Split Plan (Phase A)

Split `mcp_server.py` (1288L, 29 tools) into `src/mcp/cybersec/` subpackage:

```
src/mcp/
  __init__.py              # all_servers() → dict, allowed_tools() → list[str]
  cybersec/
    __init__.py            # create_sdk_mcp_server("cybersec", tools=[ALL 29 tools])
    helpers.py             # ScopeState, scope vars, helper funcs (lines 16-142 of mcp_server.py)
    findings.py            # add_finding, add_ioc, query_findings, update_risk_register (4 tools)
    db.py                  # db_healthcheck, bootstrap_intelligence (2 tools)
    intelligence.py        # suggest_mitre, get_project_memory (2 tools)
    layers.py              # share_to_layers, get_layer_value (2 tools)
    cache.py               # cache_lookup, cache_store, cache_analytics, cache_invalidate (4 tools)
    proxy.py               # proxy_chat, proxy_providers, proxy_models, proxy_usage, proxy_cost,
                           # simulate_route, set_budget_guard, get_circuit_breakers,
                           # explain_route, routing_strategies (10 tools)
    session.py             # session_snapshot, agent_registry, best_provider (3 tools)
    cases.py               # case_open, case_status (2 tools)
  dystopian.py             # 5 crypto tools wrapping src/crypto/
```

`mcp_server.py` → thin FastMCP stdio shim:
```python
from src.mcp.cybersec import all_tools
mcp = FastMCP("cybersec")
for t in all_tools(): mcp.add_tool(t)
```

Tool naming: `mcp__cybersec__<tool>` (SDK) / `cybersec.<tool>` (FastMCP stdio)
Wildcards: `mcp__cybersec__*`

---

## Agent System

### `"agent": "cybersec-agent"` — Default Claude Code Agent
Loads `.claude/agents/cybersec-agent.md`. Orchestrator with `role: orchestrator`.
Accepts `blue|red|purple` mode. Delegates to all 32 specialist sub-agents.

### All 32 agents — frontmatter consistent ✅
Model tiers:
- **Haiku** — watchdog, command-verifier, layer2-6 specialists
- **Sonnet** — most analysts + developers (default)
- **Opus** — firmware-analyst, reverse-engineer, agent-factory

### Two Execution Paths (NEVER conflate)
**A. Agent SDK** (internal): `query()` → `http://localhost:8000/v1` → provider routing → MCP tools + subagents
**B. A2A Protocol** (external): `POST /a2a` JSON-RPC → OrchestratorAgent → registry → `execute()`

### mcp.json — 5 MCP servers for Claude Code CLI
| Key                      | Server                                                         |
|--------------------------|----------------------------------------------------------------|
| `cybersec`               | Main forensics (29 tools, stdio, `mcp_server.py`)              |
| `dystopian-crypto`       | Crypto/CA/GPG (`mcps/dystopian-crypto-mcp/app.py` — **EMPTY**) |
| `kerneldev`              | Kernel module dev (`kerneldev_mcp.server`)                     |
| `token-optimization-mcp` | Token caching                                                  |
| `playwright-stealth-mcp` | Browser automation                                             |

---

## Ports (after Phase 0)
| Port | What                | Status                        |
|------|---------------------|-------------------------------|
| 8000 | ASGI HTTP (primary) | ✅                             |
| 8080 | ASGI HTTP (alt)     | ⚠️ exposed, no alt listener   |
| 8433 | ASGI HTTPS          | ⚠️ SSL helper ready, no certs |
| 5432 | PostgreSQL          | ✅ localhost                   |

---

## Roadmap

### Phase 0 — Quick Fixes ✅ COMPLETE
### Phase Docs — 16 docs ✅ COMPLETE (commit 7217dff)

### Skills Restructure — IN PROGRESS (2026-04-18)
- **Part A**: Redistribute `red-team/` (51 skills) to component domains
- **Part B**: Flatten 75 same-name nestings
- **Part C**: Restructure `malware/` domain  
- **Part D**: Copy Anthropic extra content (~2,648 files)
- **Part E**: Generate tag + NIST CSF 2.0 fixtures; implement seeding
  - E1: Embed NIST CSF 2.0 (6 Functions, 22 Categories, 106 Subcategories) as static fixture
  - E2: Extract 2,245 tags + 57 MITRE ATT&CK
- **Part F**: Sync MEMORY.md + regenerate INDEX.md + skills.tree

### Phase A — mcp_server.py Split + SDK Package (PRIORITY)
Ordered by dependency:
1. `mcp-cybersec-helpers` — ScopeState + scope helpers (foundation)
2. `mcp-cybersec-findings` / `mcp-cybersec-db` / `mcp-cybersec-intelligence` / `mcp-cybersec-layers` / `mcp-cybersec-cache` / `mcp-cybersec-proxy` / `mcp-cybersec-session` / `mcp-cybersec-cases` — 8 tool submodules (parallel)
3. `mcp-cybersec-pkg` — `src/mcp/cybersec/__init__.py` assembles all tools
4. `mcp-pkg-create` — `src/mcp/__init__.py` with `all_servers()` + `allowed_tools()`
5. `mcp-dystopian-impl` — `src/mcp/dystopian.py` (parallel with above)
6. `mcp-shim-update` — slim `mcp_server.py` to thin shim
7. `mcp-agent-sdk-update` — `agent_sdk.py`: use pkg + set `base_url`
8. `dystopian-mcp-scaffold` — `mcps/dystopian-crypto-mcp/app.py`

### Phase A2 — Wire A2A Stubs to SDK (parallel with A)
`a2a-devagents-wire`, `a2a-cybersec-wire`, `a2a-orchestrator-wire`, `a2a-agentdef-enhance`, `a2a-hooks-add`

### Phase A-Audit (parallel with A/A2)
`hooks-audit`, `commands-audit`, `skills-audit`, `fix-brave-profile-gitignore`

### Phase E — Telemetry + Extended Dashboard + Task Builder
`telemetry-store`, `telemetry-middleware`, `telemetry-decorator`, `telemetry-collector`, `telemetry-mount`
`dashboard-api-telemetry/findings/iocs/yara/network/intel/audit/compliance`
`dashboard-sse-telemetry`, `dashboard-task-create`, `dashboard-task-get`, `dashboard-html-rewrite`

### Phase B — Code Review (after A/A2)
`review-dashboard-routes`, `review-combo-routing`, `review-mcp-server`, `review-a2a-modules`, `review-db-models`, `review-manage-cli`

### Phase C — SSL/TLS (after A)
`ssl-dystopian-integrate`, `ssl-cert-generation`, `ssl-cli-commands`, `ssl-dashboard-tab`, `ssl-proxy-config`

### Phase D — SSE Frontend (optional)
`sse-eventsource-wire`, `sse-autoreconnect`, `sse-replace-polling`

---

## Stack & Conventions

- **Python 3.14** · **`uv`** — never `pip`
- **Tortoise ORM** + PostgreSQL (asyncpg) — `localhost:5432/cybersec_forensics`
- **Starlette ASGI** + uvicorn port 8000
- **FastMCP** for stdio MCP server (Claude Code CLI)
- **Pydantic v2**
- **cryptography** lib: Ed25519, BLAKE2b-256, Argon2id, AES-256-GCM
- **claude-agent-sdk** @ v0.1.61
- Subagents cannot call subagents — never `"Agent"` in `AgentDefinition.tools`
- SSL certs: `~/.omniroute/certs/` · Keys: `/etc/dystopian-crypto/keys`

---

## SDK Code Patterns

### Tool definition (SDK in-process format)
```python
@tool("tool_name", "description", {"param": {"type": "string"}})
async def _fn(args: dict) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(result)}]}
```
FastMCP tools return raw dicts — must be converted for SDK.

### ClaudeAgentOptions
```python
opts = ClaudeAgentOptions(
    allowed_tools=allowed,
    agents=agents,
    base_url=os.environ.get("ANTHROPIC_BASE_URL", "http://localhost:8000/v1"),
    api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
)
```

### ClaudeSDKClient (multi-turn)
```python
async with ClaudeSDKClient(options=options) as client:
    await client.query("prompt")
    async for msg in client.receive_response():
        if isinstance(msg, ResultMessage):
            session_id = msg.session_id
```

### PreToolUse hook
```python
async def audit_hook(input_data, tool_use_id, context):
    await write_scoped_entry_async(entry_type="tool_call", data=input_data)
    return {}
options = ClaudeAgentOptions(hooks={"PreToolUse": [HookMatcher(hooks=[audit_hook])]})
```

### AgentDefinition from frontmatter
```python
AgentDefinition(
    description=card.card.description,
    prompt=card.body,
    tools=card.tools or ["Read", "Glob", "Grep"],  # NEVER "Agent"
    model=card.model,
)
```

### A2A execute() → SDK
```python
async def execute(self, task, message):
    result = await run_agent_query("cybersec-analyst", self._extract_text(message))
    self._reply(task.id, result or "No response.")
```

### Hook import pattern (graceful fallback)
```python
import sys, os
_AI_HOOKS = os.environ.get("CYBERSEC_AI_HOOKS_DIR", "/home/daen/Projects/AI")
if _AI_HOOKS not in sys.path:
    sys.path.insert(0, _AI_HOOKS)
try:
    from hooks.database import (ScopeContext, write_scoped_entry_async,
        query_findings_db_async, get_recent_entries_async, get_scoped_entries_async)
    from hooks.exact_match_cache import (compute_cache_key, cache_get_async,
        cache_put_async, cache_invalidate_async, cache_analytics_async)
    _HOOKS_OK = True
except ImportError:
    _HOOKS_OK = False
    class ScopeContext: pass
    async def write_scoped_entry_async(**kw): return {"status": "hooks_unavailable"}
    # ... rest of stubs
```

### DB bootstrap imports
```python
from db.bootstrap import (get_database_health_async, init_tortoise_async,
    bootstrap_intelligence_async as bootstrap_intelligence_db_async)
```

### Scope helpers — copy from `mcp_server.py` lines 16–142
Copy verbatim into `src/mcp/cybersec/helpers.py`.

---

## Investigation Phases

| Phase | Name               | Agent                   |
|-------|--------------------|-------------------------|
| 0     | Case Opening       | cybersec-agent          |
| 1     | Reconaissance      | cybersec-agent          |
| 2     | Deep Scan          | filesystem-analyst      |
| 3     | Network Analysis   | network-analyst         |
| 4     | Persistence Hunt   | persistence-analyst     |
| 5     | Memory Forensics   | memory-analyst          |
| 6     | IOC Correlation    | cybersec-analyst        |
| 7     | Threat Attribution | threat-modeler          |
| 8     | Artifact Signing   | cybersec-agent (crypto) |

---

## Blueprint Reference
`/home/daen/Projects/AI/blueprints/agent-sdk/` — `custom-tools.md`, `mcp.md`, `agent-loop.md`, `subagents.md`, `sessions.md`, `hooks.md`

---

## Skills System (RESTRUCTURING IN PROGRESS)

### Core Philosophy (User-Defined)
**Skills = components** (tools, protocols, systems, software).
**Actions = verbs** (analyze, harden, attack, detect, hunt, create) applied to components.
**Activities ≠ domains** — `red-team/`, `forensics/`, `incident-response/` are methods/activities.

### Restructuring Plan (5 Phases - Ordered)

#### Phase 0: Copy Anthropic Extra Content ⭐ FIRST
**Why**: Must copy scripts/references BEFORE renaming, to ensure complete skill dirs.

- **ALL 754 Anthropic skills** have: LICENSE + scripts/ + references/ + sometimes assets/
- **Strategy**: For each Anthropic skill, use `/tmp/skill_mapping.json` to find corresponding skill location
- **Copy**: LICENSE + scripts/ + references/ + assets/ → our skill dir
- **Preserve**: directory structure (scripts/, references/, assets/)
- **Total**: ~2,648 files copied
- **Result**: Each skill dir has complete Anthropic content + our SKILL.md

#### Phase 1: Plan Deep Hierarchy
- Analyze all 780 skills by path depth
- Identify logical groupings for 3rd/4th/5th subdirs
- Generate: old_path → new_path, old_name → new_name mappings

#### Part A: Redistribute red-team/ (51 skills) to component domains
**Currently**: `red-team/` has 51 skills (access/, recon/, c2/, lateral/, privesc/, socialeng/, etc.)
**Solution**: `red-team/SKILL.md` stays as single **orchestrator index**. All 51 skills move to:
- `web-security/auth/enum/` (access/authentication)
- `identity/ad/`, `identity/kerberos/` (lateral movement, Kerberos attacks, AD exploits)
- `network/smb/`, `network/dns/`, `network/lateral/`, `network/recon/` (network attacks)
- `malware/c2/` (c2/sliver, c2/havoc, c2/covenant, c2/adversary, etc.)
- `cloud-security/aws/`, `cloud-security/kubernetes/` (cloud privesc)
- `endpoint-security/` (windows lateral, LOLBins, privesc, credentials)
- `kernel-os/linux/` (Linux privesc)
- `ot-ics/iot/` (IoT attacks)
- `siem-soc/splunk/` (SIEM detection)
- `ops/engagement/`, `ops/socialeng/`, `ops/purpleteam/`, `ops/physical/` (non-attack ops)
- `mobile/pentest/`, `vulnerability/exploit/` (mobile/binary exploitation)

**After redistribution**: `red-team/` = ONLY `SKILL.md` (links to 51 skills in their homes).

#### Part B: Flatten 75 same-name nestings
Across all domains: promote `foo/foo/SKILL.md` → `foo/SKILL.md`.

#### Part C: Restructure malware/ domain
Merge: `static/` + `static-analysis/` → `analysis/`; `ioc/` + `iocs/` → `ioc/`.
Relocate: Empire → `c2/empire/`; `ghidrare` → `golang/`; `dnspy` → `dotnet/`.

#### Part D: Copy Anthropic extra content
~2,648 files: `scripts/`, `references/`, `assets/`, `SKILL.es.md`.

#### Part E: Deep Hierarchy + Path-Based Naming
Add 3rd/4th/5th levels, rename all SKILL.md `name:` fields to path-based names:
- `mobile/android/apk/static-analysis/SKILL.md` → name: `android-apk-static-analysis`
- `forensics/memory/analysis/volatility3/plugins/linux/processes/SKILL.md` → name: `memory-volatility3-plugins-linux-processes`

#### E1 — NIST CSF 2.0 static fixture ✅ YES
**Why**: CSF 2.0 is closed/published — no live API. Embed as static fixture.
**Structure**: 6 Functions → 22 Categories → 106 Subcategories
- Functions: `GV` (Govern), `ID` (Identify), `PR` (Protect), `DE` (Detect), `RS` (Respond), `RC` (Recover)
- Categories: e.g. `GV.OC`, `ID.AM`, `PR.AA`, `DE.CM`, `RS.MA`, `RC.RP`
- All 106 subcategories embedded in `data/fixtures/nist_csf.json` (static, no download)

**Coverage**: SKILL.md files reference 46/106. `RS.AN-01` (CSF 1.1) marked as deprecated.

**Implementation**:
- Model: `ComplianceRule` with `framework="NIST_CSF_2.0"` (or new `NistCsfControl`)
- Seed: `seed_nist_csf()` in `seeds.py` (idempotent, get_or_create by identifier)
- Cross-ref: Link skills to CSF controls after tag seeding

#### E2 — Tag fixtures
Extract 2,245 tags + 57 MITRE ATT&CK → `data/fixtures/`; seed via `seed_skill_tags()`.

#### Part G: Sync
Update `MEMORY.md` (component philosophy), regenerate `INDEX.md` + `skills.tree`.

### Restructuring Order
**Phase 0** → **Phase 1** → **Part A** → **Part B** → **Part C** → **Part D** → **Part E** → **Part G**

### Current Structure (before restructuring)
```
.claude/skills/               ← root (780 SKILL.md, 20 domains)
├── forensics/          (89)  # disk, memory, network, log, email, mobile, cloud, usb
├── malware/            (70)  # static, dynamic, reversing, ransomware, persistence, obfuscation,
│                             #   cobaltstrike, families, supplychain, ioc, yara, pdf, triage
├── threat-intel/       (87)  # platforms, feeds, ioc, osint, darkweb, mitre, analysis,
│                             #   detection, hunting
├── incident-response/  (39)  # triage, containment, eradication, recovery, playbooks, tabletop,
│                             #   phishing, cloud, insider, malware, dashboard
├── vulnerability/      (30)  # scanning, sca, prioritization, remediation, management
├── red-team/           (51)  # TO REDISTRIBUTE ⚠️
├── network/ (was network-security)  (35)
├── web-security/       (95)
├── cloud-security/    (113)
├── identity/ (was identity-security) (44)
├── endpoint-security/  (16)
├── ot-ics/             (24)
├── crypto-pki/         (20)
├── siem-soc/           (24)
├── compliance/         (13)
├── kernel-os/           (7)
├── mobile/              (7)
├── steganography/       (1)
├── deception/           (5)
├── database/ (new, empty)
├── browser/ (new, empty)
├── hardening/ (index-only, empty)
└── ops/                 (9)  # mode, scope, meta-ops
```

### Skill Counts (Current)
| Type                                | Count   | Description                                              |
|-------------------------------------|---------|----------------------------------------------------------|
| Project-native (full)               | 26      | Rich SKILL.md with MCP examples, DB queries, agent hooks |
| Anthropic-integrated (full content) | 754     | Full Anthropic workflow + CyberSecSuite integration      |
| **Total**                           | **780** | All in `.claude/skills/`, indexed in `INDEX.md`          |

### Naming Rules
- **Taxonomy dirs** (framework): CAN have hyphens (`cloud-security`, `red-team`, `crypto-pki`)
- **Leaf skill dirs**: Single-word only (`volatility3`, `cobaltstrike`, `jit`, `kerberoasting`)
- Each Anthropic skill individually mapped to meaningful single-word dirname
- 224 explicit collision overrides for disambiguation

### SKILL.md Format
All skills share common frontmatter:
```yaml
---
name: skill-name
description: "..."
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: [T1055]
nist_csf: [DE.AE-02]
tags: [volatility, memory]
source: Anthropic-Cybersecurity-Skills   # or empty for project-native
---
```
Anthropic skills contain FULL original workflow content (commands, code, detection steps)
plus appended `## CyberSecSuite Integration` section with MCP tool usage.

### Key Files (After Restructure)
- `INDEX.md` — master sorted list (auto-generated, 780 entries)
- `ops/mode/blue-team/SKILL.md` — blue team mode activation
- `red-team/SKILL.md` — red team orchestrator index (links to 51 skills across domains)
- `ops/purpleteam/SKILL.md` — purple team mode activation
- `kernel-os/linux/lkm/kerneldev-forensic/` — full skill with config/, examples/, scripts/, templates/

### Anthropic Skills Source
All 754 skills from `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/`
Full content copied with adapted frontmatter (model, maxTurns, mcpServers added).
Restructure script: `/tmp/skills_restructure2.py` (taxonomy routing + single-word extraction)

---

## OmniRoute Integration (NEW)

### OmniRoute MCP Server — 16+ Tools
**Location**: `/home/daen/Projects/OmniRoute/open-sse/mcp-server/`

#### Essential Tools (8)
| Tool | Purpose |
|------|---------|
| `omniroute_get_health` | Gateway health, circuit breakers, uptime |
| `omniroute_list_combos` | All configured combos with models |
| `omniroute_get_combo_metrics` | Performance metrics for a specific combo |
| `omniroute_switch_combo` | Switch active combo by ID/name |
| `omniroute_check_quota` | Quota status per provider or all |
| `omniroute_route_request` | Send a chat completion through OmniRoute |
| `omniroute_cost_report` | Cost analytics for a time period |
| `omniroute_list_models_catalog` | Full model catalog with capabilities |

#### Advanced Tools (8)
| Tool | Purpose |
|------|---------|
| `omniroute_simulate_route` | Dry-run routing simulation |
| `omniroute_set_budget_guard` | Session budget with degrade/block/alert |
| `omniroute_set_routing_strategy` | Runtime strategy switch |
| `omniroute_set_resilience_profile` | Apply resilience presets |
| `omniroute_test_combo` | Live-test all models in a combo |
| `omniroute_get_provider_metrics` | Detailed per-provider metrics |
| `omniroute_best_combo_for_task` | Task-fitness recommendation |
| `omniroute_explain_route` | Explain a past routing decision |

#### Skill Tools (3)
- `omniroute_skills_list` — List all registered skills
- `omniroute_skills_enable` — Enable/disable skill
- `omniroute_skills_execute` — Execute skill with input

### Integration Plan
- Register as external MCP server in `mcp.json`
- Add omniroute entry with npm command
- Env vars: `OMNIROUTE_API_KEY`, `OMNIROUTE_BASE_URL=http://localhost:8888`
- Update allowed_tools() → `mcp__omniroute__*`
- Status: **PENDING** (todo: omniroute-integrate)

---

## Author + Action Metadata Update (NEW)

### Changes to ALL 780 SKILL.md Files
**Philosophy**: Skills = components. Last directory = action verb/tool applied to component.

### Fields to Update/Add
1. **`author: dcx7c5`** — change ALL from mahipal → dcx7c5 (754 Anthropic skills)
                          add to 26 project-native skills
2. **`action: <last_dir>`** — extract leaf directory name
   - Examples:
     - `mobile/android/apk/static-analysis/` → action: `static-analysis`
     - `forensics/memory/analysis/volatility3/` → action: `volatility3`
     - `cloud-security/aws/iam/` → action: `iam`
     - `malware/c2/sliver/` → action: `sliver`

### Current State
- 754/780 have author field (mostly mahipal)
- 26/780 have NO author field (project-native)
- 0/780 have action field (to be added)

### Todos
- `author-action-map` — Generate mapping (pending)
- `author-action-update` — Update all 780 SKILL.md (pending)
- `author-action-validate` — Verify + regenerate INDEX (pending)

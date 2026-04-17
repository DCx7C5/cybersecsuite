# CyberSecSuite — MEMORY.md (Updated 2026-04-17 08:00 UTC)

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
| Path | What |
|------|------|
| `/health` | DB health check (200/503) |
| `/dashboard/*` | Dashboard UI + 16 REST + 4 SSE endpoints |
| `/v1/*` | AI Proxy (OpenAI-compat) ← Claude routes here |
| `/a2a/*`, `/.well-known/` | A2A JSON-RPC 2.0 server |

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
| File | Issue | Phase |
|------|-------|-------|
| `src/mcp/__init__.py` (0L) | Empty | Phase A |
| `src/mcp/cybersec/` | Not created (tool split) | Phase A |
| `src/mcp/dystopian.py` | Not created | Phase A |
| `mcps/dystopian-crypto-mcp/` | Empty directory | Phase A |
| `src/a2a/dev_agents.py` | 6 execute() stubs | Phase A2 |
| `src/a2a/cybersec_agent.py` | ORM-only, no AI | Phase A2 |
| `src/a2a/agent_sdk.py` | No base_url, 2 inline tools | Phase A2 |
| `tests/` | Only `__init__.py`, no tests | Phase B |
| `.claude/hooks/*.py` | 18 files, never audited | Phase A |
| `.claude/commands/*` | 6 forensics commands, not reviewed | Phase A |
| `.claude/skills/*/SKILL.md` | 20+ skills, not reviewed | Phase A |
| `src/telemetry/` | Not created | Phase E |
| Extended dashboard | 8 new tabs, task builder | Phase E |

---

## Codebase Map

### Root
| File | Lines | Purpose |
|------|-------|---------|
| `mcp_server.py` | 1288 | FastMCP stdio — 29 tools (source of truth → split to src/mcp/cybersec/) |
| `mcp.json` | 87 | 5 MCP servers for Claude Code CLI |
| `pyproject.toml` | — | Python 3.14, uv, all deps |
| `Makefile` | — | `make serve`, `make test`, etc. |
| `Dockerfile` | — | EXPOSE 8000 8080 8433, uvicorn CMD |
| `docker-compose.yml` | — | ASGI + PostgreSQL, healthcheck → 8000/health |
| `.aiignore` | — | AI tool ignore patterns |
| `.gitignore` | — | Standard Python gitignore (*.log, .venv, etc.) |

### src/
| File | Lines | Purpose |
|------|-------|---------|
| `src/proxy/asgi.py` | 116 | ASGI app, env-driven ports, mounts all sub-apps |
| `src/manage.py` | 329 | CLI management (`manage.py serve`, `case-open`, etc.) |
| `src/logger.py` | 30 | Structured logger |
| `src/mcp/__init__.py` | 0 | EMPTY — needs `all_servers()`, `allowed_tools()` |

### src/a2a/
| File | Lines | Purpose |
|------|-------|---------|
| `agent_sdk.py` | 304 | SDK bridge (needs base_url + MCP pkg update) |
| `agent_loader.py` | 272 | Loads `.claude/agents/*.md` → AgentCards |
| `orchestrator.py` | 353 | A2A task orchestration |
| `dev_agents.py` | 349 | Dev agent stubs (needs SDK wiring) |
| `cybersec_agent.py` | 327 | CybersecAgent (ORM-only, needs SDK wiring) |
| `server.py` | 236 | A2A JSON-RPC server |
| `client.py` | 205 | A2A client |
| `registry.py` | 257 | AgentRegistry — remote A2A discovery |
| `task_store.py` | 157 | In-memory + DB task store |
| `models.py` | 215 | A2A Pydantic models |
| `enums.py` | — | A2A enums |
| `agent.py` | — | BaseA2AAgent |

### src/ai_proxy/
| File | Lines | Purpose |
|------|-------|---------|
| `routes.py` | 224 | OpenAI-compat `/v1/*` endpoints |
| `providers/registry.py` | 1001 | 9 providers, model lists, cost metadata, auth types |
| `routing/combo.py` | 574 | 13-strategy routing engine, circuit breaker, budget guard |
| `translators/core.py` | 275 | Request/response translation between formats |
| `services/rate_limiter.py` | 159 | Rate limiting per provider |
| `services/usage_tracker.py` | 139 | Token usage tracking |
| `executors/base.py` | 256 | Base executor for async provider calls |
| `executors/playwright.py` | 270 | Playwright-based browser AI provider |
| `cli.py` | 273 | CLI for provider management, usage, cost reports |

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

### mcps/ (5 servers)
| Server | Status |
|--------|--------|
| `dystopian-crypto-mcp/` | **EMPTY** — needs scaffold (mcp.json references `app.py`) |
| `playwright-stealth-mcp/` | Complete standalone MCP server |
| `token-optimization-mcp/` | Complete standalone MCP server |
| `brave_stealth_profile/` | Browser profile for playwright (should be gitignored!) |
| `MCP_DEV_INSTRUCTIONS.md` | Dev instructions for MCP component development |

### .claude/ system
| Component | Files | Status |
|-----------|-------|--------|
| `agents/` | 32 agents + AGENT_FACTORY + 3 teams | ✅ all consistent frontmatter |
| `hooks/` | 18 hook .py files + hooks.json (18 events) | ⚠️ NEVER AUDITED |
| `commands/` | 6 forensics commands + config.py | ⚠️ NEVER AUDITED |
| `skills/` | 20+ skills with SKILL.md | ⚠️ NEVER AUDITED |
| `templates/` | artifact.md, baselines/ (kernel/network/persistence) | Not reviewed |

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
| Key | Server |
|-----|--------|
| `cybersec` | Main forensics (29 tools, stdio, `mcp_server.py`) |
| `dystopian-crypto` | Crypto/CA/GPG (`mcps/dystopian-crypto-mcp/app.py` — **EMPTY**) |
| `kerneldev` | Kernel module dev (`kerneldev_mcp.server`) |
| `token-optimization-mcp` | Token caching |
| `playwright-stealth-mcp` | Browser automation |

---

## Ports (after Phase 0)
| Port | What | Status |
|------|------|--------|
| 8000 | ASGI HTTP (primary) | ✅ |
| 8080 | ASGI HTTP (alt) | ⚠️ exposed, no alt listener |
| 8433 | ASGI HTTPS | ⚠️ SSL helper ready, no certs |
| 5432 | PostgreSQL | ✅ localhost |

---

## Roadmap

### Phase 0 — Quick Fixes ✅ COMPLETE
### Phase Docs — 16 docs ✅ COMPLETE (commit 7217dff)

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

| Phase | Name | Agent |
|-------|------|-------|
| 0 | Case Opening | cybersec-agent |
| 1 | Rapid Recon | cybersec-agent |
| 2 | Deep Scan | filesystem-analyst |
| 3 | Network Analysis | network-analyst |
| 4 | Persistence Hunt | persistence-analyst |
| 5 | Memory Forensics | memory-analyst |
| 6 | IOC Correlation | cybersec-analyst |
| 7 | Threat Attribution | threat-modeler |
| 8 | Artifact Signing | cybersec-agent (crypto) |

---

## Blueprint Reference
`/home/daen/Projects/AI/blueprints/agent-sdk/` — `custom-tools.md`, `mcp.md`, `agent-loop.md`, `subagents.md`, `sessions.md`, `hooks.md`

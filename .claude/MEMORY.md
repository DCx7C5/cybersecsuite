# CyberSecSuite — MEMORY.md (Updated 2026-04-17 07:46 UTC)

---

## CRITICAL ARCHITECTURE — READ FIRST

### Claude → ASGI Proxy → Provider routing

Claude Code (and `agent_sdk.py`) is configured to route ALL Claude API calls through
the local ASGI proxy at `http://localhost:8000/v1` instead of hitting Anthropic directly.

```
Claude Code / claude-agent-sdk query()
        │
        │  ANTHROPIC_BASE_URL=http://localhost:8000/v1
        ▼
  ASGI /v1/* (AI Proxy)           ← OpenAI-compatible endpoint
        │
        │  AI Proxy routing (combo.py, 13 strategies)
        ├── Anthropic (default)
        ├── OpenAI / Gemini / Groq / Mistral / ...
        └── cost-optimized strategy by default
```

This means:
- Every agent query → goes through `ai_proxy/routes.py` → routed to best provider
- Routing strategy in proxy config: `"default_strategy": "cost-optimized"`
- Circuit breaker protects each provider (5 failures → 60s cooldown)
- Token usage is tracked in DB (`ApiUsageLog`) for every request

### settings.json — Key fields (`.claude/settings.json`)

```json
{
  "agent": "cybersec-agent",     ← Default Claude Code agent (cybersec-agent)
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "proxy": {
    "enabled": true,
    "default_strategy": "cost-optimized",
    "prefer_free": false
  },
  "asgi": {
    "host": "127.0.0.1",
    "port": 8000,
    "alt_port": 8080,
    "tls_port": 8433
  },
  "mcp": {
    "servers": ["cybersec", "dystopian"],
    "tool_prefix": "mcp__"
  }
}
```

The `"agent": "cybersec-agent"` key sets the Claude Code default agent.
Claude Code loads `.claude/agents/cybersec-agent.md` as the active agent on start.

### agent_sdk.py — must set base_url

When `build_agent_options()` creates `ClaudeAgentOptions`, it MUST set the proxy URL:
```python
opts = ClaudeAgentOptions(
    allowed_tools=allowed,
    agents=agents,
    # Route through local ASGI proxy
    base_url=os.environ.get("ANTHROPIC_BASE_URL", "http://localhost:8000/v1"),
    api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
)
```
Without this, `query()` hits Anthropic directly, bypassing our proxy and routing logic.

### ASGI App Mount Map

```
GET  /health                     → DB health check (200/503)
     /dashboard/*                → Dashboard UI + 16 REST + 4 SSE endpoints
     /v1/*                       → AI Proxy (OpenAI-compat) ← Claude routes here
     /a2a/*, /.well-known/       → A2A JSON-RPC 2.0 server
```

---

## Session Progress

### Done ✅
- Full codebase audit — ground truth established
- Architecture: in-process MCP via `create_sdk_mcp_server()`
- Agent audit — all 32 agents inspected, 8 needed fixes
- **Phase 0** — agents, ports, docker, settings, deleted dead code
- **Phase Docs** — 16 docs written (README, docs/, module READMEs)
- Telemetry + extended dashboard plan written (17 todos in SQL)

### Not Done (stub / incomplete)
| File | Issue | Fix in |
|------|-------|--------|
| `src/mcp/__init__.py` (0L) | Empty | Phase A |
| `src/mcp/cybersec.py` | Not created | Phase A |
| `src/mcp/dystopian.py` | Not created | Phase A |
| `src/a2a/dev_agents.py` | 6 execute() stubs | Phase A2 |
| `src/a2a/cybersec_agent.py` | ORM-only, no AI | Phase A2 |
| `src/a2a/agent_sdk.py` | No base_url set, 2 inline tools | Phase A2 |
| `tests/` | Source files missing | Phase B |
| Telemetry module | Not created | Phase E (next) |
| Extended dashboard | 8 new tabs, task builder | Phase E (next) |

---

## Verified Reality

### Codebase
- **92 Python files**, **15,783 LOC**, 8 modules
- **32 agent definitions** in `.claude/agents/` (+ AGENT_FACTORY + 3 teams)
- **29 MCP tools** in `mcp_server.py` (stdio only; not yet in-process)
- **9 AI providers** configured
- **5 MCP servers** in `mcp.json` (cybersec, dystopian-crypto, kerneldev, token-optimization, playwright-stealth)

### Ports (current — after Phase 0)
| Port | What | Status |
|------|------|--------|
| 8000 | ASGI app (primary) | ✅ HTTP, env-configurable |
| 8080 | Alt HTTP | ⚠️ Exposed, no alt listener yet |
| 8433 | HTTPS | ⚠️ SSL context ready, needs certs |
| 5432 | PostgreSQL | ✅ localhost only |

---

## Agent System

### `"agent": "cybersec-agent"` — Default Claude Code Agent
When Claude Code starts in this project, it loads `cybersec-agent` from
`.claude/agents/cybersec-agent.md`. This is the orchestrator. It:
- Accepts `blue|red|purple` mode argument
- Delegates to all 32 specialist sub-agents
- Has `role: orchestrator` in frontmatter

### Agent Frontmatter Canon (all 32 except AGENT_FACTORY)
```yaml
---
name: <agent-name>
description: "<trigger description — must have 'Invoke for:' and 'Triggers:' clauses>"
model: sonnet          # haiku | sonnet | opus
maxTurns: 30
tools:
  - Read
  - Bash
  - Glob
  - Grep
disallowedTools:       # for read-only analysts only
  - Write
  - Edit
---
```

### Model tiers
| Tier | Model | Agents |
|------|-------|--------|
| Haiku | claude-haiku-4.5 | watchdog, command-verifier, layer2-6 specialists |
| Sonnet | claude-sonnet-4 | most analysts + developers (default) |
| Opus | claude-opus-4.5 | firmware-analyst, reverse-engineer, agent-factory |

### All 32 agents — frontmatter consistent ✅

---

## Architecture

### Two Complementary Subsystems (NEVER conflate)

**A. Agent SDK path** (internal AI execution)
```
query(prompt, options) → Claude API (via ASGI /v1/* proxy)
  → in-process MCP tools (src/mcp/)
  → subagents (.claude/agents/*.md as AgentDefinitions)
```

**B. A2A Protocol path** (external HTTP agent-to-agent)
```
POST /a2a (JSON-RPC 2.0)
  → OrchestratorAgent → AgentRegistry → BaseA2AAgent.execute()
  → eventually calls run_agent_query() [Phase A2]
```

Both paths are served by the same ASGI app. SDK is for internal use; A2A is for external interop.

### In-Process MCP target structure (Phase A)
```
src/mcp/
  __init__.py     # all_servers() → dict, allowed_tools() → list[str]
  cybersec.py     # 29 @tool defs + create_sdk_mcp_server("cybersec", ...)
  dystopian.py    # crypto @tool defs + create_sdk_mcp_server("dystopian", ...)
mcp_server.py     # thin FastMCP stdio shim → imports from src/mcp/
```

Tool naming: `mcp__cybersec__<tool>`, `mcp__dystopian__<tool>`
Wildcards: `mcp__cybersec__*`

---

## Roadmap (All Phases)

### Phase 0 — Quick Fixes ✅ COMPLETE

### Phase Docs — Documentation ✅ COMPLETE
16 docs: README.md, docs/architecture|quickstart|configuration|api|mcp-tools|agents|deployment|contributing.md,
src/a2a|ai_proxy|crypto|dashboard|db|proxy|mcp/README.md

### Phase E — Telemetry + Extended Dashboard + Task Builder (NEXT)
17 todos in SQL DB. Priority: Phase E before A/A2 because it adds observability.

| Group | Todos |
|-------|-------|
| Telemetry layer (src/telemetry/) | telemetry-store, telemetry-middleware, telemetry-decorator, telemetry-collector, telemetry-mount |
| New dashboard API endpoints | dashboard-api-telemetry, -findings, -iocs, -yara, -network, -intel, -audit, -compliance |
| New SSE endpoint | dashboard-sse-telemetry |
| Task builder API | dashboard-task-create, dashboard-task-get |
| Dashboard HTML rewrite | dashboard-html-rewrite |

**Telemetry captures**: HTTP latency/RPS, A2A task throughput, MCP tool timing, provider response times  
**New tabs**: Telemetry, Findings, IOCs, YARA Rules, Network, Intelligence, Audit Log, Compliance  
**Task Builder**: UI panel to submit A2A tasks (agent dropdown, message, session ID, live result stream)

### Phase A — In-Process MCP Package
| Todo | Task |
|------|------|
| `mcp-pkg-create` | `src/mcp/__init__.py`: `all_servers()`, `allowed_tools()` |
| `mcp-cybersec-extract` | Port 29 tools → `src/mcp/cybersec.py` |
| `mcp-dystopian-impl` | Crypto tools in `src/mcp/dystopian.py` |
| `mcp-shim-update` | `mcp_server.py` → thin shim |
| `mcp-agent-sdk-update` | `agent_sdk.py`: use src/mcp/, set base_url, ClaudeSDKClient |

### Phase A2 — Wire A2A Stubs to SDK (parallel with A)
| Todo | Task |
|------|------|
| `a2a-devagents-wire` | `dev_agents.py` execute() stubs → `run_agent_query()` |
| `a2a-cybersec-wire` | `cybersec_agent.py` execute() → `run_agent_query()` |
| `a2a-orchestrator-wire` | `orchestrator.py` `_auto_route()` fallback → SDK |
| `a2a-agentdef-enhance` | Pass `tools` + `model` from frontmatter to `AgentDefinition` |
| `a2a-hooks-add` | `PreToolUse` SDK hook → `hooks/database.py` audit trail |

### Phase B — Code Review (after A/A2)
`review-dashboard-routes`, `review-combo-routing`, `review-a2a-modules`, `review-db-models`, `review-manage-cli`

### Phase C — SSL/TLS (after A)
`ssl-dystopian-integrate`, `ssl-cert-generation`, `ssl-cli-commands`, `ssl-dashboard-tab`, `ssl-proxy-config`

---

## Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `mcp_server.py` | 1288 | FastMCP stdio — 29 tools (source of truth until Phase A) |
| `src/dashboard/routes.py` | 1178 | Dashboard HTML + 16 API + 3 SSE endpoints |
| `src/ai_proxy/routing/combo.py` | 574 | 13-strategy routing, circuit breaker, budget guard |
| `src/crypto/pydantic_models.py` | 494 | Crypto Pydantic schemas |
| `src/crypto/artifact_manager.py` | 376 | Artifact CRUD + signing |
| `src/crypto/key_manager.py` | 362 | Ed25519 key lifecycle, Argon2id KDF |
| `src/a2a/orchestrator.py` | 353 | A2A task orchestration |
| `src/a2a/dev_agents.py` | 349 | Dev agent stubs |
| `src/manage.py` | 329 | CLI management commands |
| `src/a2a/cybersec_agent.py` | 327 | CybersecAgent (ORM-only, needs SDK wiring) |
| `src/a2a/agent_sdk.py` | 304 | Agent SDK integration (needs base_url + MCP update) |
| `src/a2a/agent_loader.py` | 272 | Loads .claude/agents/*.md → AgentCards |

---

## Stack & Conventions

- **Python 3.14** · **`uv`** — never pip
- **Tortoise ORM** + PostgreSQL (asyncpg) — `localhost:5432/cybersec_forensics`
- **Starlette ASGI** + uvicorn on port 8000
- **FastMCP** for stdio MCP server (Claude Code CLI)
- **Pydantic v2** for validation
- **cryptography** lib: Ed25519, BLAKE2b-256, Argon2id, AES-256-GCM
- **claude-agent-sdk** @ v0.1.61 — `query()`, `ClaudeAgentOptions`, `AgentDefinition`, `create_sdk_mcp_server`
- Subagents CANNOT call subagents → never put `"Agent"` in `AgentDefinition.tools`
- SSL certs: PEM format, `~/.omniroute/certs/` (keys dir: `/etc/dystopian-crypto/keys`)
- `mcp.json` + stdio `mcp_server.py` must keep working (Claude Code CLI integration)

### MCP servers in `mcp.json` (5 total)
| Server key | What |
|------------|------|
| `cybersec` | Main forensics MCP server (29 tools) |
| `dystopian-crypto` | Crypto/CA/GPG tools |
| `kerneldev` | Kernel module development |
| `token-optimization-mcp` | Token caching + compression |
| `playwright-stealth-mcp` | Browser automation |

---

## SDK Code Patterns

### ClaudeAgentOptions — MUST set proxy base_url
```python
opts = ClaudeAgentOptions(
    allowed_tools=allowed,
    agents=agents,
    base_url=os.environ.get("ANTHROPIC_BASE_URL", "http://localhost:8000/v1"),
    api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
)
```

### Tool definition
```python
@tool("tool_name", "description", {"param": {"type": "string"}})
async def _fn(args: dict) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(result)}]}
```

### ClaudeSDKClient (multi-turn)
```python
async with ClaudeSDKClient(options=options) as client:
    await client.query("Analyze this CVE")
    async for msg in client.receive_response():
        if isinstance(msg, ResultMessage):
            session_id = msg.session_id
```

### PreToolUse hook
```python
async def audit_hook(input_data, tool_use_id, context):
    await write_scoped_entry_async(entry_type="tool_call", data=input_data)
    return {}  # empty = allow
options = ClaudeAgentOptions(hooks={"PreToolUse": [HookMatcher(hooks=[audit_hook])]})
```

### AgentDefinition from frontmatter
```python
AgentDefinition(
    description=card.card.description,
    prompt=card.body,
    tools=card.tools or ["Read", "Glob", "Grep"],  # NEVER "Agent"
    model=card.model,  # "sonnet" | "opus" | "haiku"
)
```

### A2A execute() → SDK
```python
async def execute(self, task, message):
    text = self._extract_text(message).strip()
    result = await run_agent_query("cybersec-analyst", text)
    self._reply(task.id, result or "No response from agent.")
```

### Tool return format (SDK — NOT raw dicts)
```python
return {"content": [{"type": "text", "text": json.dumps(result_dict)}]}
```

### Hook import pattern (graceful fallback)
```python
import sys, os
_AI_HOOKS = os.environ.get("CYBERSEC_AI_HOOKS_DIR", "/home/daen/Projects/AI")
if _AI_HOOKS not in sys.path:
    sys.path.insert(0, _AI_HOOKS)
try:
    from hooks.database import (
        ScopeContext, write_scoped_entry_async, query_findings_db_async,
        get_recent_entries_async, get_scoped_entries_async,
    )
    from hooks.exact_match_cache import (
        compute_cache_key, cache_get_async, cache_put_async,
        cache_invalidate_async, cache_analytics_async,
    )
    _HOOKS_OK = True
except ImportError:
    _HOOKS_OK = False
    class ScopeContext: pass
    async def write_scoped_entry_async(**kw): return {"status": "hooks_unavailable"}
    # ... stubs
```

### DB bootstrap imports
```python
from db.bootstrap import (
    get_database_health_async,
    init_tortoise_async,
    bootstrap_intelligence_async as bootstrap_intelligence_db_async,
)
```

### Scope helpers — copy from `mcp_server.py` lines 16–142
Copy verbatim into `src/mcp/cybersec.py`: `ScopeState` TypedDict, constants, `_initialize_scope()`, `_get_base_dir()`

---

## Investigation Phases

| Phase | Name | Agent |
|-------|------|-------|
| 0 | Case Opening | cybersec-agent (direct) |
| 1 | Rapid Recon | cybersec-agent |
| 2 | Deep Scan | filesystem-analyst |
| 3 | Network Analysis | network-analyst |
| 4 | Persistence Hunt | persistence-analyst |
| 5 | Memory Forensics | memory-analyst |
| 6 | IOC Correlation | cybersec-analyst |
| 7 | Threat Attribution | threat-modeler |
| 8 | Artifact Signing | cybersec-agent (crypto skill) |

---

## Blueprint Reference
`/home/daen/Projects/AI/blueprints/agent-sdk/` — `custom-tools.md`, `mcp.md`, `agent-loop.md`, `subagents.md`, `sessions.md`, `hooks.md`

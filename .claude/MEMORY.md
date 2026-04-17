# CyberSecSuite — MEMORY.md (Updated 2026-04-17 06:46 UTC)

## Session Progress

### Done
- Full codebase audit — verified ground truth, false claims purged
- Architecture decided — in-process MCP via `create_sdk_mcp_server()`
- All 29 tool implementations read from `mcp_server.py`
- Redundancy analysis complete — SDK vs A2A boundaries clear
- Agent audit — all 32 agents inspected, 8 needed frontmatter fixes
- Source file audit — 92 files, 15.8k LOC, issues catalogued
- Port/TLS audit — no TLS configured, healthcheck references wrong port
- **Phase 0 COMPLETE** (2026-04-17):
  - ✅ All 32 agents now have consistent frontmatter (model/tools/maxTurns/description)
  - ✅ `encoding-specialist.md` rewritten (was unrelated forensics doc → proper encoding analysis agent)
  - ✅ `command-verifier.md` rewritten (no frontmatter → full agent with CmdGuard system prompt)
  - ✅ `watchdog.md` expanded (4 lines → full monitoring agent with alert criteria)
  - ✅ `docker-compose.yml` healthcheck fixed (port 9433 → 8000/health)
  - ✅ `settings.json` got `asgi` + `mcp` sections (ports 8000/8080/8433)
  - ✅ `src/proxy/asgi.py` — env-driven ports (ASGI_HOST/PORT/TLS_PORT) + SSL context helper
  - ✅ `Dockerfile` — EXPOSE 8000 8080 8433 + ASGI env vars + curl for healthcheck
  - ✅ `src/proxy/middleware.py` DELETED (dead code, nothing imported it)
  - ✅ `templates/` dir created (Dockerfile COPY referenced it)
  - ✅ `__pycache__/` cleaned at root and tests/

### NOT Done (no commits yet)
- `src/mcp/cybersec.py` — NOT CREATED
- `src/mcp/dystopian.py` — NOT CREATED
- `src/mcp/__init__.py` — EMPTY
- `agent_sdk.py` — NOT UPDATED (still 2 inline tools)
- `mcp_server.py` — NOT SLIMMED (still full 1288L)
- `tests/` — source files missing (only __pycache__ existed, now cleaned)

---

## Verified Reality — What Actually Exists

### Git
- **No commits yet** — repo on `main` branch, no history

### Codebase Overview
- **92 Python files**, **15,783 LOC**, 8 modules (a2a, ai_proxy, crypto, db, dashboard, proxy, mcp, root)
- **32 agent definitions** in `.claude/agents/` (+ AGENT_FACTORY)
- **29 MCP tools** in `mcp_server.py` (stdio only, not in-process)
- **9 AI providers** configured (OpenAI, Anthropic, Gemini, DeepSeek, Groq, Mistral, XAI, Together, OpenRouter)

### Port Configuration (CURRENT — after Phase 0)
| Port | What                  | Status                                                 |
|------|-----------------------|--------------------------------------------------------|
| 8000 | ASGI app (uvicorn)    | ✅ HTTP, env-configurable via ASGI_PORT                 |
| 8080 | docker-compose mapped | ⚠️ Exposed in Dockerfile, needs alt listener (Phase C) |
| 8433 | docker-compose mapped | ⚠️ SSL context helper ready, needs certs (Phase C)     |
| 5432 | PostgreSQL            | ✅ localhost only                                       |

### Port Configuration (TARGET)
| Port | What                                          |
|------|-----------------------------------------------|
| 8000 | ASGI app HTTP (dev)                           |
| 8080 | ASGI app HTTP (alt, for reverse proxy setups) |
| 8433 | ASGI app HTTPS (TLS via uvicorn `--ssl-*`)    |
| 5432 | PostgreSQL                                    |

---

## Agent Audit — Frontmatter Consistency

### Canonical agent frontmatter (every agent except AGENT_FACTORY must have):
```yaml
---
name: <agent-name>
description: "<clear trigger description>"
model: sonnet          # sonnet | opus | haiku
maxTurns: 30           # 20-50
tools:
  - Read
  - Bash
  - Glob
  - Grep
  - LS
  - TodoRead
  - TodoWrite
---
```
Developers (python-developer, cpp-developer) add: `Write`, `Edit`, `MultiEdit`
Orchestrator (cybersec-agent) adds: `Task`, `WebFetch`, and `role: orchestrator`
Analysts (read-only by default): no `Write`/`Edit`

### All 32 Agents — Frontmatter Consistent ✅
All agents now have: `name`, `description`, `model`, `maxTurns`, `tools` (+ `disallowedTools` where appropriate).
- Read-only analysts: `disallowedTools: [Write, Edit]`
- Developers (python-developer, cpp-developer, frontend-design, senior-frontend): have Write/Edit/MultiEdit
- Orchestrator (cybersec-agent): has Task, WebFetch, `role: orchestrator`
- Lightweight agents (command-verifier, watchdog): `model: haiku`, lower `maxTurns`
- Opus agents: firmware-analyst, reverse-engineer
- Only `cybersec-agent` has `role: orchestrator` — optional for others

---

## Source File Issues

### Files with problems (remaining)
| File                               | Issue                                           | Fix                                              |
|------------------------------------|-------------------------------------------------|--------------------------------------------------|
| `src/mcp/__init__.py` (0L)         | Empty                                           | Populate with `all_servers()`, `allowed_tools()` |
| `src/a2a/dev_agents.py` (350L)     | 6 stub methods return placeholder text          | Wire to `run_agent_query()`                      |
| `src/a2a/cybersec_agent.py` (328L) | ORM only, no AI                                 | Wire to `run_agent_query()`                      |
| `src/a2a/agent_sdk.py` (305L)      | Only 2 inline tools, manual session_id          | Upgrade to full MCP + `ClaudeSDKClient`          |
| `tests/`                           | Source files missing (only __pycache__ existed) | Recreate test suite                              |

### Files fixed in Phase 0 ✅
| File                      | What was done                                                              |
|---------------------------|----------------------------------------------------------------------------|
| `src/proxy/asgi.py`       | Env-driven ports (ASGI_HOST/PORT/TLS_PORT), SSL context helper, documented |
| `src/proxy/middleware.py` | DELETED (dead code)                                                        |
| `docker-compose.yml`      | Healthcheck port 9433 → 8000/health                                        |
| `Dockerfile`              | EXPOSE 8000 8080 8433, ASGI env vars, curl for healthcheck                 |
| `.claude/settings.json`   | Added `asgi` + `mcp` sections                                              |
| 8 agent `.md` files       | Full frontmatter (model/tools/maxTurns)                                    |
| `templates/`              | Created (Dockerfile COPY referenced it)                                    |

### Files that are fine (no changes needed)
- `src/a2a/server.py`, `client.py`, `models.py`, `enums.py`, `task_store.py`, `registry.py` — A2A protocol ✅
- `src/a2a/agent_loader.py` — loads agents, works correctly ✅
- `src/a2a/agent.py`, `orchestrator.py` — structure fine, just needs SDK wiring ✅
- `src/ai_proxy/` (all files) — complete, no issues ✅
- `src/crypto/` (all 8 files) — complete, no issues ✅
- `src/db/` (all files) — complete, no issues ✅
- `src/dashboard/routes.py` — complete ✅
- `src/manage.py` — complete ✅
- `src/logger.py` — complete ✅
- `mcp_server.py` — works as-is for CLI, will become thin shim ✅
- `Makefile` — correct, port-agnostic via env vars ✅
- `mcp.json` — all 5 entries reference valid files ✅
- `pyproject.toml` — dependencies OK ✅

---

## Architecture & SDK Patterns

### In-Process MCP (why + how)
The ASGI app cannot use stdio subprocesses. SDK's `create_sdk_mcp_server()` runs tools as async functions **in-process**.

```
src/mcp/
  __init__.py       # all_servers(), allowed_tools()
  cybersec.py       # 29 @tool defs + create_sdk_mcp_server("cybersec", ...)
  dystopian.py      # cert/key @tool defs + create_sdk_mcp_server("dystopian", ...)
src/a2a/agent_sdk.py  # imports from src/mcp/, ClaudeSDKClient, SDK hooks
mcp_server.py         # THIN SHIM: FastMCP stdio, imports from src/mcp/
```

Tool naming: `mcp__cybersec__<tool>`, `mcp__dystopian__<tool>` — wildcards: `mcp__cybersec__*`

### Two Complementary Subsystems (never conflate)
**A. Agent SDK** (internal AI) — `agent_sdk.py` → `query()` → Claude + MCP tools + subagents
**B. A2A Protocol** (external HTTP) — `server.py`, `client.py` → JSON-RPC 2.0. SDK doesn't replace this.

### Redundancy Summary
| Redundant                        | Fix                                  |
|----------------------------------|--------------------------------------|
| `dev_agents.py` 6 stub methods   | Wire to `run_agent_query()`          |
| `cybersec_agent.py` ORM-only     | Add `run_agent_query()`              |
| `agent_sdk.py` 2 inline tools    | Replace with `src/mcp/all_servers()` |
| `agent_sdk.py` manual session_id | Upgrade to `ClaudeSDKClient`         |
| `_claude_card_to_agent_def()`    | Also pass `tools`, `model`           |

Not redundant: `A2AServer`, `A2AClient`, `models.py`, `enums.py`, `task_store.py`, `registry.py`, `agent_loader.py`, `ai_proxy/`, `crypto/`, `db/`, `dashboard/`

---

## Roadmap

### Phase 0 — Quick Fixes ✅ COMPLETE
| Todo ID                  | Task                                              | Status |
|--------------------------|---------------------------------------------------|--------|
| `fix-agent-frontmatter`  | Fixed all 8 agents — consistent frontmatter       | ✅      |
| `fix-docker-healthcheck` | Healthcheck port 9433 → 8000/health               | ✅      |
| `fix-settings-json`      | Added `asgi` + `mcp` sections                     | ✅      |
| `fix-asgi-ports`         | Env-driven ports, SSL context, Dockerfile updated | ✅      |
| `fix-delete-middleware`  | Deleted `src/proxy/middleware.py`                 | ✅      |

### Documentation ✅ COMPLETE
All 16 docs written:
- `docs/architecture.md` — system diagram, module map, data flows
- `docs/quickstart.md` — full setup guide (clone → serve)
- `docs/configuration.md` — all env vars, ports, settings
- `docs/api.md` — REST + A2A + dashboard API reference
- `docs/mcp-tools.md` — all 29 MCP tools with params
- `docs/agents.md` — all 32 agents catalog
- `docs/deployment.md` — Docker, TLS, production checklist
- `docs/contributing.md` — dev workflow, adding agents/tools
- `src/a2a/README.md` — updated (stale refs fixed, SDK note added)
- `src/ai_proxy/README.md` — 9 providers, 13 strategies, circuit breaker
- `src/crypto/README.md` — Ed25519/BLAKE2b/Argon2id/AES-GCM, key lifecycle
- `src/dashboard/README.md` — 16 REST + 3 SSE endpoints
- `src/db/README.md` — updated (full 50-model table added)
- `src/proxy/README.md` — ASGI mounts, port config, TLS
- `src/mcp/README.md` — stub (Phase A placeholder)
- `README.md` — full project overview (was 3 lines)

### Phase A — In-Process MCP Package
| Todo ID                | Task                                                                     |
|------------------------|--------------------------------------------------------------------------|
| `mcp-pkg-create`       | `src/mcp/__init__.py`: `all_servers()`, `allowed_tools()`                |
| `mcp-cybersec-extract` | Port 29 tools `mcp_server.py` → `src/mcp/cybersec.py` as `@tool` defs    |
| `mcp-dystopian-impl`   | 5 crypto `@tool` defs in `src/mcp/dystopian.py` using `src/crypto/`      |
| `mcp-shim-update`      | `mcp_server.py` → thin FastMCP shim importing from `src/mcp/cybersec.py` |
| `mcp-agent-sdk-update` | `agent_sdk.py`: `src/mcp/all_servers()` + `ClaudeSDKClient` + SDK hooks  |

### Phase A2 — Wire A2A Stubs to Real AI (parallel with A)
| Todo ID                 | Task                                                                            |
|-------------------------|---------------------------------------------------------------------------------|
| `a2a-devagents-wire`    | `dev_agents.py`: replace ALL stubs with `run_agent_query()` calls               |
| `a2a-cybersec-wire`     | `cybersec_agent.py`: `execute()` → `run_agent_query("cybersec-analyst", ...)`   |
| `a2a-orchestrator-wire` | `orchestrator.py`: `_auto_route()` fallback → `run_agent_query()`               |
| `a2a-agentdef-enhance`  | `agent_loader.py`: pass `tools` + `model` from frontmatter to `AgentDefinition` |
| `a2a-hooks-add`         | `agent_sdk.py`: `PreToolUse` SDK hook → `hooks/database.py` audit trail         |

### Phase B — Code Review (after A/A2)
| Todo ID                   | Focus                                |
|---------------------------|--------------------------------------|
| `review-dashboard-routes` | SSE, ORM N+1, error handling         |
| `review-combo-routing`    | Circuit breaker, strategy resolution |
| `review-mcp-server`       | Auth, validation, error sanitization |
| `review-a2a-modules`      | SDK wiring correctness               |
| `review-db-models`        | Constraints, FK integrity            |
| `review-manage-cli`       | CLI async patterns                   |

### Phase C — SSL/TLS (after A)
| Todo ID                   | Task                                                   |
|---------------------------|--------------------------------------------------------|
| `ssl-dystopian-integrate` | Add dystopian-crypto git deps to `pyproject.toml`      |
| `ssl-cert-generation`     | `cert_gen` @tool + `src/crypto/tls.py`                 |
| `ssl-cli-commands`        | `cert-gen`, `cert-status`, `cert-renew` in `manage.py` |
| `ssl-dashboard-tab`       | Dashboard SSL tab + `/api/ssl` + `/sse/ssl`            |
| `ssl-proxy-config`        | ASGI TLS on port 8433                                  |

### Phase D — SSE Frontend (optional)
| Todo ID                | Task                                   |
|------------------------|----------------------------------------|
| `sse-eventsource-wire` | Wire `EventSource` for SSE endpoints   |
| `sse-autoreconnect`    | Exponential backoff + status indicator |
| `sse-replace-polling`  | Replace `setInterval` with SSE         |

---

## Key Files (Actual Line Counts)

| File                              | Lines | Purpose                                               |
|-----------------------------------|-------|-------------------------------------------------------|
| `mcp_server.py`                   | 1288  | FastMCP stdio shim — 29 tools (CLI only)              |
| `src/dashboard/routes.py`         | 1178  | Dashboard HTML + 16 API + 3 SSE endpoints             |
| `src/ai_proxy/routing/combo.py`   | 574   | 13-strategy routing engine, circuit breaker           |
| `src/crypto/pydantic_models.py`   | 494   | Crypto Pydantic schemas                               |
| `src/crypto/artifact_manager.py`  | 376   | Artifact CRUD + signing                               |
| `src/crypto/key_manager.py`       | 362   | Ed25519 key lifecycle, Argon2id KDF                   |
| `src/a2a/orchestrator.py`         | 353   | A2A task orchestration                                |
| `src/a2a/dev_agents.py`           | 349   | Dev agent definitions                                 |
| `src/manage.py`                   | 329   | CLI — case-open + commands                            |
| `src/a2a/cybersec_agent.py`       | 327   | CybersecAgent implementation                          |
| `src/a2a/agent_sdk.py`            | 304   | Agent SDK integration (2 inline tools — needs update) |
| `src/crypto/cli_integration.py`   | 299   | Crypto CLI helpers                                    |
| `src/crypto/ssl_signer.py`        | 277   | Ed25519 signing, JWT-like tokens                      |
| `src/a2a/agent_loader.py`         | 272   | Loads .claude/agents/*.md → AgentCards                |
| `src/crypto/cache.py`             | 270   | Crypto cache                                          |
| `src/a2a/registry.py`             | 257   | AgentRegistry — dynamic agent discovery               |
| `src/crypto/config.py`            | 253   | Crypto config                                         |
| `src/a2a/server.py`               | 236   | A2A JSON-RPC server                                   |
| `src/crypto/template_renderer.py` | 228   | Template rendering                                    |
| `src/a2a/models.py`               | 215   | A2A Pydantic models                                   |
| `src/a2a/client.py`               | 205   | A2A client                                            |
| `src/a2a/task_store.py`           | 157   | In-memory + DB task registry                          |
| `mcp.json`                        | 87    | 5 MCP entries for Claude Code CLI                     |

---

## Stack & Conventions

- **Python 3.14** · **`uv`** — never `pip`. Tests: `uv run --group test pytest`
- **Tortoise ORM** + PostgreSQL (asyncpg) — `localhost:5432/cybersec_forensics`
- **Starlette ASGI** + uvicorn
- **FastMCP** for stdio MCP server (Claude Code CLI only)
- **Pydantic v2** for validation
- **cryptography** lib: Ed25519, BLAKE2b-256, Argon2id, AES-256-GCM
- **Agent SDK**: `claude-agent-sdk @ git+...@v0.1.61`
- 32 `.claude/agents/*.md` agent definitions (+ AGENT_FACTORY)
- **A2A protocol** (JSON-RPC 2.0) for external agent interop
- `AgentRegistry` = remote A2A discovery only. SDK `agents=` dict = internal.
- `mcp.json` + stdio `mcp_server.py` must keep working (Claude Code CLI)
- Subagents cannot call subagents — never include `"Agent"` in `AgentDefinition.tools`
- SSL certs: PEM format, `~/.omniroute/certs/`

### settings.json — IMPLEMENTED ✅ (`.claude/settings.json`)
```json
{
  "asgi": {
    "host": "127.0.0.1",
    "port": 8000,
    "tls_port": 8433,
    "alt_port": 8080,
    "tls_cert": "~/.omniroute/certs/cert.pem",
    "tls_key": "~/.omniroute/certs/key.pem"
  },
  "mcp": {
    "servers": ["cybersec", "dystopian"],
    "tool_prefix": "mcp__"
  }
}
```

### Ports (target)
| Port | Service                         |
|------|---------------------------------|
| 8000 | ASGI HTTP (dev)                 |
| 8080 | ASGI HTTP (alt / reverse proxy) |
| 8433 | ASGI HTTPS (TLS)                |
| 5432 | PostgreSQL                      |

### Investigation Phases
| Phase | Name               | Agent                         |
|-------|--------------------|-------------------------------|
| 0     | Case Opening       | CYBERSEC-AGENT (direct)       |
| 1     | Recon              | CYBERSEC-AGENT                |
| 2     | Deep Scan          | filesystem-analyst            |
| 3     | Network Analysis   | network-analyst               |
| 4     | Persistence Hunt   | persistence-analyst           |
| 5     | Memory Forensics   | memory-analyst                |
| 6     | IOC Correlation    | cybersec-analyst              |
| 7     | Threat Attribution | threat-modeler                |
| 8     | Artifact Signing   | CYBERSEC-AGENT (crypto skill) |

### Hook Import Pattern (for `src/mcp/cybersec.py`)
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
    from hooks.uvloop_integration import get_event_loop_info
    _HOOKS_OK = True
except ImportError:
    _HOOKS_OK = False
    # minimal stubs so import doesn't fail
    class ScopeContext: pass
    async def write_scoped_entry_async(**kw): return {"status": "hooks_unavailable"}
    async def query_findings_db_async(**kw): return []
    async def get_recent_entries_async(*a, **kw): return []
    async def get_scoped_entries_async(**kw): return []
    def compute_cache_key(p):
        import hashlib, json
        return hashlib.sha256(json.dumps(p, sort_keys=True).encode()).hexdigest()
    async def cache_get_async(k): return None
    async def cache_put_async(k, r, t=0, ttl=None): return "stored"
    async def cache_invalidate_async(k): return "invalidated"
    async def cache_analytics_async(): return {}
    def get_event_loop_info(): return {}
```

### Agent SDK Blueprint Reference
`/home/daen/Projects/AI/blueprints/agent-sdk/` — local cached docs:
- `custom-tools.md` — `@tool` decorator, `create_sdk_mcp_server`, in-process pattern
- `mcp.md` — HTTP/stdio/in-process transport options, `allowed_tools` wildcards
- `agent-loop.md` — message types, turns, ResultMessage, AssistantMessage

### Tool Result Format (SDK)
All SDK tools must return:
```python
{"content": [{"type": "text", "text": json.dumps(result_dict)}]}
```
NOT a raw dict. The FastMCP tools in `mcp_server.py` return raw dicts — these need conversion.

### DB bootstrap imports (for case_open / case_status tools)
```python
from db.bootstrap import (
    get_database_health_async,
    init_tortoise_async,
    bootstrap_intelligence_async as bootstrap_intelligence_db_async,
)
```

### Scope helpers to copy from `mcp_server.py` (lines 16–142)
Copy verbatim into `src/mcp/cybersec.py` — do NOT import from mcp_server.py:
- `ScopeState` TypedDict, all 5 constants, all helper functions
- `_BASE_DIR`, `_WORKSPACE_DIR`, `_PROJECT_DIR`, `_SESSION_BASE` module-level vars
- `_initialize_scope()` call at module level

---

## SDK Code Patterns (copy-paste reference)

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
# Resume: ClaudeAgentOptions(resume=session_id, ...)
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
    description=card.card.description, prompt=card.body,
    tools=card.tools or ["Read", "Glob", "Grep"],  # never "Agent"
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

### Hook import pattern (for `src/mcp/cybersec.py`)
See full version in "Stack & Conventions" section above.

### DB bootstrap imports
```python
from db.bootstrap import (get_database_health_async, init_tortoise_async,
    bootstrap_intelligence_async as bootstrap_intelligence_db_async)
```

### Scope helpers — copy from `mcp_server.py` lines 16–142
Copy verbatim into `src/mcp/cybersec.py`: `ScopeState` TypedDict, constants, `_initialize_scope()`, `_get_base_dir()`

### Blueprint reference
`/home/daen/Projects/AI/blueprints/agent-sdk/` — `custom-tools.md`, `mcp.md`, `agent-loop.md`, `subagents.md`, `sessions.md`, `hooks.md`

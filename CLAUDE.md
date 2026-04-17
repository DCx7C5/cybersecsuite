# CyberSecSuite — Claude Project Instructions

> **Default agent**: `cybersec-agent` (set in `.claude/settings.json`)  
> Claude Code auto-loads `.claude/agents/cybersec-agent.md` as the orchestrator for every session.

---

## What this project is

**CyberSecSuite** is a full-stack cybersecurity forensics platform with:
- **ASGI server** (Starlette, port 8000) — AI proxy, A2A protocol, live dashboard
- **MCP server** — 34 tools for forensic investigation, intel lookup, crypto, AI routing
- **33 specialist sub-agents** — filesystem, memory, network, kernel, persistence, and more
- **922 skills** — deep taxonomy across 24+ domains
- **PostgreSQL** — 44 models (findings, IOCs, MITRE, CVE, CWE, CAPEC, NIST CSF/AI RMF, ...)
- **AI proxy** — 9 providers, 13 routing strategies, circuit breaker, budget guard

## Quick Start

```bash
# 1. Start services
docker-compose up -d

# 2. Seed the database
uv run python -m manage seed-all

# 3. Open Claude Code in this directory
# cybersec-agent loads automatically via settings.json
```

## MCP Tools (34 total)

### cybersec server (29 tools, `mcp__cybersec__*`)
| Category | Tools |
|----------|-------|
| Findings | `add_finding`, `add_ioc`, `query_findings`, `update_risk_register` |
| Database | `db_healthcheck`, `bootstrap_intelligence` |
| Intelligence | `suggest_mitre`, `get_project_memory` |
| Layers | `share_to_layers`, `get_layer_value` |
| Cache | `cache_lookup`, `cache_store`, `cache_analytics`, `cache_invalidate` |
| Proxy | `proxy_chat`, `proxy_providers`, `proxy_models`, `proxy_usage`, `proxy_cost`, `simulate_route`, `set_budget_guard`, `get_circuit_breakers`, `explain_route`, `routing_strategies` |
| Session | `session_snapshot`, `agent_registry`, `best_provider` |
| Cases | `case_open`, `case_status` |

### dystopian server (5 tools, `mcp__dystopian__*`)
`crypto_generate_keypair`, `crypto_sign_artifact`, `crypto_verify_artifact`, `crypto_list_keys`, `crypto_rotate_key`

## Agent SDK Pattern

All tools in `src/mcp/` follow the SDK pattern:

```python
@tool("tool_name", "description", {"param": {"type": "string", "description": "..."}})
async def _tool_fn(args: dict[str, Any]) -> dict:
    value = args.get("param", "default")
    return sdk_result({"key": value})
```

Use `from mcp import all_servers, allowed_tools` for SDK wiring.

## Architecture

```
Claude Code / claude-agent-sdk query()
        │  ANTHROPIC_BASE_URL=http://localhost:8000/v1
        ▼
  ASGI /v1/* (AI Proxy — 9 providers, 13 strategies)
        │
  ┌─────┴──────┐
  │ MCP (stdio)│  mcp_server.py → src/mcp/cybersec/ + src/mcp/dystopian.py
  │ A2A (/a2a) │  src/a2a/ → OrchestratorAgent → 33 sub-agents
  │ Dashboard  │  /dashboard/* → 30 REST + 4 SSE endpoints
  └────────────┘
```

## Key Directories

| Path | Purpose |
|------|---------|
| `src/mcp/cybersec/` | SDK MCP package (29 tools, 8 submodules) |
| `src/mcp/dystopian.py` | Crypto tools (Ed25519, Argon2id, AES-256-GCM) |
| `src/a2a/` | A2A protocol, agent SDK bridge, orchestrator |
| `src/ai_proxy/` | AI proxy (9 providers, 13 routing strategies) |
| `src/db/models/` | 44 Tortoise ORM models |
| `src/dashboard/` | Live forensic dashboard (Starlette) |
| `src/telemetry/` | In-process metrics (ring buffer, p50/p95/p99) |
| `src/crypto/` | Ed25519 signing, BLAKE2b-256, Argon2id, AES-256-GCM |
| `.claude/agents/` | 33 specialist agents + 3 team modes |
| `.claude/skills/` | 922 SKILL.md across 24+ domains |
| `.claude/commands/` | 7 slash commands |
| `data/fixtures/` | NIST CSF 2.0, NIST AI RMF 1.0 seed data |

## Environment Variables

```env
# Database
CYBERSEC_DB_HOST=localhost
CYBERSEC_DB_PORT=5432
CYBERSEC_DB_USER=cybersec
CYBERSEC_DB_PASSWORD=<secret>
CYBERSEC_DB_NAME=cybersec_forensics

# AI Proxy
ANTHROPIC_API_KEY=<key>
OPENAI_API_KEY=<key>
ANTHROPIC_BASE_URL=http://localhost:8000/v1   # route through local proxy

# Scope
CYBERSEC_WORKSPACE=default
CYBERSEC_PROJECT=my-project
CYBERSEC_SESSION_ID=<optional>

# Intel
CYBERSEC_INTEL_DIR=./data/cybersec-shared/intelligence
CYBERSEC_BOOTSTRAP_INTEL_ON_START=false
```

## Conventions

- **Python 3.14** · **`uv`** — never `pip install`
- **Tortoise ORM** + PostgreSQL (asyncpg) — no sync DB calls
- **Pydantic v2** for all models
- **Ed25519 + BLAKE2b-256** for artifact signing
- **Argon2id** for key derivation (mem=262144, iters=4)
- Subagents CANNOT call subagents — never `"Agent"` in `AgentDefinition.tools`
- All skill `name:` fields follow: skip layer-1 domain, join remaining dirs with `-`

## See Also

- [`docs/architecture.md`](docs/architecture.md) — system design + flowcharts
- [`docs/quickstart.md`](docs/quickstart.md) — getting started
- [`docs/mcp-tools.md`](docs/mcp-tools.md) — all 34 tools reference
- [`docs/agents.md`](docs/agents.md) — all 33 agents
- [`docs/api.md`](docs/api.md) — REST API endpoints
- [`.claude/MEMORY.md`](.claude/MEMORY.md) — session memory (DO NOT DELETE)

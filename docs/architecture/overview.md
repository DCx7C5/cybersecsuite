# Architecture Overview

CyberSecSuite is a full-stack cybersecurity forensics platform with 7 interconnected layers.

_Last updated: 2026-04_

---

## Layer Summary

| Layer                | Purpose                                                   | Entry point                         |
|----------------------|-----------------------------------------------------------|-------------------------------------|
| **ASGI Application** | HTTP entry point, mounts all subsystems                   | `src/proxy/asgi.py`                 |
| **AI Proxy**         | Multi-provider LLM routing (60 providers, 13 strategies)  | `src/ai_proxy/`                     |
| **MCP Tools**        | 83 tools across 2 servers (stdio)                         | `src/csmcp/`                          |
| **A2A Protocol**     | External agent-to-agent communication (JSON-RPC 2.0)      | `src/a2a/`                          |
| **Agent System**     | 18 active agents, 3 team modes                            | `.claude/agents/`                   |
| **Database**         | PostgreSQL — 44 models, Tortoise ORM (asyncpg)            | `src/db/`                           |
| **Observability**    | Telemetry, OpenObserve, 40+ endpoint dashboard            | `src/telemetry/` + `src/dashboard/` |

---

## System Diagram

```
External clients / Claude Code CLI
      │
      ▼
┌───────────────────────────────────────────────────────────────┐
│  ASGI Application  (src/proxy/asgi.py, port 8000)             │
│                                                               │
│  GET /health          → DB health check (200/503)             │
│  /                    → Dashboard UI                           │
│  /api/* + /sse/*      → Dashboard REST/SSE endpoints           │
│  /v1/*                → AI Proxy (OpenAI-compatible)           │
│  /a2a                 → A2A JSON-RPC 2.0 server                │
│  /.well-known/        → Agent card discovery                   │
└──────┬──────────┬────────────┬────────────────┬───────────────┘
       │          │            │                │
       ▼          ▼            ▼                ▼
  ┌─────────┐ ┌──────────┐ ┌──────────┐  ┌──────────────┐
  │Dashboard│ │ AI Proxy │ │   A2A    │  │   Health     │
  │ 40+ APIs│ │ 13 strat │ │ JSON-RPC │  │   check      │
  │ 4 SSE   │ │ 60 prov  │ │ SSE      │  └──────────────┘
  └────┬────┘ └────┬─────┘ └────┬─────┘
       │           │            │
       ▼           ▼            ▼
  ┌──────────────────────────────────────────────┐
  │  PostgreSQL (Tortoise ORM, asyncpg)          │
  │  44 models · 65 tables · cybersec_forensics  │
  │  MITRE ATT&CK · CVE · CWE · CAPEC · NIST    │
  │  Findings · IOCs · Cases · Artifacts         │
  └──────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────┐
  │ OpenObserve (port 5080)                      │
  │  cybersecsuite-telemetry-YYYY.MM.DD          │
  │  cybersecsuite-audit-YYYY.MM.DD              │
  │  cybersecsuite-api-usage-YYYY.MM.DD          │
  └──────────────────────────────────────────────┘
```

### MCP Servers (Claude Code stdio)

```
Claude Code
  ├── cybersec server      88 tools  (uv run python -m csmcp.cybersec.server)
  ├── dystopian-crypto      5 tools  (uv run python -m csmcp.dystopian_server)
                           ══════
                           122 tools total
```

---

## Two AI Execution Paths

These paths are **complementary**, not alternatives.

### Path A — Agent SDK (internal)

```
request → run_agent_query() → Claude API (via AI Proxy localhost:8000/v1)
                                    │
                         ┌──────────┴──────────┐
                         │  93 in-process MCP   │
                         │  (88 cybersec +      │
                         │   5 dystopian)       │
                         └─────────────────────┘
```

`agent_sdk.py` → `build_agent_options()` → loads agent + MCP tools → `claude_agent_sdk.query()` → Claude model → tool calls. All in-process.

### Path B — A2A Protocol (external)

```
POST /a2a (tasks/send JSON-RPC)
        │
        ▼
  CybersecA2AAgent
        │
        ├── keyword routing → skill handler (CVE/IOC/MITRE/artifact/threat)
        │         │
        │         ▼
        │   run_agent_query()  → SDK → AI Proxy → Provider
        │
        └── no match → _handle_generic()
                              │
                              ▼
                     run_agent_query("cybersec-analyst")
```

External clients call `/a2a` via JSON-RPC 2.0. Results stream via SSE at `/a2a/stream/{task_id}`.

---

## Port Configuration

| Port    | Protocol | Service                               | Env var                                   |
|---------|----------|---------------------------------------|-------------------------------------------|
| `8000`  | HTTP     | Primary ASGI server (uvicorn)         | `ASGI_PORT`                               |
| `8443`  | HTTPS    | TLS proxy (auto-activates with certs) | `ASGI_TLS_PORT`                           |
| `8765`  | HTTP     | Alt HTTP (Docker exposed)             | —                                         |
| `5432`  | TCP      | PostgreSQL                            | `CYBERSEC_DB_PORT`                        |
| `6379`  | TCP      | Redis cache                           | `REDIS_URL`                               |
| `5080`  | HTTP     | OpenObserve UI + ingestion API        | `OPENOBSERVE_HOST`                        |
| `11434` | HTTP     | Ollama (local LLM)                    | —                                         |

TLS activates automatically when `ASGI_TLS_CERT` + `ASGI_TLS_KEY` exist.

---

## Cryptography Stack

| Algorithm       | Purpose                          | Parameters                       |
|-----------------|----------------------------------|----------------------------------|
| **Ed25519**     | Key generation, artifact signing | 256-bit keys                     |
| **BLAKE2b**     | Content hashing                  | 256-bit digests                  |
| **Argon2id**    | Password KDF, key encryption     | mem=256MB, iters=4, lanes=4      |
| **AES-256-GCM** | Authenticated encryption         | Random 12-byte nonce per message |

Keys stored at `DYSTOPIAN_KEYS_DIR` (default: `/etc/dystopian/crypto/cert/private`). Vault secrets at `~/.dystopian-crypto/vault/`.

---

## Docker Compose Services

| Service                 | Image                          | Port             | Healthcheck         |
|-------------------------|--------------------------------|------------------|---------------------|
| cybersec-postgres        | custom                         | 5432             | pg_isready          |
| cybersec-dashboard       | custom (Python 3.14)           | 8000, 8443, 8765 | curl /health        |
| cybersec-redis           | custom                         | 6379             | redis-cli ping      |
| cybersec-openobserve     | openobserve/openobserve:latest | 5080             | none                |
| cybersec-wazuh           | wazuh/wazuh-manager:latest     | —                | —                   |
| cybersec-ollama          | ollama/ollama:latest           | 11434            | —                   |

---

## Related Docs

- [module-map.md](module-map.md) — file-by-file breakdown
- [data-flow.md](data-flow.md) — request flow examples and integration points
- [../configuration/env-vars.md](../configuration/env-vars.md) — all environment variables
- [../mcp/overview.md](../mcp/overview.md) — MCP tool servers
- [../agents/reference.md](../agents/reference.md) — agent roster

# CyberSecSuite — Layer Integration Guide

> How every layer connects, what data flows between them, and how they
> work together during forensic investigations.

---

## Table of Contents

1. [Overview](#overview)
2. [Layer Summary](#layer-summary)
3. [Architecture Diagram](#architecture-diagram)
4. [Layer Details](#layer-details)
   - [Layer 1 — ASGI Application](#layer-1--asgi-application)
   - [Layer 2 — AI Proxy](#layer-2--ai-proxy)
   - [Layer 3 — MCP Tools](#layer-3--mcp-tools)
   - [Layer 4 — A2A Protocol](#layer-4--a2a-protocol)
   - [Layer 5 — Agent System](#layer-5--agent-system)
   - [Layer 6 — Database](#layer-6--database)
   - [Layer 7 — Observability](#layer-7--observability)
5. [Key Integration Points](#key-integration-points)
6. [Request Flow Examples](#request-flow-examples)
7. [Port Map & Services](#port-map--services)
8. [Docker Compose Services](#docker-compose-services)
9. [Environment Variables Reference](#environment-variables-reference)

---

## Overview

CyberSecSuite is a **multi-layer cybersecurity forensics platform**.  Seven
distinct layers cooperate to deliver AI-powered investigation, threat
intelligence, artifact signing, and real-time observability.  Every external
request enters through a single ASGI application and fans out to the
appropriate subsystem; every subsystem can reach the database and telemetry
pipeline independently.

This document is the authoritative reference for understanding how the layers
connect, which files own each integration point, and what environment
variables govern each connection.

---

## Layer Summary

| # | Layer                | Root Path                                               | Key Responsibility                                       |
|---|----------------------|---------------------------------------------------------|----------------------------------------------------------|
| 1 | **ASGI Application** | `src/proxy/asgi.py`                                     | HTTP entry point — mounts all subsystems                 |
| 2 | **AI Proxy**         | `src/ai_proxy/`                                         | Multi-provider LLM routing (13 strategies, 60 providers) |
| 3 | **MCP Tools**        | `src/csmcp/` + `src/omniroute_mcp/`                     | 63 tools: 31 cybersec + 5 crypto + 27 OmniRoute          |
| 4 | **A2A Protocol**     | `src/a2a/`                                              | JSON-RPC 2.0 agent communication, agent SDK bridge       |
| 5 | **Agent System**     | `.claude/agents/`                                       | 48 agents (37 main + 3 teams + 8 sub-agents), 942 skills |
| 6 | **Database**         | `src/db/`                                               | PostgreSQL via Tortoise ORM — 40+ models, 65 tables      |
| 7 | **Observability**    | `src/telemetry/` + `src/opensearch/` + `src/dashboard/` | Metrics, OpenSearch, 41 dashboard endpoints              |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL CLIENTS                                    │
│   Browser · Claude Code · A2A Peers · REST Consumers · MCP stdio            │
└──────┬──────────┬────────────┬──────────────┬───────────────┬───────────────┘
       │          │            │              │               │
       │ HTTP     │ HTTP       │ HTTP         │ JSON-RPC      │ stdio
       │ :8000    │ :8000      │ :8000        │ :8000         │ (local)
       ▼          ▼            ▼              ▼               ▼
┌──────────────────────────────────────────────────┐   ┌──────────────────┐
│            LAYER 1 — ASGI APPLICATION            │   │   MCP stdio      │
│                 src/proxy/asgi.py                 │   │  (Claude Code)   │
│                                                  │   │  uv run python   │
│  Mount Points:                                   │   │  -m csmcp...     │
│    /v1/*          → AI Proxy  (Layer 2)          │   └────────┬─────────┘
│    /dashboard/*   → Dashboard (Layer 7)          │            │
│    /a2a           → A2A       (Layer 4)          │            │
│    /.well-known/* → Agent Card                   │            │
└──────┬──────────┬────────────┬───────────────────┘            │
       │          │            │                                │
       ▼          │            ▼                                │
┌──────────────┐  │  ┌─────────────────────┐                    │
│  LAYER 2     │  │  │     LAYER 4         │                    │
│  AI PROXY    │  │  │   A2A PROTOCOL      │                    │
│              │  │  │                     │                    │
│  13 routing  │  │  │  JSON-RPC 2.0       │                    │
│  strategies  │◄─┼──│  CybersecA2AAgent   │                    │
│  60 providers│  │  │  → agent_sdk.py     │                    │
│  combo.py    │  │  │  → run_agent_query()│                    │
└──────┬───────┘  │  └─────────┬───────────┘                    │
       │          │            │                                │
       │  ┌───────┘            │                                │
       │  │                    ▼                                │
       │  │  ┌─────────────────────────────────────────────┐    │
       │  │  │          LAYER 5 — AGENT SYSTEM             │    │
       │  │  │                                             │    │
       │  │  │  48 agents  ·  942 skills  ·  3 teams       │    │
       │  │  │  .claude/agents/*.md                        │    │
       │  │  │  .claude/skills/**/*.md                     │    │
       │  │  │                                             │    │
       │  │  │  Agent SDK injects 36 MCP tools             │    │
       │  │  │  (31 cybersec + 5 dystopian)                │    │
       │  │  └──────────────────┬──────────────────────────┘    │
       │  │                     │                               │
       │  │                     ▼                               │
       │  │  ┌──────────────────────────────────────────────────┤
       │  │  │            LAYER 3 — MCP TOOLS                  │
       │  │  │                                                 │
       │  │  │  src/csmcp/cybersec/  →  31 tools (SDK compat)  │
       │  │  │  src/csmcp/dystopian.py → 5 crypto tools        │
       │  │  │  src/omniroute_mcp/   →  27 OmniRoute tools     │
       │  │  └───────┬──────────────────┬──────────────────────┘
       │  │          │                  │
       │  │          ▼                  ▼
       │  │  ┌──────────────┐   ┌──────────────────┐
       │  │  │  LAYER 6     │   │  Crypto Layer    │
       │  │  │  DATABASE    │   │  src/crypto/     │
       │  │  │              │   │                  │
       │  │  │  PostgreSQL  │   │  Ed25519 signing │
       │  │  │  :5432       │   │  BLAKE2b hashing │
       │  │  │  40+ models  │   │  Argon2id KDF    │
       │  │  │  65 tables   │   │  AES-256-GCM     │
       │  │  └──────────────┘   └──────────────────┘
       │  │
       │  ▼
┌──────┴──────────────────────────────────────────────────────┐
│               LAYER 7 — OBSERVABILITY                       │
│                                                             │
│  src/dashboard/   → 41 endpoints (8 API modules + 4 SSE)   │
│  src/telemetry/   → In-process ring buffer (p50/p95/p99)   │
│  src/opensearch/  → Async bulk writer → OpenSearch :9200    │
│                                                             │
│  Dual-write: ring buffer + OpenSearch (3 daily indices)     │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer Details

### Layer 1 — ASGI Application

| Property         | Value                   |
|------------------|-------------------------|
| **Entry point**  | `src/proxy/asgi.py`     |
| **Framework**    | Starlette               |
| **Server**       | Uvicorn                 |
| **Default port** | 8000 (HTTP), 8433 (TLS) |

**What it does:**
The ASGI application is the single HTTP entry point for the entire platform.
It creates a Starlette application and mounts every subsystem at a distinct
URL prefix.  All cross-cutting concerns — CORS, middleware, lifespan
management — live here.

**Mount table:**

| Path                      | Target                      | Layer             |
|---------------------------|-----------------------------|-------------------|
| `/v1/*`                   | `create_proxy_router()`     | AI Proxy (2)      |
| `/dashboard/*`            | `create_dashboard_router()` | Observability (7) |
| `/a2a`                    | `A2AServer`                 | A2A Protocol (4)  |
| `/.well-known/agent.json` | Agent card                  | A2A Protocol (4)  |

**Connects to:**
- Layer 2 (AI Proxy) — forwards `/v1/chat/completions` and model endpoints
- Layer 4 (A2A) — forwards JSON-RPC requests on `/a2a`
- Layer 7 (Dashboard) — forwards all `/dashboard/*` requests
- Layer 6 (Database) — lifespan hooks call `init_tortoise_async()` on startup

---

### Layer 2 — AI Proxy

| Property               | Value                                 |
|------------------------|---------------------------------------|
| **Root**               | `src/ai_proxy/`                       |
| **Key files**          | `routes.py`, `combo.py`, `providers/` |
| **Providers**          | 60                                    |
| **Routing strategies** | 13                                    |

**What it does:**
Routes LLM requests across 60 providers using 13 intelligent strategies.
Includes circuit breaker, budget guard, cost tracking, and usage analytics.

**Routing strategies (13):**

| Strategy            | Description                             |
|---------------------|-----------------------------------------|
| `PRIORITY`          | Ordered provider preference list        |
| `ROUND_ROBIN`       | Cycle through providers evenly          |
| `COST_OPTIMIZED`    | Cheapest provider first                 |
| `WEIGHTED`          | Weighted random selection               |
| `RANDOM`            | Uniform random                          |
| `LEAST_USED`        | Provider with fewest recent calls       |
| `FILL_FIRST`        | Fill one provider before moving to next |
| `P2C`               | Power-of-two-choices (load-aware)       |
| `STRICT_RANDOM`     | True random, no fallback                |
| `AUTO`              | Automatic strategy selection            |
| `LKGP`              | Last-known-good provider                |
| `CONTEXT_OPTIMIZED` | Best provider for context window size   |
| `CONTEXT_RELAY`     | Relay context across providers          |

**Custom headers:**

| Header              | Purpose                                |
|---------------------|----------------------------------------|
| `x-provider`        | Force a specific provider              |
| `x-prefer-free`     | Prefer free-tier providers             |
| `x-max-cost-per-1k` | Budget filter (max cost per 1K tokens) |

**Connects to:**
- Layer 1 (ASGI) — mounted at `/v1`
- Layer 3 (MCP Tools) — `proxy.py` tools query proxy status endpoints
- Layer 7 (Observability) — emits telemetry events per request

---

### Layer 3 — MCP Tools

| Property           | Value                              |
|--------------------|------------------------------------|
| **Cybersec root**  | `src/csmcp/cybersec/`              |
| **Crypto root**    | `src/csmcp/dystopian.py`           |
| **OmniRoute root** | `src/omniroute_mcp/`               |
| **Total tools**    | 63 (31 + 5 + 27)                   |
| **SDK pattern**    | `@tool` decorator + `sdk_result()` |

**What it does:**
Provides 63 MCP tools that Claude Code and agents can invoke.  The cybersec
server uses an SDK-compatible pattern (`@tool` decorator from
`csmcp/_sdk_compat.py`), the dystopian server provides crypto operations, and
the OmniRoute server (TypeScript/Bun) bridges to an external AI gateway.

**Tool categories (cybersec — 31 tools):**

| Category     | Tools                                                                                                                                                                             |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Findings     | `add_finding`, `add_ioc`, `query_findings`, `update_risk_register`                                                                                                                |
| Database     | `db_healthcheck`, `bootstrap_intelligence`                                                                                                                                        |
| Intelligence | `suggest_mitre`, `get_project_memory`                                                                                                                                             |
| Layers       | `share_to_layers`, `get_layer_value`                                                                                                                                              |
| Cache        | `cache_lookup`, `cache_store`, `cache_analytics`, `cache_invalidate`                                                                                                              |
| Proxy        | `proxy_chat`, `proxy_providers`, `proxy_models`, `proxy_usage`, `proxy_cost`, `simulate_route`, `set_budget_guard`, `get_circuit_breakers`, `explain_route`, `routing_strategies` |
| Session      | `session_snapshot`, `agent_registry`, `best_provider`                                                                                                                             |
| Cases        | `case_open`, `case_status`                                                                                                                                                        |

**Tool categories (crypto — 5 tools):**

| Tool                      | Purpose                    |
|---------------------------|----------------------------|
| `crypto_generate_keypair` | Generate Ed25519 key pair  |
| `crypto_sign_artifact`    | Sign artifact with Ed25519 |
| `crypto_verify_artifact`  | Verify Ed25519 signature   |
| `crypto_list_keys`        | List available key pairs   |
| `crypto_rotate_key`       | Rotate signing key         |

**Tool categories (OmniRoute — 27 tools):**
Health, combos, routing, quota, cost, models, web search, memory, and skills
management — all via HTTP calls to `OMNIROUTE_BASE_URL`.

**SDK pattern:**
```python
@tool("tool_name", "description", {"param": {"type": "string", "description": "..."}})
async def _tool_fn(args: dict[str, Any]) -> dict:
    value = args.get("param", "default")
    return sdk_result({"key": value})
```

**Connects to:**
- Layer 5 (Agents) — agents invoke tools via SDK bridge
- Layer 6 (Database) — tools read/write via Tortoise ORM
- Layer 2 (AI Proxy) — `proxy.py` tools query proxy endpoints
- Crypto layer (`src/crypto/`) — dystopian tools use key manager, SSL signer
- OmniRoute gateway (`:20128`) — OmniRoute MCP calls external gateway

---

### Layer 4 — A2A Protocol

| Property      | Value                                   |
|---------------|-----------------------------------------|
| **Root**      | `src/a2a/`                              |
| **Protocol**  | JSON-RPC 2.0                            |
| **Key files** | `server.py`, `agent.py`, `agent_sdk.py` |
| **Transport** | HTTP POST + SSE streaming               |

**What it does:**
Implements the Agent-to-Agent (A2A) protocol for inter-agent communication.
External clients send JSON-RPC requests; the `CybersecA2AAgent` parses
intent via keyword routing and delegates to the appropriate specialist agent
through the Agent SDK.

**Endpoints:**

| Method | Path                      | Purpose                               |
|--------|---------------------------|---------------------------------------|
| POST   | `/a2a`                    | JSON-RPC dispatch                     |
| GET    | `/a2a/stream/{task_id}`   | SSE streaming for task updates        |
| GET    | `/.well-known/agent.json` | Agent card (capability advertisement) |

**JSON-RPC methods:**
- `tasks/send` — submit a new investigation task
- `tasks/get` — retrieve task status and results
- `tasks/cancel` — cancel a running task

**Connects to:**
- Layer 1 (ASGI) — mounted at `/a2a`
- Layer 5 (Agents) — `run_agent_query()` in `agent_sdk.py` invokes agents
- Layer 2 (AI Proxy) — agent SDK routes through `ANTHROPIC_BASE_URL`
- Layer 6 (Database) — task state persisted via Tortoise ORM

---

### Layer 5 — Agent System

| Property        | Value                                   |
|-----------------|-----------------------------------------|
| **Root**        | `.claude/agents/`                       |
| **Skills root** | `.claude/skills/`                       |
| **Agents**      | 48 (37 main + 3 teams + 8 sub-agents)   |
| **Skills**      | 942                                     |
| **Hooks**       | `.claude/hooks/` + `src/agent/hooks.py` |

**What it does:**
Defines the specialist agent roster — each agent is a Markdown file with YAML
frontmatter specifying model, tools, and system prompt.  The Agent SDK
(`src/a2a/agent_sdk.py`) loads these definitions, injects 36 MCP tools
(31 cybersec + 5 dystopian), and creates `claude_agent_sdk` options that
route all LLM calls through the AI Proxy.

**Agent build flow:**
```
agent_sdk.py
  → build_agent_options(agent_name)
     → loads .claude/agents/{agent_name}.md
     → parses frontmatter (model, tools, allowed_tools)
     → creates MCP server via create_sdk_mcp_server()
     → sets ANTHROPIC_BASE_URL = http://localhost:8000/v1
     → returns AgentOptions ready for claude_agent_sdk.query()
```

**Hooks pipeline (two systems):**

| System           | Location             | Execution              |
|------------------|----------------------|------------------------|
| Filesystem hooks | `.claude/hooks/`     | Subprocess (`python3`) |
| SDK hooks        | `src/agent/hooks.py` | In-process             |

| Hook Phase  | Hook            | Purpose                   |
|-------------|-----------------|---------------------------|
| PreToolUse  | `security_hook` | Blocks dangerous commands |
| PreToolUse  | `audit_hook`    | Logs all tool calls       |
| PostToolUse | `ioc_hook`      | Extracts IOCs from output |
| Stop        | `cost_hook`     | Logs session cost         |

**Memory tiers (3-tier hierarchy):**
```
.memory/system/    → Global defaults (read-only)
.memory/project/   → Project-level context
.memory/session/   → Ephemeral session state
```

**Connects to:**
- Layer 2 (AI Proxy) — all LLM calls route through proxy
- Layer 3 (MCP Tools) — 36 tools injected into every agent
- Layer 4 (A2A) — A2A agent delegates to specialist agents

---

### Layer 6 — Database

| Property   | Value                         |
|------------|-------------------------------|
| **Root**   | `src/db/`                     |
| **ORM**    | Tortoise ORM (asyncpg driver) |
| **Models** | 40+                           |
| **Tables** | 65                            |
| **Port**   | 5432                          |

**What it does:**
PostgreSQL stores all persistent state — findings, IOCs, MITRE mappings,
CVE/CWE/CAPEC records, risk registers, case intakes, agent registrations,
NIST CSF/AI RMF frameworks, and telemetry metadata.  All access is async
via Tortoise ORM.

**Key model groups:**

| Group         | Models                                          | Purpose                |
|---------------|-------------------------------------------------|------------------------|
| Findings      | `Finding`, `IOC`, `Risk`                        | Investigation results  |
| Intelligence  | `MitreTechniqueIntel`, `ForensicMITRETechnique` | MITRE ATT&CK           |
| Cases         | `CaseIntake`                                    | Case management        |
| Frameworks    | NIST CSF 2.0, NIST AI RMF 1.0                   | Compliance             |
| CVE/CWE/CAPEC | Vulnerability databases                         | Threat intel           |
| POC           | `POCIntel`                                      | Proof-of-concept intel |

**Initialization:**
```python
# src/db/db.py
await init_tortoise_async()   # Called during ASGI lifespan startup
await get_database_health_async()  # Health check for /dashboard/health
```

**Connects to:**
- Layer 3 (MCP Tools) — tools CRUD via Tortoise ORM
- Layer 7 (Dashboard) — dashboard queries all models for display
- Layer 4 (A2A) — task state stored in DB
- Layer 1 (ASGI) — lifespan hooks initialize DB connection pool

---

### Layer 7 — Observability

| Property                | Value                              |
|-------------------------|------------------------------------|
| **Dashboard root**      | `src/dashboard/`                   |
| **Telemetry root**      | `src/telemetry/`                   |
| **OpenSearch root**     | `src/opensearch/`                  |
| **Dashboard endpoints** | 41 (8 API modules + 4 SSE streams) |
| **OpenSearch port**     | 9200                               |
| **OS Dashboards port**  | 5601                               |

**What it does:**
Provides real-time and historical observability across the entire platform.
The telemetry layer dual-writes to an in-process ring buffer (for immediate
p50/p95/p99 stats) and to OpenSearch (for long-term storage and querying).
The dashboard exposes 41 endpoints for the web UI.

**Dashboard API modules (8):**

| Module             | Purpose                        |
|--------------------|--------------------------------|
| `core`             | Health, status, overview       |
| `agents`           | Agent listing, query execution |
| `forensic`         | Findings, IOCs, MITRE data     |
| `ops`              | Operations, cost, usage        |
| `tables`           | Generic table CRUD             |
| `settings`         | Configuration management       |
| `team_builder`     | Team composition               |
| `opensearch_stats` | OpenSearch cluster metrics     |

**SSE streams (4):**
Real-time event streams for telemetry, findings, agent activity, and system
alerts — pushed to connected browsers at configurable intervals.

**Telemetry dual-write:**
```
Event occurs (tool call, proxy request, error)
  → telemetry/store.py
     ├─→ In-process ring buffer  (immediate: p50/p95/p99)
     └─→ OpenSearch bulk writer  (durable: 3 daily-rollover indices)
```

**OpenSearch indices (3, daily rollover):**

| Index Pattern          | Content              |
|------------------------|----------------------|
| `telemetry-YYYY.MM.DD` | Performance metrics  |
| `audit-YYYY.MM.DD`     | Security audit trail |
| `api-usage-YYYY.MM.DD` | API usage analytics  |

**OpenSearch client (`src/opensearch/client.py`):**
- Async singleton connection
- Buffered bulk writer: 100 documents or 5-second flush (whichever first)

**Connects to:**
- Layer 1 (ASGI) — mounted at `/dashboard`
- Layer 6 (Database) — queries all models for display
- Layer 2 (AI Proxy) — queries provider/routing status
- Layer 3 (MCP Tools) — telemetry store receives tool execution events
- OpenSearch (:9200) — bulk writes for durable storage

---

## Key Integration Points

### 1. ASGI → AI Proxy

```
src/proxy/asgi.py
  └─ mounts create_proxy_router() at /v1
       └─ POST /v1/chat/completions
            → routes.chat_completions()
            → combo.py (strategy selection)
            → provider executor
            → response
```

**13 routing strategies** govern how `combo.py` selects a provider for each
request.  Custom headers (`x-provider`, `x-prefer-free`, `x-max-cost-per-1k`)
allow callers to influence routing at the request level.

---

### 2. ASGI → Dashboard

```
src/proxy/asgi.py
  └─ mounts create_dashboard_router() at /dashboard
       └─ 41 endpoints across 8 API modules + 4 SSE streams
            → Tortoise ORM queries (Layer 6)
            → AI Proxy status queries (Layer 2)
            → Telemetry snapshots (Layer 7)
```

---

### 3. ASGI → A2A

```
src/proxy/asgi.py
  └─ mounts A2AServer at /
       ├─ POST /a2a
       │    → JSON-RPC dispatch
       │    → CybersecA2AAgent
       │    → skill handler
       │    → run_agent_query()
       │    → Agent SDK → AI Proxy
       │
       ├─ GET /a2a/stream/{task_id}
       │    → SSE streaming
       │
       └─ GET /.well-known/agent.json
            → Agent card
```

---

### 4. Agent SDK → AI Proxy

```
src/a2a/agent_sdk.py
  └─ build_agent_options()
       ├─ ANTHROPIC_BASE_URL = http://localhost:8000/v1
       ├─ Agent model from frontmatter (haiku / sonnet / opus)
       └─ claude_agent_sdk.query()
            → HTTP POST to AI Proxy
            → combo.py routes to correct provider
```

All agent LLM calls are routed through the local AI Proxy, ensuring
consistent cost tracking, circuit breaking, and strategy enforcement
regardless of which agent or model is invoked.

---

### 5. Agent SDK → MCP Tools

```
src/csmcp/_sdk_compat.py
  └─ @tool decorator registers tools
  └─ SdkMcpServer collects all decorated tools

src/a2a/agent_sdk.py
  └─ create_sdk_mcp_server()
       └─ Builds in-process MCP server from all decorated tools
       └─ Injected into agent options (36 tools total)
```

Tools access:
- **Database** via Tortoise ORM (async)
- **Crypto** via `src/crypto/` (key manager, SSL signer)
- **AI Proxy** via proxy tool endpoints (routing info, cost data)

---

### 6. MCP Tools → Database

| Tool Module       | DB Models Used                                         |
|-------------------|--------------------------------------------------------|
| `findings.py`     | `Finding`, `IOC`, `Risk`                               |
| `intelligence.py` | `MitreTechniqueIntel`, `ForensicMITRETechnique`        |
| `cases.py`        | `CaseIntake`                                           |
| `db.py`           | `init_tortoise_async()`, `get_database_health_async()` |
| `poc.py`          | `POCIntel`                                             |

All database access is **async** — no synchronous DB calls anywhere in the
codebase.  Tortoise ORM manages connection pooling via asyncpg.

---

### 7. MCP Tools → AI Proxy

The `proxy.py` module exposes **10 tools** that call AI Proxy endpoints:

| Tool                   | Proxy Endpoint              |
|------------------------|-----------------------------|
| `proxy_chat`           | `POST /v1/chat/completions` |
| `proxy_providers`      | `GET /v1/providers`         |
| `proxy_models`         | `GET /v1/models`            |
| `proxy_usage`          | `GET /v1/usage`             |
| `proxy_cost`           | `GET /v1/cost`              |
| `simulate_route`       | `POST /v1/simulate`         |
| `set_budget_guard`     | `POST /v1/budget`           |
| `get_circuit_breakers` | `GET /v1/circuit-breakers`  |
| `explain_route`        | `GET /v1/explain`           |
| `routing_strategies`   | `GET /v1/strategies`        |

---

### 8. OmniRoute MCP → OmniRoute Gateway

```
src/omniroute_mcp/server.ts
  └─ HTTP calls to OMNIROUTE_BASE_URL
       └─ Default: http://localhost:20128
       └─ 27 tools (health, combos, routing, quota, cost,
          models, web search, memory, skills)
```

Self-contained TypeScript server, runs via **Bun**.  Completely independent
of the Python stack — communicates only via HTTP to the OmniRoute gateway.

---

### 9. Telemetry → OpenSearch

```
src/telemetry/store.py
  └─ Dual-write on every event:
       ├─ In-process ring buffer  →  immediate stats (p50/p95/p99)
       └─ opensearch/client.py    →  async bulk writer
            └─ Buffered: 100 docs OR 5-second flush
            └─ 3 daily-rollover indices:
                 ├─ telemetry-YYYY.MM.DD
                 ├─ audit-YYYY.MM.DD
                 └─ api-usage-YYYY.MM.DD
```

---

### 10. Dashboard → Telemetry

```
GET  /api/telemetry     → MetricsStore.snapshot()
                             → Ring-buffer stats (p50/p95/p99)

SSE  /sse/telemetry     → TelemetryCollector
                             → 15-second polling interval
                             → Real-time push to browser
```

---

### 11. Hooks Pipeline

Two complementary hook systems run in parallel:

```
┌──────────────────────────────┐    ┌──────────────────────────────┐
│  FILESYSTEM HOOKS            │    │  SDK HOOKS                   │
│  .claude/hooks/              │    │  src/agent/hooks.py          │
│  Execution: subprocess       │    │  Execution: in-process       │
│  Runtime: python3            │    │  Runtime: async Python       │
└──────────────┬───────────────┘    └──────────────┬───────────────┘
               │                                   │
               ▼                                   ▼
       ┌───────────────────────────────────────────────────┐
       │              HOOK EXECUTION PIPELINE              │
       │                                                   │
       │  PreToolUse:                                      │
       │    ├─ security_hook  → blocks dangerous commands  │
       │    └─ audit_hook     → logs all tool calls        │
       │                                                   │
       │  PostToolUse:                                     │
       │    └─ ioc_hook       → extracts IOCs from output  │
       │                                                   │
       │  Stop:                                            │
       │    └─ cost_hook      → logs session cost          │
       └───────────────────────────────────────────────────┘
```

**3-tier memory hierarchy:**
```
.memory/system/     ← Global defaults (read-only baseline)
    ▲
.memory/project/    ← Project-level overrides
    ▲
.memory/session/    ← Ephemeral session state (highest priority)
```

---

### 12. Crypto Layer

```
src/crypto/
  ├─ Ed25519   → Digital signatures (artifact signing)
  ├─ BLAKE2b   → 256-bit content hashing
  ├─ Argon2id  → Key derivation (mem=262144, iters=4)
  └─ AES-256-GCM → Symmetric encryption
```

**Consumers:**

| Consumer            | Usage                                         |
|---------------------|-----------------------------------------------|
| Dystopian MCP tools | Key generation, artifact signing/verification |
| Hooks               | Evidence integrity checksums                  |
| A2A agent           | Artifact signing skill                        |

**Key storage:** `DYSTOPIAN_KEYS_DIR` (default: `/etc/dystopian-crypto/keys`)

---

## Request Flow Examples

### Example 1: Agent Query via Dashboard

```
Browser
  │
  │  POST /dashboard/api/agent-query
  │  Body: {prompt: "Analyze suspicious binary", agent_name: "reverse-engineer"}
  │
  ▼
api_agent_query()                          ← src/dashboard/api/agents.py
  │
  ▼
run_agent_query("reverse-engineer", prompt)  ← src/a2a/agent_sdk.py
  │
  ▼
build_agent_options()
  ├─ Loads .claude/agents/reverse-engineer.md
  ├─ Parses frontmatter → model: sonnet
  ├─ Creates SDK MCP server with 36 tools
  └─ Sets ANTHROPIC_BASE_URL = http://localhost:8000/v1
  │
  ▼
claude_agent_sdk.query()
  │
  │  POST http://localhost:8000/v1/chat/completions
  │
  ▼
AI Proxy combo.py
  ├─ Strategy: COST_OPTIMIZED (or configured default)
  ├─ Selects provider: e.g., Anthropic Claude Sonnet
  └─ Forwards to provider API
  │
  ▼
Claude model processes prompt
  ├─ May invoke MCP tool: add_finding(title, severity, description)
  │    → findings.py → Finding.create() → PostgreSQL INSERT
  ├─ May invoke MCP tool: suggest_mitre(technique_name)
  │    → intelligence.py → MitreTechniqueIntel.filter() → PostgreSQL SELECT
  └─ Returns analysis result
  │
  ▼
Response streams back:
  SDK → agent_sdk.py → api_agent_query() → HTTP response → Browser
```

---

### Example 2: External A2A Request

```
External A2A Client
  │
  │  POST /a2a
  │  Body: {
  │    "jsonrpc": "2.0",
  │    "method": "tasks/send",
  │    "params": {"message": "Analyze CVE-2024-1234"},
  │    "id": 1
  │  }
  │
  ▼
A2AServer.handle_rpc()                     ← src/a2a/server.py
  │
  ▼
CybersecA2AAgent.execute()                 ← src/a2a/agent.py
  │
  ├─ Keyword routing: "cve" detected
  ▼
_handle_cve()
  │
  ▼
run_agent_query("cybersec-analyst", enriched_prompt)
  │
  ▼
Agent SDK → AI Proxy → Claude → MCP tools → DB queries
  │
  ├─ Task stored in DB + in-memory store
  │
  ▼
JSON-RPC response:
  {
    "jsonrpc": "2.0",
    "result": {"task_id": "abc-123", "status": "completed", "output": {...}},
    "id": 1
  }

Client can also poll:
  GET /a2a/stream/abc-123  →  SSE updates in real time
```

---

### Example 3: MCP Tool Execution (Claude Code)

```
Claude Code (local IDE)
  │
  │  stdio transport
  │  uv run python -m csmcp.cybersec.server
  │
  ▼
MCP Server (in-process)
  │
  │  Tool call: add_finding
  │  Args: {title: "Suspicious SUID binary", severity: "high",
  │         description: "Found /usr/local/bin/backdoor with SUID bit"}
  │
  ▼
findings.py → add_finding()
  │
  ▼
Finding.create(
    title="Suspicious SUID binary",
    severity="high",
    description="Found /usr/local/bin/backdoor with SUID bit"
)
  │
  │  Tortoise ORM → asyncpg → PostgreSQL INSERT
  │
  ▼
sdk_result({"id": 42, "title": "Suspicious SUID binary", ...})
  │
  │  JSON response via stdio
  │
  ▼
Claude Code receives result and continues investigation
```

---

## Port Map & Services

```
┌─────────────────────────────────────────────────────────────────┐
│                        PORT MAP                                 │
├───────┬───────────────────┬───────────────┬─────────────────────┤
│ Port  │ Service           │ Layer         │ Purpose             │
├───────┼───────────────────┼───────────────┼─────────────────────┤
│ 8000  │ ASGI (uvicorn)    │ Application   │ HTTP entry point    │
│ 8080  │ ASGI alt          │ Application   │ Docker exposed HTTP │
│ 8433  │ ASGI TLS          │ Application   │ HTTPS (TLS certs)   │
│ 5432  │ PostgreSQL        │ Database      │ 40+ models, 65 tbl  │
│ 6379  │ Redis             │ Cache         │ Rate limit, session │
│ 9200  │ OpenSearch        │ Observability │ Telemetry/audit/use │
│ 5601  │ OS Dashboards     │ Observability │ Kibana-like UI      │
│ 20128 │ OmniRoute         │ AI Gateway    │ External AI routing │
└───────┴───────────────────┴───────────────┴─────────────────────┘
```

---

## Docker Compose Services

| Service                          | Image                                            | Depends On           | Healthcheck             |
|----------------------------------|--------------------------------------------------|----------------------|-------------------------|
| `cybersec-postgres`              | Custom (with extensions)                         | —                    | `pg_isready`            |
| `cybersec-dashboard`             | Custom (Python 3.14)                             | postgres (healthy)   | `curl /health`          |
| `cybersec-redis`                 | Custom                                           | —                    | `redis-cli ping`        |
| `cybersec-opensearch`            | `opensearchproject/opensearch:2.17.1`            | —                    | `curl /_cluster/health` |
| `cybersec-opensearch-dashboards` | `opensearchproject/opensearch-dashboards:2.17.1` | opensearch (healthy) | —                       |

**Startup order:**
```
cybersec-postgres  ─────────────────────┐
cybersec-redis  ────────────────────────┤
cybersec-opensearch  ───────────────────┤
                                        ▼
                              cybersec-dashboard
                                        │
                              cybersec-opensearch-dashboards
                                (waits for opensearch)
```

---

## Environment Variables Reference

### Database

| Variable               | Default              | Purpose             |
|------------------------|----------------------|---------------------|
| `CYBERSEC_DB_HOST`     | `localhost`          | PostgreSQL hostname |
| `CYBERSEC_DB_PORT`     | `5432`               | PostgreSQL port     |
| `CYBERSEC_DB_USER`     | `cybersec`           | Database user       |
| `CYBERSEC_DB_PASSWORD` | —                    | Database password   |
| `CYBERSEC_DB_NAME`     | `cybersec_forensics` | Database name       |

### AI Proxy

| Variable             | Default                    | Purpose                   |
|----------------------|----------------------------|---------------------------|
| `ANTHROPIC_API_KEY`  | —                          | Anthropic API key         |
| `OPENAI_API_KEY`     | —                          | OpenAI API key            |
| `ANTHROPIC_BASE_URL` | `http://localhost:8000/v1` | Route through local proxy |

### Scope

| Variable              | Default      | Purpose                       |
|-----------------------|--------------|-------------------------------|
| `CYBERSEC_WORKSPACE`  | `default`    | Workspace isolation           |
| `CYBERSEC_PROJECT`    | `my-project` | Project identifier            |
| `CYBERSEC_SESSION_ID` | —            | Session identifier (optional) |

### Intelligence

| Variable                            | Default                               | Purpose                    |
|-------------------------------------|---------------------------------------|----------------------------|
| `CYBERSEC_INTEL_DIR`                | `./data/cybersec-shared/intelligence` | Intel data directory       |
| `CYBERSEC_BOOTSTRAP_INTEL_ON_START` | `false`                               | Auto-seed intel on startup |

### Crypto

| Variable             | Default                      | Purpose             |
|----------------------|------------------------------|---------------------|
| `DYSTOPIAN_KEYS_DIR` | `/etc/dystopian-crypto/keys` | Ed25519 key storage |

### OmniRoute

| Variable             | Default                  | Purpose               |
|----------------------|--------------------------|-----------------------|
| `OMNIROUTE_BASE_URL` | `http://localhost:20128` | OmniRoute gateway URL |

---

*Last updated: auto-generated — see `docs/` for related documentation.*

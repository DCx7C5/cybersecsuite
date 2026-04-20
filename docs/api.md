# API Reference

Complete reference for all HTTP endpoints exposed by CyberSecSuite.

Base URL: `http://localhost:8000` (default)

---

## Health

### `GET /health`

Database and system health check.

**Response:**
```json
{
  "status": "ok",
  "initialized": true,
  "intel_bootstrapped": true,
  "table_count": 50,
  "config": {
    "database": "cybersec_forensics",
    "host": "localhost",
    "port": 5432
  }
}
```

Returns `200` when healthy, `503` when DB is unavailable.

---

## Agent Card Discovery

### `GET /.well-known/agent.json`

Returns the orchestrator's A2A agent card (Google A2A spec).

**Response:**
```json
{
  "name": "CyberSecOrchestrator",
  "description": "...",
  "url": "http://localhost:8000",
  "version": "1.0.0",
  "capabilities": {"streaming": true},
  "authentication": {"schemes": ["ed25519"]},
  "skills": [...]
}
```

---

## A2A — Agent-to-Agent Protocol

All A2A endpoints accept and return JSON-RPC 2.0. Mounted at `/a2a/` and `/` (root).

### `POST /a2a` — `tasks/send`

Send a task to the orchestrator.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "id": 1,
  "params": {
    "message": {
      "role": "user",
      "parts": [{"type": "text", "text": "@cybersec-analyst CVE-2024-1234"}]
    },
    "sessionId": "optional-session-id"
  }
}
```

**Routing syntax in message text:**
| Prefix | Behavior |
|--------|---------|
| `@agent-name` | Route to specific agent |
| `@fanout` | Send to all agents in parallel |
| *(none)* | Auto-route via keyword + skill matching |
| `list agents` | List all registered agents |

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "id": "task-uuid",
    "status": {"state": "submitted"},
    "sessionId": "session-uuid"
  }
}
```

---

### `POST /a2a` — `tasks/get`

Get the current state of a task.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/get",
  "id": 2,
  "params": {"id": "task-uuid"}
}
```

**Task states:** `submitted` → `working` → `completed` | `failed` | `cancelled`

---

### `POST /a2a` — `tasks/cancel`

Cancel a running task.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/cancel",
  "id": 3,
  "params": {"id": "task-uuid"}
}
```

---

### `GET /a2a/stream/{task_id}` (SSE)

Stream task updates as Server-Sent Events.

```bash
curl -N http://localhost:8000/a2a/stream/task-uuid
```

Events: `task_update`, `task_complete`, `task_error`

---

## AI Proxy — OpenAI-Compatible

Mounted at `/v1/`. Drop-in replacement for OpenAI API.

### `POST /v1/chat/completions`

Multi-provider chat completion.

**Request** (OpenAI format):
```json
{
  "model": "auto",
  "messages": [
    {"role": "user", "content": "Analyze this IOC: 192.168.1.100"}
  ],
  "stream": false
}
```

Special `model` values:
| Value | Behavior |
|-------|---------|
| `auto` | Auto-route based on context |
| `provider:model` | Force specific provider + model (e.g. `anthropic:claude-3-5-sonnet`) |
| `free` | Cost-optimized routing (free-tier providers first) |

**Response:** Standard OpenAI `ChatCompletion` format.

---

### `GET /v1/models`

List all available models across all active providers.

**Response:**
```json
{
  "object": "list",
  "data": [
    {"id": "claude-3-5-sonnet-20241022", "object": "model", "owned_by": "anthropic"},
    ...
  ]
}
```

---

## Dashboard API

All dashboard JSON endpoints are mounted at `/api/*`. The dashboard page is mounted at `/`, and real-time streams at `/sse/*`.

### `GET /api/overview`
System overview: version, uptime, active modules.

### `GET /api/providers`
All 9 AI providers with status (`active`/`inactive`/`tripped`) and model counts.

### `GET /api/usage`
Token + cost usage statistics, grouped by provider and model.

### `GET /api/health`
Full health check across all subsystems.

### `GET /api/crypto`
Crypto module status: key files present, algorithm info, last signing timestamp.

### `GET /api/a2a`
A2A server stats: agent count, active tasks, completed tasks, failure count.

### `GET /api/db-counts`
Row counts for all 50 ORM models.

### `GET /api/investigations`
Recent investigations (paginated). Query params: `limit`, `offset`, `status`.

### `GET /api/agents`
All loaded agents: name, model, skill count, A2A URL.

### `GET /api/routing`
Circuit breaker states + routing strategy usage histogram.

### `GET /api/agent-factory`
AGENT_FACTORY configuration and available model tiers.

### `GET /api/cases`
Open investigation cases (summary list).

### `GET /api/tasks`
Recent A2A tasks: state, assigned agent, timestamps. Query params: `limit`, `state`.

### `POST /api/tasks/{id}/cancel`
Cancel a running A2A task by ID.

### `GET /api/prompts`
Prompt template catalog.

### `POST /api/agent-query`
Single-shot agent query endpoint used by the Agent Query panel.

### `POST /api/agent-run`
Start streaming chat execution.

**Request:**
```json
{
  "agent": "cybersec-agent",
  "prompt": "Analyze IOC 10.0.0.5",
  "stream": true
}
```

**Response:**
```json
{
  "task_id": "uuid"
}
```

### `DELETE /api/agent-run/{task_id}`
Cancel an active chat stream task.

---

## Dashboard SSE

### `GET /sse/cases`
Live stream of case events: `case_opened`, `case_updated`, `case_closed`.

### `GET /sse/tasks`
Live stream of A2A task state changes.

### `GET /sse/health`
Periodic health pulse (every 30 seconds).

```bash
# Example: stream health events
curl -N http://localhost:8000/sse/health
```

### `GET /sse/agent-run/{task_id}`
Streaming chat events emitted by `POST /api/agent-run`.

Event types:
- `token` → incremental assistant text chunks
- `tool_start` → tool invocation start marker
- `tool_done` → tool completion marker with elapsed ms
- `done` → terminal success event (`elapsed_ms`, `stop_reason`, optional `text`)
- `error` → terminal failure event

---

## Dashboard UI

### `GET /`
Full monitoring dashboard HTML page.

---

## Error Responses

### HTTP errors

```json
{"detail": "Not found"}
```

Standard HTTP status codes: `400` (bad request), `404` (not found), `500` (internal error), `503` (service unavailable).

### JSON-RPC errors (A2A)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32600,
    "message": "Invalid Request",
    "data": "..."
  }
}
```

Standard A2A error codes defined in `src/a2a/models.py` (`A2AErrorCodes`).

---

## Accounts API

API key management with vault-backed storage.

### `GET /api/accounts`

List all accounts.

**Response:**
```json
{
  "accounts": [
    {
      "vault_key": "openai-abc123",
      "provider_id": "openai",
      "label": "My OpenAI Key",
      "active": true,
      "test_status": "success",
      "last_tested_at": "2026-04-19T12:00:00Z"
    }
  ]
}
```

### `POST /api/accounts`

Create a new account.

**Request:**
```json
{
  "provider_id": "openai",
  "api_key": "sk-...",
  "label": "My Key"
}
```

### `GET /api/accounts/{vault_key}`

Get a single account.

### `PUT /api/accounts/{vault_key}`

Update an account (set_active, rotate, test).

**Request:**
```json
{
  "action": "set_active"
}
```

Actions: `set_active`, `rotate`, `test`

### `DELETE /api/accounts/{vault_key}`

Delete an account.

### `GET /api/accounts/resolve?provider_id={id}`

Resolve API key for a provider (checks vault first, then env var).

---

## SDK Options

### `GET /api/sdk/options`
Get merged runtime options (MCPs, agents, model, permission_mode).

**Query params:** `?id=<project_id>` for project scope.

**Response:**
```json
{
  "mcps": {"cybersec": true, "dystopian": true},
  "agents": {"filesystem-analyst": true, "memory-analyst": true},
  "permission_mode": null,
  "model": null,
  "hooks": null
}
```

### `POST /api/sdk/options`
Update options for a scope layer.

**Query params:** `?scope=global|app|project` (default: global), `?id=<project_id>` for project.

**Request:**
```json
{
  "mcps": {"cybersec": false},
  "model": "sonnet"
}
```

### `GET /api/sdk/options/scopes`
Get raw snapshot of all scope layers (before merge).

### `DELETE /api/sdk/options`
Reset a scope to defaults.

---

## Startup

### `GET /api/startup/status`

Returns startup status including first-run info and marketplace.

**Response:**
```json
{
  "is_first_run": false,
  "marketplace": {"providers": [], "skills": [], "agents": []},
  "cybersecsuite_dir": "/home/user/.cybersecsuite"
}
```

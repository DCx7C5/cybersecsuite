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

### `GET /a2a/tasks/{id}/stream` (SSE)

Stream task updates as Server-Sent Events.

```bash
curl -N http://localhost:8000/a2a/tasks/task-uuid/stream
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

All endpoints return JSON. Mounted at `/dashboard/api/`.

### `GET /dashboard/api/overview`
System overview: version, uptime, active modules.

### `GET /dashboard/api/providers`
All 9 AI providers with status (`active`/`inactive`/`tripped`) and model counts.

### `GET /dashboard/api/usage`
Token + cost usage statistics, grouped by provider and model.

### `GET /dashboard/api/health`
Full health check across all subsystems.

### `GET /dashboard/api/crypto`
Crypto module status: key files present, algorithm info, last signing timestamp.

### `GET /dashboard/api/a2a`
A2A server stats: agent count, active tasks, completed tasks, failure count.

### `GET /dashboard/api/db/counts`
Row counts for all 50 ORM models.

### `GET /dashboard/api/investigations`
Recent investigations (paginated). Query params: `limit`, `offset`, `status`.

### `GET /dashboard/api/agents`
All loaded agents: name, model, skill count, A2A URL.

### `GET /dashboard/api/routing`
Circuit breaker states + routing strategy usage histogram.

### `GET /dashboard/api/agent-factory`
AGENT_FACTORY configuration and available model tiers.

### `GET /dashboard/api/cases`
Open investigation cases (summary list).

### `GET /dashboard/api/tasks`
Recent A2A tasks: state, assigned agent, timestamps. Query params: `limit`, `state`.

### `POST /dashboard/api/tasks/{id}/cancel`
Cancel a running A2A task by ID.

### `GET /dashboard/api/prompts`
Prompt template catalog.

---

## Dashboard SSE

### `GET /dashboard/sse/cases`
Live stream of case events: `case_opened`, `case_updated`, `case_closed`.

### `GET /dashboard/sse/tasks`
Live stream of A2A task state changes.

### `GET /dashboard/sse/health`
Periodic health pulse (every 30 seconds).

```bash
# Example: stream health events
curl -N http://localhost:8000/dashboard/sse/health
```

---

## Dashboard UI

### `GET /dashboard/`
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

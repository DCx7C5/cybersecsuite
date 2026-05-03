# HTTP API Reference

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
  "config": {"database": "cybersec_forensics", "host": "localhost", "port": 5432}
}
```

Returns `200` when healthy, `503` when DB unavailable.

---

## Agent Card

### `GET /.well-known/agent.json`

Returns the orchestrator's A2A agent card.

---

## AI Proxy — OpenAI-Compatible (`/v1/`)

### `POST /v1/chat/completions`

Multi-provider chat completion.

```json
{
  "model": "auto",
  "messages": [{"role": "user", "content": "Analyze IOC: 192.168.1.100"}],
  "stream": false
}
```

Special `model` values:
| Value              | Behavior                                            |
|--------------------|-----------------------------------------------------|
| `auto`             | Auto-route based on context                         |
| `provider:model`   | Force specific provider + model (`anthropic:claude-3-5-sonnet`) |
| `free`             | Cost-optimized routing (free-tier first)            |

### `GET /v1/models`

List all available models across active providers.

### Custom routing headers

| Header              | Purpose                                 |
|---------------------|-----------------------------------------|
| `x-provider`        | Force a specific provider               |
| `x-prefer-free`     | Prefer free-tier providers              |
| `x-max-cost-per-1k` | Budget filter (max cost per 1K tokens)  |

---

## Dashboard API (`/api/*`)

### System & Providers

| Method | Path                | Description                                              |
|--------|---------------------|----------------------------------------------------------|
| GET    | `/api/overview`     | System overview: version, uptime, active modules         |
| GET    | `/api/providers`    | All 9 AI providers with status and model counts          |
| GET    | `/api/usage`        | Token + cost usage by provider and model                 |
| GET    | `/api/health`       | Full health check across all subsystems                  |
| GET    | `/api/crypto`       | Crypto module status                                     |
| GET    | `/api/db-counts`    | Row counts for all 44+ ORM models                        |
| GET    | `/api/routing`      | Circuit breaker states + routing strategy histogram      |

### Agents & Tasks

| Method | Path                          | Description                                  |
|--------|-------------------------------|----------------------------------------------|
| GET    | `/api/agents`                 | All loaded agents: name, model, skill count  |
| GET    | `/api/a2a`                    | A2A server stats: agent count, task counts   |
| GET    | `/api/agent-factory`          | AGENT_FACTORY config and model tiers         |
| GET    | `/api/tasks`                  | Recent A2A tasks. Query: `limit`, `state`    |
| POST   | `/api/tasks/{id}/cancel`      | Cancel a running A2A task                    |
| POST   | `/api/agent-query`            | Single-shot agent query                      |
| POST   | `/api/agent-run`              | Start streaming chat execution               |
| DELETE | `/api/agent-run/{task_id}`    | Cancel active chat stream                    |

**`POST /api/agent-query` body:**
```json
{"agent": "cybersec-agents", "prompt": "Analyze IOC 10.0.0.5"}
```

**`POST /api/agent-run` body:**
```json
{"agent": "cybersec-agents", "prompt": "Analyze IOC 10.0.0.5", "stream": true}
```

Returns `{"task_id": "uuid"}`. Read events via `GET /sse/agent-run/{task_id}`.

### Investigation Data

| Method | Path                    | Description                                        |
|--------|-------------------------|----------------------------------------------------|
| GET    | `/api/investigations`   | Recent investigations. Query: `limit`, `offset`, `status` |
| GET    | `/api/cases`            | Open investigation cases (summary)                 |
| GET    | `/api/prompts`          | Prompt template catalog                            |

### SDK Options

| Method | Path                       | Description                                 |
|--------|----------------------------|---------------------------------------------|
| GET    | `/api/sdk/options`         | Merged runtime options (MCPs, agents, model)|
| POST   | `/api/sdk/options`         | Update options for a scope layer            |
| GET    | `/api/sdk/options/scopes`  | Raw snapshot of all scope layers            |
| DELETE | `/api/sdk/options`         | Reset a scope to defaults                   |

### Accounts

| Method | Path                                     | Description                     |
|--------|------------------------------------------|---------------------------------|
| GET    | `/api/accounts`                          | List all API key accounts       |
| POST   | `/api/accounts`                          | Create account                  |
| GET    | `/api/accounts/{vault_key}`              | Get account                     |
| PUT    | `/api/accounts/{vault_key}`              | Update (actions: set_active, rotate, test) |
| DELETE | `/api/accounts/{vault_key}`              | Delete account                  |
| GET    | `/api/accounts/resolve?provider_id={id}` | Resolve API key for provider    |

### Provider Authentication (Provider Hub)

| Method | Path                                              | Description |
|--------|---------------------------------------------------|-------------|
| POST   | `/api/providers/{provider_id}/auth/initiate`      | Start provider auth flow (`oauth`, `device_flow`, `api_key`, `browser`) |
| POST   | `/api/providers/{provider_id}/auth/verify`        | Verify/complete provider auth flow or save credentials |
| POST   | `/api/providers/{provider_id}/auth/revoke`        | Revoke (delete) provider account credentials |
| GET    | `/api/providers/{provider_id}/accounts`           | List provider-scoped accounts |

**`POST /api/providers/{provider_id}/auth/initiate` body:**
```json
{"auth_method": "oauth"}
```

**OAuth initiate response (example):**
```json
{
  "status": "oauth_pending",
  "auth_flow_id": "uuid",
  "state": "random-state",
  "oauth_url": "https://provider/oauth/authorize?...",
  "expires_in": 900
}
```

**Device flow initiate response (example):**
```json
{
  "status": "device_pending",
  "auth_flow_id": "uuid",
  "device_code": "opaque-device-code",
  "user_code": "ABCD-EFGH",
  "verification_uri": "https://provider/device",
  "interval": 8,
  "expires_in": 900
}
```

### Startup

| Method | Path                   | Description                               |
|--------|------------------------|-------------------------------------------|
| GET    | `/api/startup/status`  | Startup status, first-run flag, marketplace |

### QoL Output Controls

| Method | Path                     | Description                                |
|--------|--------------------------|---------------------------------------------|
| GET    | `/api/qol`               | Get current QoL settings (active scope)     |
| POST   | `/api/qol`               | Update QoL settings (toggles, preset, scope)|
| DELETE | `/api/qol`               | Reset QoL to defaults                       |
| GET    | `/api/qol/presets`       | List builtin presets                        |
| POST   | `/api/qol/presets/{name}`| Apply builtin preset (e.g., `audit`, `silent`) |

**`GET /api/qol` response:**
```json
{
  "scope": "session",
  "scope_id": "sess-abc123",
  "enabled_toggles": ["REASONING_SILENT"],
  "preset": "silent",
  "token_estimate": 50
}
```

**`POST /api/qol` body:**
```json
{
  "scope": "session",
  "enabled_toggles": ["CODE_ONLY", "REASONING_SILENT"],
  "preset": "code-only"
}
```

**`GET /api/qol/presets` response:**
```json
{
  "presets": {
    "silent": {
      "name": "silent",
      "description": "Minimal chatter, quick answers",
      "toggles": ["REASONING_SILENT", "STEP_BY_STEP_SILENT"],
      "token_estimate": 45
    },
    "code-only": {
      "name": "code-only",
      "description": "Pure code output for automation",
      "toggles": ["CODE_ONLY", "REASONING_SILENT"],
      "token_estimate": 30
    },
    "audit": {
      "name": "audit",
      "description": "Forensic compliance logging",
      "toggles": ["AUDIT_MODE", "PLAIN_TEXT_ONLY"],
      "token_estimate": 55
    },
    "structured": {
      "name": "structured",
      "description": "Machine-parseable with provenance",
      "toggles": ["JSON_STRUCTURED", "AUDIT_MODE"],
      "token_estimate": 65
    },
    "plain-text": {
      "name": "plain-text",
      "description": "Clean plain text output",
      "toggles": ["PLAIN_TEXT_ONLY", "NO_CITATIONS"],
      "token_estimate": 40
    }
  }
}
```

**Error codes:**
- `400` — Invalid toggle name or incompatible preset
- `403` — Permission denied (scope mismatch)
- `409` — Conflicting toggle combination (e.g., `CODE_ONLY` + `PLAIN_TEXT_ONLY`)

---

## Dashboard SSE Streams (`/sse/*`)

| Path                     | Events                                                   |
|--------------------------|----------------------------------------------------------|
| `/sse/cases`             | `case_opened`, `case_updated`, `case_closed`             |
| `/sse/tasks`             | A2A task state changes                                   |
| `/sse/health`            | Periodic health pulse (every 30 seconds)                 |
| `/sse/agent-run/{id}`    | `token`, `tool_start`, `tool_done`, `done`, `error`      |
| `/sse/telemetry`         | Real-time telemetry (15-second polling)                  |

```bash
# Stream health events
curl -N http://localhost:8000/sse/health

# Stream agents output
curl -N http://localhost:8000/sse/agent-run/{task_id}
```

### SSE Event Types (`/sse/agent-run`)

| Event        | Payload                                         |
|--------------|-------------------------------------------------|
| `token`      | Incremental assistant text chunks               |
| `tool_start` | Tool invocation start marker                    |
| `tool_done`  | Tool completion + elapsed ms                    |
| `done`       | Terminal success (`elapsed_ms`, `stop_reason`)  |
| `error`      | Terminal failure                                |

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

Standard HTTP status codes: `400`, `404`, `500`, `503`.

### JSON-RPC errors (A2A)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {"code": -32600, "message": "Invalid Request", "data": "..."}
}
```

Standard A2A error codes: see `src/a2a/models.py` (`A2AErrorCodes`).

# Dashboard

Live monitoring dashboard for CyberSecSuite — REST API + SSE streaming + HTML UI.

## Overview

The dashboard provides:
- 16 REST API endpoints covering all subsystem metrics
- 3 SSE (Server-Sent Events) endpoints for live streaming
- A single-page HTML dashboard at `/`

## Quick Start

```bash
# Start the ASGI server
make serve

# Open dashboard
open http://localhost:8000/

# Or generate a static HTML snapshot
make dashboard
make dashboard-serve  # serves at http://localhost:9000
```

## REST API Endpoints

All endpoints return JSON. Mounted at `/api/`.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/overview` | GET | System overview: version, uptime, module status |
| `/api/providers` | GET | AI provider list with status and model counts |
| `/api/usage` | GET | Token + cost usage stats by provider |
| `/api/health` | GET | Full health check (DB, providers, MCP) |
| `/api/crypto` | GET | Crypto module status (keys loaded, algo info) |
| `/api/a2a` | GET | A2A server status: agent count, task counts |
| `/api/db-counts` | GET | Row counts for all ORM models |
| `/api/investigations` | GET | Recent investigations list |
| `/api/agents` | GET | All loaded agents (name, model, skills) |
| `/api/routing` | GET | Circuit breaker states + routing stats |
| `/api/agent-factory` | GET | AGENT_FACTORY config + available models |
| `/api/cases` | GET | Open investigation cases |
| `/api/tasks` | GET | Recent A2A tasks (state + summary) |
| `/api/tasks/{task_id}/cancel` | POST | Cancel a running A2A task |
| `/api/prompts` | GET | Prompt templates catalog |

### Provider Hub auth endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/providers/{provider_id}/auth/initiate` | POST | Start OAuth/device/API key auth flow |
| `/api/providers/{provider_id}/auth/verify` | POST | Verify or complete auth flow |
| `/api/providers/{provider_id}/auth/revoke` | POST | Revoke provider account credentials |
| `/api/providers/{provider_id}/accounts` | GET | List provider accounts |

## SSE Endpoints

Server-Sent Events for real-time updates. Connect with `EventSource` in the browser or `curl`.

| Endpoint | Event type | Description |
|----------|-----------|-------------|
| `/sse/cases` | `case_update` | New/updated investigation cases |
| `/sse/tasks` | `task_update` | A2A task state changes |
| `/sse/health` | `health_pulse` | Periodic health check (every 30s) |

```javascript
// Browser example
const es = new EventSource('/sse/health');
es.addEventListener('health_pulse', (e) => {
  const data = JSON.parse(e.data);
  console.log('DB status:', data.status);
});
```

```bash
# CLI example
curl -N http://localhost:8000/sse/health
```

## HTML Dashboard

The dashboard page at `/` is a single HTML page that:
- Connects to all SSE endpoints for live updates
- Polls the REST API for initial data load
- Displays: provider status, active tasks, case list, DB health, routing stats

The static HTML can also be generated with `make dashboard` (produces `skills/dashboard/index.html`).

## Files

| File | Purpose |
|------|---------|
| `routes.py` | All 16 REST + 3 SSE endpoints + `create_dashboard_router()` |
| `__init__.py` | Package exports |

## Example: get system health

```bash
curl http://localhost:8000/api/health | python -m json.tools
```

Example response:
```json
{
  "status": "ok",
  "db": {"initialized": true, "intel_bootstrapped": true},
  "providers": {"active": 3, "total": 9},
  "mcp": {"tools": 83},
  "a2a": {"agents": 32, "tasks_active": 0}
}
```

# Dashboard

Live monitoring dashboard for CyberSecSuite — REST API + SSE streaming + HTML UI.

## Overview

The dashboard provides:
- 16 REST API endpoints covering all subsystem metrics
- 3 SSE (Server-Sent Events) endpoints for live streaming
- A single-page HTML dashboard at `/dashboard/`

## Quick Start

```bash
# Start the ASGI server
make serve

# Open dashboard
open http://localhost:8000/dashboard/

# Or generate a static HTML snapshot
make dashboard
make dashboard-serve  # serves at http://localhost:9000
```

## REST API Endpoints

All endpoints return JSON. Mounted at `/dashboard/api/`.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/dashboard/api/overview` | GET | System overview: version, uptime, module status |
| `/dashboard/api/providers` | GET | AI provider list with status and model counts |
| `/dashboard/api/usage` | GET | Token + cost usage stats by provider |
| `/dashboard/api/health` | GET | Full health check (DB, providers, MCP) |
| `/dashboard/api/crypto` | GET | Crypto module status (keys loaded, algo info) |
| `/dashboard/api/a2a` | GET | A2A server status: agent count, task counts |
| `/dashboard/api/db/counts` | GET | Row counts for all 50 ORM models |
| `/dashboard/api/investigations` | GET | Recent investigations list |
| `/dashboard/api/agents` | GET | All loaded agents (name, model, skills) |
| `/dashboard/api/routing` | GET | Circuit breaker states + routing stats |
| `/dashboard/api/agent-factory` | GET | AGENT_FACTORY config + available models |
| `/dashboard/api/cases` | GET | Open investigation cases |
| `/dashboard/api/tasks` | GET | Recent A2A tasks (state + summary) |
| `/dashboard/api/tasks/{id}/cancel` | POST | Cancel a running A2A task |
| `/dashboard/api/prompts` | GET | Prompt templates catalog |

## SSE Endpoints

Server-Sent Events for real-time updates. Connect with `EventSource` in the browser or `curl`.

| Endpoint | Event type | Description |
|----------|-----------|-------------|
| `/dashboard/sse/cases` | `case_update` | New/updated investigation cases |
| `/dashboard/sse/tasks` | `task_update` | A2A task state changes |
| `/dashboard/sse/health` | `health_pulse` | Periodic health check (every 30s) |

```javascript
// Browser example
const es = new EventSource('/dashboard/sse/health');
es.addEventListener('health_pulse', (e) => {
  const data = JSON.parse(e.data);
  console.log('DB status:', data.status);
});
```

```bash
# CLI example
curl -N http://localhost:8000/dashboard/sse/health
```

## HTML Dashboard

The dashboard page at `/dashboard/` is a single HTML page that:
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
curl http://localhost:8000/dashboard/api/health | python -m json.tool
```

Example response:
```json
{
  "status": "ok",
  "db": {"initialized": true, "intel_bootstrapped": true},
  "providers": {"active": 3, "total": 9},
  "mcp": {"tools": 29},
  "a2a": {"agents": 32, "tasks_active": 0}
}
```

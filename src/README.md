# src/ — CyberSecSuite Source Code Reference

This directory contains 33+ Python modules (~295 files) that comprise the CyberSecSuite forensic analysis platform.

## ⚠️ Critical Modules (Do Not Remove)

### ASGI Entrypoint
- **proxy/** — ASGI/FastAPI entrypoint
  - `proxy/asgi.py` — Main app definition
  - **Used by**: Makefile, Docker, `src/ai_proxy/cli.py`, `tests/test_dashboard_routing.py`
  - **Command**: `uvicorn proxy.asgi:app --port 8000`
  - **Restart**: `docker-compose restart cybersec-proxy`

### Active Worker API
- **api/** — FastAPI routes for worker management
  - `api/routes/workers.py` — CRUD operations for workers
  - `api/routes/worker_batch.py` — Batch operations
  - `api/routes/worker_metrics.py` — Metrics endpoints
  - `api/routes/worker_lifecycle.py` — Lifecycle management
  - `api/routes/worker_history.py` — History tracking
  - **Used by**: Multiple `tests/test_worker_*.py` files
  - **Status**: In-progress API surface (Phase 5+)

### Desktop Notifications
- **dbus/** — DBus integration for desktop notifications
  - `dbus/notifier.py` — DbusNotifier class for system notifications
  - **Used by**: `src/hooks/sdk_hooks.py`
  - **Purpose**: Desktop notifications when hooks fire

### Memory/Vault
- **memory/** — In-memory caching and vault storage
  - `memory/backends/` — Cache backend implementations
  - `memory/vault/` — Secret vault storage
  - `memory/canvas/` — Canvas state management
  - **Used by**: `src/csmcp/cybersec/canvas_tool.py`, `vault_tool.py`
  - **Purpose**: Session state, secrets, canvas rendering

## 📦 Core Modules

| Module | Size | Purpose | Status |
|--------|------|---------|--------|
| **db** | 2.1MB | Database models & ORM (Tortoise) — 47+ models | ✅ Core |
| **ai_proxy** | 516KB | AI provider routing, translators, executors | ✅ Core |
| **hooks** | 224KB | Lifecycle hooks (1344 files, one per event) | ✅ Core |
| **crypto** | 192KB | Ed25519, AES, BLAKE2b encryption | ✅ Core |
| **csmcp** | 280KB | MCP server integration & tools | ✅ Core |
| **a2a** | 120KB | Agent-to-Agent protocol implementation | ✅ Core |

## 🎨 Frontend & Services

| Module | Size | Purpose | Status |
|--------|------|---------|--------|
| **frontend** | 320MB | React 19 + TypeScript SPA (includes node_modules) | ✅ Active |
| **agent_ts** | 263MB | TypeScript agent implementations (includes node_modules) | ✅ Active |
| **ts_api** | 56MB | GraphQL/REST API client (TypeScript) | ✅ Active |

## 🔧 Utilities & Integration

| Module | Size | Purpose |
|--------|------|---------|
| **llm** | 21KB | LLM client & session tracking |
| **logger** | 1.8KB | Structured logging setup |
| **manage** | 52KB | CLI management commands (schema, seed, migrate) |
| **marketplace** | 68KB | Marketplace item registry & seeding |
| **accounts** | 68KB | Account management & auth |
| **telemetry** | 20KB | OTEL metrics collection |
| **openobserve** | 15KB | Observability sink (append-only streams) |
| **browser-plugin** | 76KB | Chrome extension integration |
| **checks** | 44KB | Model/fixture/config consistency checks |
| **template_engine** | 28KB | Jinja2-based template rendering |
| **testing** | 24KB | Test fixtures & utilities |
| **agent** | 44KB | Agent orchestration (minimal CLI) |
| **startup** | 44KB | System startup/shutdown hooks |
| **csmcp** | 280KB | MCP server + cybersec tools |

## 📊 Module Dependency Map

```
proxy/asgi.py (ASGI app)
  ├─ ai_proxy (routing, translators, executors)
  ├─ db (ORM models, database access)
  ├─ api/routes (worker API endpoints)
  ├─ hooks (lifecycle events)
  └─ csmcp (MCP tools)
       ├─ memory/vault (vault storage)
       └─ memory/canvas (canvas rendering)

frontend (React SPA)
  └─ ts_api (GraphQL/REST client)
  
dbus (desktop notifications)
  └─ hooks/sdk_hooks.py

ai_proxy/cli.py
  └─ proxy.asgi:app (entrypoint)
```

## 🚀 Docker Compose Services

The platform uses Docker Compose for orchestration:

```bash
# View all services
docker-compose ps

# Restart specific services
docker-compose restart cybersec-proxy      # ASGI backend
docker-compose restart cybersec-dashboard  # Frontend
docker-compose restart cybersec-postgres   # Database
docker-compose restart cybersec-redis      # Cache
docker-compose restart cybersec-ollama     # Local LLM
docker-compose restart cybersec-openobserve # Observability

# Full restart (stop + start all services)
docker-compose down
docker-compose up -d

# View logs for a service
docker-compose logs -f cybersec-proxy
docker-compose logs -f cybersec-dashboard
```

## 🔄 Restart Workflows

### After Code Changes to Python Backend
```bash
# Edit src/proxy/asgi.py, src/ai_proxy/*, src/db/*, etc.
docker-compose restart cybersec-proxy

# Verify health
docker-compose ps
# cybersec-proxy should show "healthy" status

# Check logs if unhealthy
docker-compose logs cybersec-proxy
```

### After Code Changes to Frontend
```bash
# Edit src/frontend/src/*, src/frontend/components/*, etc.
docker-compose restart cybersec-dashboard

# Verify health
docker-compose ps
# cybersec-dashboard should show "healthy" status
```

### After Database Schema Changes
```bash
# Run manage commands to update schema
python src/manage.py schema

# Restart postgres to reload
docker-compose restart cybersec-postgres
docker-compose restart cybersec-proxy  # Depends on postgres
```

### Full System Restart (After Major Changes)
```bash
# Stop all containers and remove volumes (data loss!)
docker-compose down -v

# Rebuild images (if Dockerfiles changed)
docker-compose build --no-cache

# Start fresh
docker-compose up -d

# Wait for healthchecks to pass
docker-compose ps
```

## 🧹 Development Hygiene

### Cache Cleaning
```bash
# Remove Python bytecode cache (safe, auto-regenerates)
find src -name "__pycache__" -type d -exec rm -rf {} +

# Remove Python compiled files
find src -name "*.pyc" -delete

# Clean pip cache
pip cache purge
```

### Verification Commands
```bash
# Check all Python files compile
python -m compileall src

# Run type checking
mypy src --strict 2>&1 | head -50

# Run linting
ruff check src

# Run tests
pytest tests/ -v
```

## 📝 Key Gotchas

1. **proxy/__init__.py is intentionally minimal** — The real entrypoint is `proxy/asgi.py`, not the package init.
2. **api/__init__.py doesn't export routes** — Routes are imported directly from `api.routes.*` submodules in tests.
3. **dbus is optional** — Desktop notifications fail gracefully if DBus is unavailable (Linux/systemd only).
4. **memory/ requires initialization** — Memory backends must be explicitly initialized before use.
5. **Frontend is huge** — 320MB includes node_modules; regenerated on Docker rebuild.
6. **Agent_ts is huge** — 263MB includes TypeScript compiled code + node_modules.

## 🔗 Related Documentation

- **docs/architecture/module-map.md** — Verified import graph (auto-generated)
- **docs/database.md** — Database models (47+ ORM models)
- **docs/configuration/mcp-json.md** — MCP server configuration
- **Makefile** — Build targets and dev commands
- **docker-compose.yml** — Service definitions and health checks

---

**Last Updated**: 2026-04-27  
**Total Python Files**: ~295  
**Total Modules**: 33+  
**Total Size**: ~320MB (dominated by node_modules)

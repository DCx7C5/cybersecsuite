# @asgi — Local ASGI Runtime & Transport Surfaces

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Location**: `src/css/core/asgi/`

**Responsibility**: Local ASGI application composition, transport routing, middleware/policy boundaries, router discovery, and process lifespan.

---

## Current Reality

The live backend is a **single local FastAPI/Uvicorn process**. Docker Compose runs **infra only**:

- PostgreSQL
- Redis
- OpenObserve
- Neo4j

The ASGI app, frontend dev server, and Ollama run outside Docker on the host.

Current code state in [app.py](./app.py):
- initializes Tortoise in lifespan
- initializes `ToolRegistry` runtime state
- seeds marketplace on startup
- mounts discovered HTTP routers
- exposes `/health`

Important correction: the codebase does **not** yet have first-class transport surfaces for:
- `/v1/*` proxy traffic
- `/ws/*` realtime channels
- `/sse/*` unidirectional streams

Those paths exist in plan/docs assumptions, but not yet as an explicit ASGI architecture.

---

## Target Topology

The backend should stay **one local process** and split transport targets clearly:

```text
localhost:8000
├── /api/*          REST + CRUD + commands
├── /ws/*           browser/session realtime channels
├── /sse/*          one-way stream endpoints
├── /v1/*           local-compatible LLM proxy facade
├── /.well-known/*  discovery surfaces
└── /health         process health
```

Rules:
- `docker-compose.yml` remains infra-only
- `modules/llm_proxy` is an **in-process** surface under `/v1/*`, not a compose service
- feature modules should not invent transport roots ad hoc
- transport policy must be explicit per surface instead of assuming HTTP middleware covers everything

---

## Recommended Composition

### Root Runtime

Keep a single root ASGI runtime in `core/asgi/app.py`.

### Mounted Surfaces

Use dedicated mounted surfaces or transport-specific routers for:

- `api_app` or API router tree
- `ws_app` or websocket router tree
- `sse_app` or SSE router tree
- `proxy_app` or `/v1/*` compatibility facade

This keeps one process while allowing different middleware/policy behavior per transport.

### Why Not Another Proxy Service

Do **not** add a separate Docker or sidecar gateway for local development:

- the app is meant to stay close to host resources
- Ollama and local filesystem workflows already assume host locality
- adding a network hop complicates auth, streaming, and debugging without buying real value here

---

## Starlette Note

**FastAPI already sits on Starlette.** The right move is not to rewrite the project to pure Starlette, but to use **Starlette-level primitives at the transport boundary**:

- ASGI middleware
- mounted sub-apps
- WebSocket handling
- low-level request/response flow
- `StreamingResponse` for SSE-style output when appropriate

Keep **FastAPI** where it helps:
- request validation
- OpenAPI
- dependency injection
- typed REST route definitions

Use **Starlette semantics** where FastAPI is too HTTP-centric:
- websocket lifecycle
- transport-aware middleware/policies
- mounted app boundaries
- streaming transport composition

Recommendation:
- **FastAPI for the API/proxy sub-apps**
- **Starlette-style composition for the root transport shell**

---

## Surface Boundaries

### `/api/*`

Owns:
- CRUD
- configuration
- dashboard data
- non-streaming commands

### `/ws/*`

Owns:
- interactive chat sessions
- approval push
- live graph streams
- dashboard event subscriptions

### `/sse/*`

Owns:
- token streams
- long-running progress streams
- fallback realtime feeds for clients that do not use WebSockets

### `/v1/*`

Owns:
- local-compatible proxy facade for tools like Claude Code and other LLM clients
- request normalization into the internal routing layer
- streaming response normalization back out to client-compatible SSE

`/v1/*` is not a generic reverse proxy. It is a **controlled adapter surface** over:
- `UnifiedLLMClient`
- prompt caching
- provider routing
- resilience
- memory/retrieval context assembly
- usage/telemetry capture

---

## Middleware & Policy Gap

Current middleware in [middleware.py](./middleware.py) is effectively **HTTP-only**:

- `TelemetryMiddleware`
- `RateLimitMiddleware`
- `HTTPSRedirectMiddleware`

That leaves gaps for:
- WebSocket auth and connection lifecycle
- SSE cancellation/backpressure
- `/v1/*` streaming normalization and audit tags
- transport-specific rate limits

This area must be refactored toward transport-aware policy application instead of assuming `BaseHTTPMiddleware` is enough.

---

## Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.loader` | → consumes | router/model discovery |
| `css.core.db` | → consumes | Tortoise init + shutdown |
| `css.core.tools` | → consumes | startup registry initialization |
| `css.core.prompt_cache` | ← feeds | `/v1/*` request/stream caching behavior |
| `css.modules.chat` | ← mounted by | chat REST + WS surfaces |
| `css.modules.llm_proxy` | ← mounted by | future `/v1/*` compatibility facade |
| `css.core.events` | ← emits | request/stream lifecycle telemetry |
| frontend Vite dev server | ← proxies to | `/api/*`, `/ws/*`, `/sse/*`, `/v1/*` on localhost |

---

## Planned Work

- `asgi-transport-topology`
- `asgi-mounted-surfaces`
- `asgi-transport-policy`

These todos live in Phase 36 and are the prep layer for `modules/llm_proxy`.

---

**Status**: 🟡 Active architecture prep | **Priority**: High | **Last Updated**: 2026-05-08

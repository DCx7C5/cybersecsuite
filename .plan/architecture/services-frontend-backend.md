## 🐳 SERVICES & DOCKER-COMPOSE ARCHITECTURE

### Overview

CyberSecSuite runs 6 containerized services via `docker-compose`:

```
docker-compose up -d
```

---

## SERVICES ARCHITECTURE

### 1. **cybersec-proxy** (ASGI Backend)

**Purpose**: FastAPI application server

**Container**: `cybersec:latest`

**Port**: `8765` (direct ASGI)

**Environment**:
```bash
PYTHONUNBUFFERED=1
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@cybersec-postgres:5432/cybersec
REDIS_URL=redis://cybersec-redis:6379/1
CACHE_BACKENDS=redis,postgres
OLLAMA_API_URL=http://localhost:11434
```

**Dependencies**:
- `cybersec-postgres` (database)
- `cybersec-redis` (cache L2)
- Ollama native process (managed by `core/ollama/OllamaProcessManager` — not Docker)

**Volumes**:
- `/app/src/css/` (read-only, app code)
- `/var/log/css/` (writable, application logs)

**Healthcheck**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8765/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**Role in Caching**:
- Orchestrator processes run here (in-memory L1 cache)
- Access to Redis (L2) and PostgreSQL (L3) backends

---

### 2. **cybersec-dashboard** (Frontend)

**Purpose**: React 19.2+ TypeScript dashboard UI

**Container**: `cybersec-dashboard:latest`

**Ports**:
- `8000` (HTTP)
- `8443` (HTTPS/TLS)

**Environment**:
```bash
REACT_APP_API_URL=http://localhost:8765
REACT_APP_WS_URL=ws://localhost:8765/ws
NODE_ENV=production
```

**Volumes**:
- `/app/src/frontend/` (application code)
- `/app/build/` (compiled output, persist for hot reload)

**Healthcheck**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/"]
  interval: 30s
  timeout: 10s
  retries: 3
```

**Features**:
- Real-time WebSocket connection to backend
- Session management (cookies)
- Team/agent monitoring dashboard
- Task progress tracking
- Cache statistics visualization

---

### 3. **cybersec-postgres** (PostgreSQL Database)

**Purpose**: Primary OLTP database + L3 cache persistence

**Container**: `postgres:15-alpine`

**Port**: `5432` (Unix socket inside network, not exposed)

**Environment**:
```bash
POSTGRES_USER=cybersec
POSTGRES_PASSWORD=<secret>
POSTGRES_DB=cybersec
POSTGRES_INITDB_ARGS=--encoding=UTF8 --locale=en_US.UTF-8
```

**Volumes**:
- `/var/lib/postgresql/data/` (persistent data)
- `/docker-entrypoint-initdb.d/` (init scripts)

**Databases**:
- `cybersec` (main)
  - Tables: scopes, orchestrators, tasks, teams, task_results, cache_entries, audit_log
- `cybersec_test` (for testing)

**Healthcheck**:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U cybersec"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**Role in Caching**:
- L3 cache backend (cold, persistent)
- Primary storage for task results (idempotency)
- Cache entries table (TTL-based auto-cleanup)
- Audit trail for all cache operations
- Session-scope cache persistence

---

### 4. **cybersec-redis** (Redis Cache)

**Purpose**: L2 cache backend + multi-orchestrator synchronization

**Container**: `redis:7-alpine`

**Port**: `6379` (internal network)

**Configuration**:
```yaml
command: redis-server
  --appendonly yes
  --appendfsync everysec
  --maxmemory 512mb
  --maxmemory-policy allkeys-lru
```

**Volumes**:
- `/data/` (RDB snapshots, persistence)

**Databases** (via SELECT):
- `db 0`: Session data (temporary)
- `db 1`: LLM response cache (L2)
- `db 2`: KB query results
- `db 3`: A2A message passing
- `db 4`: Orchestrator heartbeats

**Role in Caching**:
- L2 cache backend (warm, shared, multi-orchestrator)
- Fastest persistent cache (1-10ms latency)
- Orchestrator heartbeat storage (crash detection)
- Message passing for A2A communication
- Auto-expiry via TTL keys

**Healthcheck**:
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
```

---

### 5. **Ollama** (Local LLM — Native Process)

> ⚠️ **Docker container removed** — Ollama is now managed natively by `core/ollama/OllamaProcessManager`.

**Purpose**: Local LLM for Intelligence module (offline fallback, triage, quality gates)

**Managed by**: `core/ollama/OllamaProcessManager` — `asyncio.create_subprocess_exec("ollama", "serve")`

**Port**: `11434` (localhost only)

**Dev models** (pull manually — see `ollama pull` hint in `OllamaInstallChecker`):
- `qwen3:0.6b` (lightweight, Intelligence layer)
- `phi4-mini:3.8b-q4_K_M` (quality gate, reasoning)
- `qwen3:4b-q4_K_M` (general intelligence)

**Healthcheck**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
  interval: 30s
  timeout: 10s
  retries: 3
```

**Integration**:
- Fallback when `api_services/anthropic` fails
- Always available (no external API dependency)
- Used for Triage orchestrator (lightweight model)

---

### 6. **cybersec-openobserve** (Observability)

**Purpose**: Time-series telemetry, metrics, audit logs

**Container**: `public.ecr.aws/zinclabs/openobserve:latest`

**Ports**:
- `5080` (Web UI)
- `5081` (API, internal)

**Environment**:
```bash
ZO_ROOT_USER_EMAIL=admin@css.local
ZO_ROOT_USER_PASSWORD=<secret>
ZO_DATA_DIR=/data
ZO_RULE_GROUP_LIMIT=50
```

**Volumes**:
- `/data/` (time-series storage)

**Indices Tracked**:
- `audit_log` — Cache operations, user actions
- `telemetry` — API latency, throughput
- `cache_stats` — Hit rate, evictions
- `task_execution` — Task timing, results
- `llm_calls` — Claude API usage, costs

**Dashboard**:
- Real-time cache metrics
- Orchestrator health
- Team/agent performance
- Cost analysis (LLM API spend)

**Healthcheck**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5080/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## DOCKER-COMPOSE CONFIGURATION

### Full `docker-compose.yml` Structure

```yaml
version: '3.9'

services:
  cybersec-proxy:
    image: cybersec:latest
    container_name: cybersec-proxy
    ports:
      - "8765:8765"
    depends_on:
      cybersec-postgres:
        condition: service_healthy
      cybersec-redis:
        condition: service_healthy
    environment:
      - PYTHONUNBUFFERED=1
      - DATABASE_URL=postgresql://cybersec:${DB_PASSWORD}@cybersec-postgres:5432/cybersec
      - REDIS_URL=redis://cybersec-redis:6379/1
      - CACHE_BACKENDS=redis,postgres
      - OLLAMA_API_URL=http://localhost:11434
    volumes:
      - ./src/css:/app/src/css:ro
      - logs:/var/log/css
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8765/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - cybersec-net
    restart: unless-stopped

  cybersec-dashboard:
    image: cybersec-dashboard:latest
    container_name: cybersec-dashboard
    ports:
      - "8000:8000"
      - "8443:8443"
    depends_on:
      - cybersec-proxy
    environment:
      - REACT_APP_API_URL=http://localhost:8765
      - REACT_APP_WS_URL=ws://localhost:8765/ws
      - NODE_ENV=production
    volumes:
      - ./src/frontend:/app/src/frontend:ro
      - dashboard_build:/app/build
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - cybersec-net
    restart: unless-stopped

  cybersec-postgres:
    image: postgres:15-alpine
    container_name: cybersec-postgres
    environment:
      - POSTGRES_USER=cybersec
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=cybersec
      - POSTGRES_INITDB_ARGS=--encoding=UTF8 --locale=en_US.UTF-8
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cybersec"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - cybersec-net
    restart: unless-stopped

  cybersec-redis:
    image: redis:7-alpine
    container_name: cybersec-redis
    command: redis-server --appendonly yes --appendfsync everysec --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - cybersec-net
    restart: unless-stopped

  # cybersec-ollama REMOVED — Ollama runs natively via core/ollama/OllamaProcessManager
  # (Phase 33: ollama-docker-remove)

  cybersec-openobserve:
    image: public.ecr.aws/zinclabs/openobserve:latest
    container_name: cybersec-openobserve
    ports:
      - "5080:5080"
    environment:
      - ZO_ROOT_USER_EMAIL=admin@css.local
      - ZO_ROOT_USER_PASSWORD=${OBSERVE_PASSWORD}
      - ZO_DATA_DIR=/data
    volumes:
      - observe_data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - cybersec-net
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  ollama_models:
    driver: local
  logs:
    driver: local
  ollama_models:
    driver: local
  dashboard_build:
    driver: local
  observe_data:
    driver: local

networks:
  cybersec-net:
    driver: bridge
```

---

## MODULES ARCHITECTURE

### How Modules Integrate in Services

All modules (`@capabilities`, `@chat`, `@css_a2a`, `@events`, `@google_a2a`, `@llm_models`) run inside **cybersec-proxy** (FastAPI backend, port 8765):

**Module Startup** (initialization sequence):

1. **core/cache** — Initialize 3-layer KV backends (L1 memory, L2 Redis, L3 PostgreSQL)
2. **@capabilities** — Discover model capabilities from 12 LLM providers (via config.py API_KEYS)
3. **@llm_models** — Load model registry & metadata
4. **@events** — Start UniversalSDK event bus
5. **@css_a2a** — Start MessageDispatcher (Redis-backed A2A routing)
6. **@google_a2a** — Initialize Google A2A adapter (optional, if GOOGLE_A2A_ENABLED=true)
7. **@chat** — Start chat endpoint handlers (depends on capabilities + cache)

**Module Data Flow**:

```
Frontend (React)
    ↓ WebSocket (ws://localhost:8765/ws)
cybersec-proxy (FastAPI)
    ├─→ @chat (QoL injection, provider selection)
    ├─→ @capabilities (model capability check)
    ├─→ api_services/* (LLM API call)
    ├─→ core/cache (store response)
    ├─→ @events (emit 'provider.used' event)
    └─→ Frontend response
```

**LLM Provider Selection** (12 providers via config.py):

```python
# config.py
API_KEYS = {
    'NVIDIA': getenv('NVIDIA_API_KEY', None),
    'DEEPSEEK': getenv('DEEPSEEK_API_KEY', None),
    'GROQ': getenv('GROQ_API_KEY', None),
    'OPENROUTER': getenv('OPENROUTER_API_KEY', None),
    'CEREBRAS': getenv('CEREBRAS_API_KEY', None),
    'TOGETHER': getenv('TOGETHER_API_KEY', None),
    'GEMINI': getenv('GEMINI_API_KEY', None),
    'GITHUB': getenv('GITHUB_API_KEY', None),
    'MISTRAL': getenv('MISTRAL_API_KEY', None),
    'CLOUDFLARE': getenv('CLOUDFLARE_API_KEY', None),
    'FIREWORKS': getenv('FIREWORKS_API_KEY', None),
    'OPENCODE': getenv('OPENCODE_API_KEY', None),
}

# @capabilities queries these providers
registry = DynamicCapabilityRegistry()
await registry.discover()  # Queries provider /models endpoints
```

**A2A Communication** (agent-to-agent):

```
Orchestrator Agent
    ↓ @css_a2a (in-process)
Redis (cybersec-redis:6379, db=3)
    ↓ MessageDispatcher
Team Member Agent
    ├─→ core/cache (store task state)
    ├─→ @events (emit 'task.started', 'task.completed')
    └─→ Results back to Orchestrator
```

**Module Location in Service Stack**:

```
Orchestrator Process (in cybersec-proxy pod)
├─ core/cache (L1 in-memory + Redis L2 + PostgreSQL L3)
├─ @capabilities (queries Redis cache db=1 for LLM models)
├─ @css_a2a (uses Redis db=3 for A2A messages)
├─ @events (broadcasts events, optional UniversalSDK forwarding)
└─ @llm_models (in-memory registry)

Frontend Chat
├─ @chat (QoL injections)
├─ @capabilities (provider selection)
└─ core/cache (chat history storage)
```

---

## CACHING LAYER INTEGRATION

### 3-Layer Cache via Docker Services

```
Application (L1)
    ↓ [in-process memory]
Redis (L2: cybersec-redis:6379)
    ↓ [if Redis down]
PostgreSQL (L3: cybersec-postgres:5432)
```

### How It Works

**Normal Path** (all services healthy):
1. Request hits cybersec-proxy
2. L1 in-memory check (fast)
3. Redis cache hit (1-10ms)
4. Return to client

**Degraded Path** (Redis down):
1. Request hits cybersec-proxy
2. L1 in-memory check (fast)
3. PostgreSQL query (10-50ms)
4. Return to client (slower but working)

**Critical Path** (Redis + PostgreSQL down):
1. Request hits cybersec-proxy
2. L1 in-memory check (fast)
3. Disk SQLite fallback (50-500ms)
4. Return to client (slow but resilient)

---

## ENVIRONMENT & SECRETS

### `.env` File (Create Before Starting)

```bash
# Database
DB_PASSWORD=<strong-random-password>

# Redis
REDIS_PASSWORD=<optional>

# OpenObserve
OBSERVE_PASSWORD=<strong-random-password>

# LLM APIs (optional, external)
ANTHROPIC_API_KEY=<from anthropic.com>
OPENAI_API_KEY=<from openai.com>
GROQ_API_KEY=<from groq.com>

# Cache Configuration
CACHE_DEFAULT_TTL=86400  # 1 day
CACHE_LLM_TTL=2592000   # 30 days
CACHE_COMPRESSION=gzip
CACHE_ENCRYPTION=true
```

### Load via Docker Compose

```yaml
env_file:
  - .env
```

---

## STARTUP SEQUENCE

```bash
# 1. Create .env file
cp .env.example .env
# Edit .env with real passwords

# 2. Build custom images
docker-compose build

# 3. Start infra services (postgres, redis, openobserve)
docker-compose up -d

# 4. Verify health
docker-compose ps

# 5. Initialize database (first run)
docker-compose exec cybersec-postgres psql -U cybersec cybersec < init-db.sql

# 6. Start app (Ollama managed by OllamaProcessManager in lifespan)
CACHE_DIR=/tmp/css-cache LOG_DIR=/tmp/css-logs python manage.py serve --reload
# Ollama pulls: see OllamaInstallChecker hint, or manually:
#   ollama pull qwen3:0.6b
#   ollama pull phi4-mini:3.8b-q4_K_M
#   ollama pull qwen3:4b-q4_K_M

# 7. Access services
# Frontend:     http://localhost:8000  (bun run dev)
# Backend:      http://localhost:8765
# Observability: http://localhost:5080
```

---

## MONITORING & MANAGEMENT

### View Logs
```bash
docker-compose logs -f cybersec-proxy
docker-compose logs -f cybersec-redis
docker-compose logs -f cybersec-postgres
```

### Restart Service
```bash
docker-compose restart cybersec-proxy
```

### Inspect Cache (Redis)
```bash
docker-compose exec cybersec-redis redis-cli
> SELECT 1
> KEYS "llm-response-*"
> TTL <key>
```

### Stop All Services
```bash
docker-compose down
```

### Persistent Cleanup
```bash
docker-compose down -v  # Remove all volumes
```

---

**Status**: 📋 Active | **Last Updated**: 2026-05-03
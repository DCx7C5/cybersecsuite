# Docker Deployment Guide

Running CyberSecSuite in production with Docker Compose, TLS, and hardened configuration.

---

## Docker Compose (Recommended)

`docker-compose.yml` defines five services:

| Service                   | Image                              | Purpose                           | Port(s)        |
|---------------------------|------------------------------------|-----------------------------------|----------------|
| `cybersec-postgres`       | `postgres:15`                      | Primary database                  | 5432           |
| `cybersec-dashboard`      | local build                        | ASGI app, AI proxy, dashboard     | 8000, 8443, 8765 |
| `cybersec-redis`          | local build (`.docker/redis/`)     | Cache, rate-limiter counters      | 6379 (loopback only) |
| `openobserve`             | `openobserve/openobserve:latest`   | Observability (logs, traces)      | 5080           |
| `cybersec-mcp`            | local build                        | MCP stdio bridge (optional)       | —              |

```bash
# Start everything
make docker-up
# or
docker compose up -d

# Check logs
docker compose logs -f cybersec-dashboard

# Stop
make docker-down
```

### Verify running

```bash
curl http://localhost:8000/health
# → {"status": "ok", "initialized": true, ...}
```

---

## Redis Service

The `cybersec-redis` service provides caching for token optimization, session state, and rate-limiter counters. Data is persisted in the `redis_data` Docker volume. Binds only to `127.0.0.1` (not publicly exposed).

Set `REDIS_URL=redis://localhost:6379` in `.env` if components need explicit connection.

---

## Environment Configuration

```bash
cp .env.example .env
chmod 600 .env
```

Key production values:

```bash
# Database
CYBERSEC_DB_PASSWORD=very_strong_random_password
CYBERSEC_DB_HOST=cybersec-postgres   # Docker Compose service name

# Disable auto-init after first run
CYBERSEC_AUTO_CREATE_DB=false
CYBERSEC_BOOTSTRAP_INTEL_ON_START=false

# Production mode
DEBUG=false

# A2A base URL (your public address)
CYBERSEC_A2A_BASE_URL=https://yourdomain.com

# TLS
ASGI_TLS_CERT=/certs/cert.pem
ASGI_TLS_KEY=/certs/key.pem
ASGI_TLS_PORT=8443

# API keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

See [`../configuration/env-vars.md`](../configuration/env-vars.md) for the full reference.

---

## First-Time Database Setup

Run once before starting the app:

```bash
docker compose run --rm cybersec-dashboard python src/manage.py schema
docker compose run --rm cybersec-dashboard python src/manage.py seed
```

After seeding, set `CYBERSEC_BOOTSTRAP_INTEL_ON_START=false`.

---

## TLS / HTTPS

> ⚠️ Direct TLS (uvicorn on 8443) is configured in docker-compose. For production, a reverse proxy in front is recommended.

### Generate a self-signed cert (testing only)

```bash
python src/manage.py ssl-genkey
python src/manage.py ssl-info    # display details
python src/manage.py ssl-verify  # check validity
```

### Recommended: Caddy reverse proxy

```
yourdomain.com {
    reverse_proxy localhost:8000
}
```

### Port Reference

| Port    | Purpose                              |
|---------|--------------------------------------|
| `8000`  | HTTP primary                         |
| `8443`  | HTTPS / TLS                          |
| `8765`  | Alt HTTP (Docker host mapping)       |
| `5080`  | OpenObserve observability UI         |
| `6379`  | Redis (loopback only)                |
| `5432`  | PostgreSQL (loopback only)           |

---

## Health Check

The `cybersec-dashboard` service has a built-in healthcheck:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## Production Checklist

- [ ] `.env` permissions `600` (`chmod 600 .env`)
- [ ] `DEBUG=false`
- [ ] `CYBERSEC_DB_PASSWORD` is a strong random password
- [ ] `CYBERSEC_AUTO_CREATE_DB=false` (after initial setup)
- [ ] `CYBERSEC_BOOTSTRAP_INTEL_ON_START=false` (after seeding)
- [ ] All required AI provider API keys configured
- [ ] TLS configured (Caddy/nginx or direct on 8443)
- [ ] `CYBERSEC_A2A_BASE_URL` set to your public address
- [ ] Health endpoint returns `"status": "ok"`
- [ ] Database is backed up

---

## Scaling

The ASGI app is stateless (DB-backed state). To scale horizontally:

1. Run multiple `cybersec-dashboard` containers pointing at the same PostgreSQL
2. Put a load balancer in front (nginx, Caddy, Traefik)
3. Set `CYBERSEC_AUTO_CREATE_DB=false` on all instances

> **Note:** A2A task state is held in-memory (`TaskStore`). Tasks are not shared across instances. Multi-instance A2A requires migrating TaskStore to Redis or PostgreSQL (not yet implemented).

---

## Logs

```bash
docker compose logs -f cybersec-dashboard
docker compose logs -f cybersec-postgres
docker compose logs -f cybersec-redis
docker compose logs --tail=100 cybersec-dashboard
```

Real-time log stream via SSE:

```bash
curl -N http://localhost:8000/sse/health
```

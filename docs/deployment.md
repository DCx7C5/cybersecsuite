# Deployment Guide

Running CyberSecSuite in production with Docker Compose, TLS, and hardened configuration.

---

## Docker Compose (recommended)

The `docker-compose.yml` defines three services:
- `cybersec-postgres` — PostgreSQL 15 database
- `cybersec-dashboard` — Dashboard and ASGI application (all ports)
- `cybersec-redis` — Redis cache (port 6379)

```bash
# Start everything
make docker-up

# Check logs
docker compose logs -f cybersec-dashboard

# Stop
make docker-down
```

### Verify it's running

```bash
curl http://localhost:8000/health
# → {"status": "ok", "initialized": true, ...}
```

---

## Redis Service

The `cybersec-redis` service provides caching for token optimization, session state, and rate-limiter counters.

```yaml
cybersec-redis:
  build:
    context: .docker/redis
    dockerfile: Dockerfile
  image: cybersec-redis
  container_name: cybersec-redis
  restart: unless-stopped
  ports:
    - "127.0.0.1:6379:6379"
  volumes:
    - redis_data:/data
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 3s
    retries: 5
    start_period: 5s
```

Redis data is persisted in the `redis_data` Docker volume. The service binds only to `127.0.0.1` (not exposed publicly). Set `REDIS_URL=redis://localhost:6379` in `.env` if your app components need to connect explicitly.

---

## Environment Configuration

Create `.env` before starting:

```bash
cp .env.example .env
chmod 600 .env
```

Edit `.env` for production:

```bash
# Database (use a real password)
CYBERSEC_DB_PASSWORD=very_strong_random_password_here
CYBERSEC_DB_HOST=cybersec-postgres   # Docker Compose service name

# Disable auto-init after first run
CYBERSEC_AUTO_CREATE_DB=false
CYBERSEC_BOOTSTRAP_INTEL_ON_START=false

# Production mode
DEBUG=false

# A2A base URL (your public address)
CYBERSEC_A2A_BASE_URL=https://yourdomain.com

# TLS (see below)
ASGI_TLS_CERT=/certs/cert.pem
ASGI_TLS_KEY=/certs/key.pem
ASGI_TLS_PORT=8433

# API keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

---

## First-time database setup

Run once before starting the app:

```bash
# Create schema + seed intelligence data
docker compose run --rm cybersec-app python src/manage.py schema
docker compose run --rm cybersec-app python src/manage.py seed
```

After seeding completes, set `CYBERSEC_BOOTSTRAP_INTEL_ON_START=false`.

---

## TLS / HTTPS

> ⚠️ TLS certificate generation (`ssl-genkey`) is implemented in `manage.py` but the full TLS reverse-proxy chain (uvicorn on 8433) is Phase C (not yet complete). Use a reverse proxy (nginx, Caddy) for TLS termination in production.

### Generate a self-signed cert (for testing)

```bash
python src/manage.py ssl-genkey
# → ~/.omniroute/certs/cert.pem + key.pem

python src/manage.py ssl-info    # Display cert details
python src/manage.py ssl-verify  # Verify cert validity
```

### Recommended: Caddy reverse proxy

```
yourdomain.com {
    reverse_proxy localhost:8000
}
```

### Ports

| Port   | Purpose                              |
|--------|--------------------------------------|
| `8000` | HTTP (primary, behind reverse proxy) |
| `8080` | Alt HTTP (Docker only)               |
| `8433` | HTTPS (Phase C — direct TLS)         |

---

## Docker Compose health check

The `cybersec-app` service has a built-in healthcheck:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

Starts reporting healthy once the DB is initialized.

---

## Production checklist

- [ ] `.env` has permissions `600` (`chmod 600 .env`)
- [ ] `DEBUG=false`
- [ ] `CYBERSEC_DB_PASSWORD` is a strong random password (not `change_me`)
- [ ] `CYBERSEC_AUTO_CREATE_DB=false` (after initial setup)
- [ ] `CYBERSEC_BOOTSTRAP_INTEL_ON_START=false` (after seeding)
- [ ] All API keys configured for providers in use
- [ ] TLS configured (Caddy/nginx in front, or Phase C when complete)
- [ ] `CYBERSEC_A2A_BASE_URL` set to your public address
- [ ] Logs are being collected (`docker compose logs`)
- [ ] Health endpoint returns `"status": "ok"`
- [ ] Database is backed up (`db/backup_db.sh`)

---

## Scaling

The ASGI app is stateless (DB-backed state). To scale horizontally:
1. Run multiple app containers pointed at the same PostgreSQL
2. Put a load balancer in front (nginx, Caddy, Traefik)
3. Use `CYBERSEC_AUTO_CREATE_DB=false` on all instances (schema already exists)

Note: A2A task state is stored in-memory (`TaskStore`) — tasks are not shared across instances. For multi-instance A2A, this needs to be migrated to Redis or PostgreSQL (not yet implemented).

---

## Logs

```bash
# App logs
docker compose logs -f cybersec-dashboard

# Database logs
docker compose logs -f cybersec-postgres

# Redis logs
docker compose logs -f cybersec-redis

# Tail last 100 lines
docker compose logs --tail=100 cybersec-dashboard
```

Access logs are available via the dashboard SSE endpoint:
```bash
curl -N http://localhost:8000/dashboard/sse/health
```

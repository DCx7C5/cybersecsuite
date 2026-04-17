# ASGI Proxy

Starlette ASGI application — entry point for all HTTP traffic.

## Overview

`src/proxy/asgi.py` combines all subsystems into a single Starlette application:

| Mount | Service |
|-------|---------|
| `GET /health` | Health check (DB + provider status) |
| `/dashboard/*` | Dashboard UI and REST/SSE API |
| `/v1/*` | AI proxy (OpenAI-compatible) |
| `/a2a/*` | A2A JSON-RPC 2.0 server |
| `/.well-known/agent.json` | Agent card discovery |

## Quick Start

```bash
# Via Makefile (recommended)
make serve
# → uvicorn proxy.asgi:app --host 127.0.0.1 --port 8000 --reload

# Direct uvicorn
uvicorn proxy.asgi:app --host 0.0.0.0 --port 8000 --app-dir src
```

## Port Configuration

All ports are env-configurable:

| Variable | Default | Description |
|----------|---------|-------------|
| `ASGI_HOST` | `0.0.0.0` | Bind address |
| `ASGI_PORT` | `8000` | HTTP port |
| `ASGI_TLS_PORT` | `8433` | HTTPS port |
| `ASGI_TLS_CERT` | `~/.omniroute/certs/cert.pem` | TLS certificate |
| `ASGI_TLS_KEY` | `~/.omniroute/certs/key.pem` | TLS private key |

TLS activates automatically when both cert and key files exist:

```python
def get_ssl_context() -> ssl.SSLContext | None:
    cert, key = Path(ASGI_TLS_CERT), Path(ASGI_TLS_KEY)
    if cert.is_file() and key.is_file():
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(str(cert), str(key))
        return ctx
    return None
```

## Startup / Shutdown

On startup (`_on_startup`):
1. `init_tortoise_async()` — connects to PostgreSQL, optionally creates DB + schema
2. Configures per-provider rate limiters from provider RPM/TPM config

On shutdown (`_on_shutdown`):
1. `cleanup_executors()` — closes provider HTTP sessions
2. `close_tortoise()` — closes DB connection

## Health Endpoint

```bash
curl http://localhost:8000/health
# → {"status": "ok", "initialized": true, ...}
```

Returns HTTP 200 when DB is healthy, 503 otherwise. Used by Docker Compose healthcheck.

## Files

| File | Purpose |
|------|---------|
| `asgi.py` | Starlette app, mounts, startup/shutdown, health, TLS |

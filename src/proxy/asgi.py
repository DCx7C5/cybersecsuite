"""
ASGI application — combines:
  - AI proxy routes (OpenAI-compatible)    at /v1/*
  - Dashboard                             at /dashboard/*
  - A2A agent server  (JSON-RPC + SSE)    at /a2a/*
  - Agent card discovery                  at /.well-known/agent.json
  - Health endpoint                       at /health

Run with:
    uvicorn proxy.asgi:app --host 0.0.0.0 --port 8000 --reload
Or via Makefile:
    make serve

Ports (env-configurable):
    ASGI_HOST      — bind address     (default: 0.0.0.0)
    ASGI_PORT      — HTTP port        (default: 8000)
    ASGI_TLS_PORT  — HTTPS port       (default: 8433)
    ASGI_TLS_CERT  — PEM cert path    (default: ~/.omniroute/certs/cert.pem)
    ASGI_TLS_KEY   — PEM key path     (default: ~/.omniroute/certs/key.pem)
"""

from __future__ import annotations

import os
import ssl
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from a2a import CybersecA2AAgent, A2AServer
from db.bootstrap import init_tortoise_async, close_tortoise
from ai_proxy.routes import create_proxy_router
from ai_proxy.routing.combo import cleanup_executors
from ai_proxy.services.rate_limiter import rate_limiter, ProviderLimits
from ai_proxy.providers.registry import get_enabled_providers
from dashboard.routes import create_dashboard_router
from telemetry.middleware import TelemetryMiddleware
from telemetry.collector import collector as _telemetry_collector
from logger import root_logger

log = root_logger.getChild("asgi")


# ── Port / TLS configuration ─────────────────────────────────────────────────

ASGI_HOST = os.environ.get("ASGI_HOST", "127.0.0.1")
ASGI_PORT = int(os.environ.get("ASGI_PORT", "8000"))
ASGI_TLS_PORT = int(os.environ.get("ASGI_TLS_PORT", "8433"))
ASGI_TLS_CERT = os.environ.get(
    "ASGI_TLS_CERT",
    str(Path.home() / ".omniroute" / "certs" / "cert.pem"),
)
ASGI_TLS_KEY = os.environ.get(
    "ASGI_TLS_KEY",
    str(Path.home() / ".omniroute" / "certs" / "key.pem"),
)


def get_ssl_context() -> ssl.SSLContext | None:
    """Return an SSL context if TLS cert/key exist, else None."""
    cert, key = Path(ASGI_TLS_CERT), Path(ASGI_TLS_KEY)
    if cert.is_file() and key.is_file():
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(str(cert), str(key))
        return ctx
    return None


# ── Startup / shutdown ────────────────────────────────────────────────────────


async def _on_startup() -> None:
    """Initialize DB + AI proxy rate limiters on startup."""
    log.info("ASGI startup — initialising database and rate limiters")
    auto_create = os.environ.get("CYBERSEC_AUTO_CREATE_DB", "false").lower() == "true"
    auto_intel = os.environ.get("CYBERSEC_BOOTSTRAP_INTEL_ON_START", "false").lower() == "true"
    await init_tortoise_async(create_db=auto_create, bootstrap_intel=auto_intel)

    for provider in get_enabled_providers():
        rate_limiter.configure(
            provider.id,
            ProviderLimits(
                rpm=provider.rate_limit_rpm,
                tpm=provider.rate_limit_tpm,
            ),
        )

    _telemetry_collector.start()

    # OpenSearch — non-fatal if unavailable
    try:
        from opensearch.indices import ensure_indices
        from opensearch.writer import start_flush_loop

        await ensure_indices()
        start_flush_loop()
        log.info("OpenSearch indices ready")
    except Exception as exc:
        log.warning("OpenSearch unavailable — continuing without it: %s", exc)


async def _on_shutdown() -> None:
    log.info("ASGI shutdown — flushing telemetry and closing connections")
    _telemetry_collector.stop()

    try:
        from opensearch.writer import flush_all, stop_flush_loop
        from opensearch.client import close_client

        stop_flush_loop()
        await flush_all()
        await close_client()
        log.info("OpenSearch flushed and closed")
    except Exception as exc:
        log.warning("OpenSearch shutdown error: %s", exc)

    await cleanup_executors()
    await close_tortoise()
    log.info("ASGI shutdown complete")


# ── Health endpoint ───────────────────────────────────────────────────────────


async def health(request: Request) -> JSONResponse:
    from db.bootstrap import get_database_health_async

    log.debug("Health check requested")
    data = await get_database_health_async(check_connection=True, include_counts=False)
    status_code = 200 if data.get("status") == "ok" else 503
    if status_code != 200:
        log.warning("Health check failed: %s", data)
    return JSONResponse(data, status_code=status_code)


# ── A2A server (CybersecA2AAgent — SDK routes to .claude/agents/ directly) ────

_base_url = os.environ.get("CYBERSEC_A2A_BASE_URL", "http://localhost:8000")
_agent = CybersecA2AAgent(base_url=_base_url)
_a2a = A2AServer(_agent)


# ── Application ───────────────────────────────────────────────────────────────

app = Starlette(
    debug=os.environ.get("DEBUG", "false").lower() == "true",
    routes=[
        Route("/health", health),
        Mount("/dashboard", create_dashboard_router()),
        Mount("/v1", create_proxy_router()),
        Mount("/", _a2a.router),
    ],
    on_startup=[_on_startup],
    on_shutdown=[_on_shutdown],
    middleware=[],
)
app.add_middleware(TelemetryMiddleware)

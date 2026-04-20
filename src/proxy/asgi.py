"""
ASGI application — combines:
  - AI proxy routes (OpenAI-compatible)    at /v1/*
  - Dashboard                             at / (root, SPA)
  - Dashboard API                         at /api/*
  - Dashboard SSE                         at /sse/*
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

import asyncio
import os
import ssl
from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from a2a import CybersecA2AAgent, A2AServer
from db.bootstrap import init_tortoise_async, close_tortoise
from ai_proxy.routes import create_proxy_router
from ai_proxy.routing.combo import cleanup_executors
from ai_proxy.services.rate_limiter import rate_limiter, ProviderLimits
from ai_proxy.providers.registry import get_enabled_providers
from dashboard.routes import create_dashboard_router
from telemetry.middleware import TelemetryMiddleware
from telemetry.collector import collector as _telemetry_collector
from logger import getLogger

log = getLogger(__name__)


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

# Check if TLS is available
TLS_AVAILABLE = (
    Path(ASGI_TLS_CERT).is_file() and Path(ASGI_TLS_KEY).is_file()
)


def get_ssl_context() -> ssl.SSLContext | None:
    """Return an SSL context if TLS cert/key exist, else None."""
    if TLS_AVAILABLE:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(ASGI_TLS_CERT, ASGI_TLS_KEY)
        return ctx
    return None


# ── HTTP → HTTPS redirect middleware ─────────────────────────────────────────────


class HTTPSRedirectMiddleware:
    """Redirect HTTP to HTTPS if TLS is enabled, otherwise no-op."""

    def __init__(self, app, tls_enabled: bool = TLS_AVAILABLE) -> None:
        self.app = app
        self.tls_enabled = tls_enabled

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] == "http" and self.tls_enabled:
            headers = dict(scope.get("headers", []))
            host = headers.get(b"host", b"localhost:8000").decode()
            if ":" in host:
                host = host.rsplit(":", 1)[0]
            path = scope.get("root_path", "") + scope.get("path", "/")
            new_url = f"https://{host}:{ASGI_TLS_PORT}{path}"
            response = RedirectResponse(new_url, status=301)
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


# ── Startup / shutdown ────────────────────────────────────────────────────────


async def _on_startup() -> None:
    """Initialize DB + AI proxy rate limiters on startup."""
    log.info("ASGI startup — initialising database and rate limiters")

    # First-run check (non-fatal)
    try:
        from startup.first_run import first_run_setup
        await first_run_setup()
        log.info("Startup status checked")
    except Exception as exc:
        log.warning("First-run check failed: %s", exc)

    # IPC server (non-fatal)
    try:
        from hooks.ipc_receiver import ensure_ipc_server
        await ensure_ipc_server()
        log.info("IPC server started")
    except Exception as exc:
        log.warning("IPC server failed: %s", exc)

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

    app.state.agent_stream_tasks: dict[str, asyncio.Task] = {}
    app.state.agent_stream_queues: dict[str, asyncio.Queue] = {}

    # OpenObserve — non-fatal if unavailable
    try:
        from openobserve.streams import ensure_streams
        from openobserve.writer import start_flush_loop

        await ensure_streams()
        start_flush_loop()
        log.info("OpenObserve streams ready")
    except Exception as exc:
        log.warning("OpenObserve unavailable — continuing without it: %s", exc)


async def _on_shutdown() -> None:
    log.info("ASGI shutdown — flushing telemetry and closing connections")
    _telemetry_collector.stop()

    # IPC server
    try:
        from hooks.ipc_receiver import stop_ipc_server
        await stop_ipc_server()
        log.info("IPC server stopped")
    except Exception as exc:
        log.warning("IPC server shutdown error: %s", exc)

    # OpenObserve
    try:
        from openobserve.writer import flush_all, stop_flush_loop
        from openobserve.client import close_client

        stop_flush_loop()
        await flush_all()
        await close_client()
        log.info("OpenObserve flushed and closed")
    except Exception as exc:
        log.warning("OpenObserve shutdown error: %s", exc)

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
        # A2A routes — explicit, before dashboard catch-all mount
        Route("/.well-known/agent.json", _a2a._agent_card, methods=["GET"]),
        Route("/a2a", _a2a._jsonrpc, methods=["POST"]),
        Route("/a2a/stream/{task_id}", _a2a._sse_stream, methods=["GET"]),
        # Static files (compiled TypeScript + CSS/images)
        Mount("/static", StaticFiles(directory="src/dashboard/static"), name="static"),
        # AI Proxy
        Mount("/v1", create_proxy_router()),
        # Dashboard SPA — mounted at / (must be last; handles /, /api/*, /sse/*)
        Mount("/", create_dashboard_router()),
    ],
    on_startup=[_on_startup],
    on_shutdown=[_on_shutdown],
    middleware=[
        Middleware(HTTPSRedirectMiddleware, tls_enabled=TLS_AVAILABLE),
    ],
)
app.add_middleware(TelemetryMiddleware)

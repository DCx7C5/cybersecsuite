"""
ASGI application — combines:
  - App endpoint auto-discovery (modules/*/endpoints.py)  at app-defined prefixes
  - A2A agent server (JSON-RPC)                        at /a2a/*
  - Agent card discovery                               at /.well-known/agent.json
  - AI proxy routes (OpenAI-compatible)                at /v1/*
  - Health endpoint                                    at /health

Run with:
    uvicorn core.asgi.app:app --host 0.0.0.0 --port 8000 --reload
Or via Makefile:
    make serve

Ports (env-configurable):
    ASGI_HOST      — bind address     (default: 0.0.0.0)
    ASGI_PORT      — HTTP port        (default: 8000)
    ASGI_TLS_PORT  — HTTPS port       (default: 8433)
    ASGI_TLS_CERT  — PEM cert path    (default: ~/.cybersecsuite/certs/cert.pem)
    ASGI_TLS_KEY   — PEM key path     (default: ~/.cybersecsuite/certs/key.pem)
"""

import os
import ssl
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.types.endpoints import mount_app_routers
from legacy.logger import getLogger

log = getLogger(__name__)


# ── Port / TLS configuration ─────────────────────────────────────────────────

ASGI_HOST = os.environ.get("ASGI_HOST", "127.0.0.1")
ASGI_PORT = int(os.environ.get("ASGI_PORT", "8000"))
ASGI_TLS_PORT = int(os.environ.get("ASGI_TLS_PORT", "8433"))
ASGI_TLS_CERT = os.environ.get(
    "ASGI_TLS_CERT",
    str(Path.home() / ".cybersecsuite" / "certs" / "cert.pem"),
)
ASGI_TLS_KEY = os.environ.get(
    "ASGI_TLS_KEY",
    str(Path.home() / ".cybersecsuite" / "certs" / "key.pem"),
)

TLS_AVAILABLE = Path(ASGI_TLS_CERT).is_file() and Path(ASGI_TLS_KEY).is_file()


def get_ssl_context() -> ssl.SSLContext | None:
    """Return an SSL context if TLS cert/key exist, else None."""
    if TLS_AVAILABLE:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(ASGI_TLS_CERT, ASGI_TLS_KEY)
        return ctx
    return None


# ── Application factory ───────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """Construct and return the fully configured FastAPI application.

    Auto-discovers all ``modules/*/endpoints.py`` modules and mounts their
    routers.  Additional startup initialization (e.g. Redis clients,
    A2A communicator) is wired via ``@app.on_event("startup")`` or
    the ``lifespan`` context in each app's ``setup()`` if provided.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        log.info("CyberSecSuite starting — host=%s port=%d", ASGI_HOST, ASGI_PORT)
        yield
        log.info("CyberSecSuite shutting down")

    _app = FastAPI(
        title="CyberSecSuite",
        description="Cybersecurity forensics platform — AI agent hub",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Health check
    @_app.get("/health", tags=["core"])
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    # Mount core endpoints (marketplace API)
    try:
        from core.types.endpoints.marketplace import router as marketplace_router
        _app.include_router(marketplace_router)
        log.info("Mounted core endpoints: marketplace")
    except Exception as e:
        log.warning(f"Failed to mount marketplace endpoints: {e}")

    # Auto-discover and mount all modules/*/endpoints.py routers
    mounted = mount_app_routers(_app)
    log.info("App endpoints mounted: %s", mounted or ["(none)"])

    return _app


app = create_app()


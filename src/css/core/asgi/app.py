"""
ASGI application — combines:
  - App endpoint auto-discovery (modules/*/endpoints.py)  at app-defined prefixes
  - A2A agents server (JSON-RPC)                        at /a2a_google/*
  - Agent card discovery                               at /.well-known/agents.json
  - Health endpoint                                    at /health

Planned but not mounted yet:
  - Local-compatible LLM proxy facade                  at /v1/*

Run with:
    uvicorn core.asgi.app:app --host 0.0.0.0 --port 8000 --reload
Or via Makefile:
    make serve

Ports (env-configurable):
    ASGI_HOST      — bind address     (default: 0.0.0.0)
    ASGI_PORT      — HTTP port        (default: 8000)
    ASGI_TLS_PORT  — HTTPS port       (default: 8433)
    ASGI_TLS_CERT  — PEM cert path    (default: ~/.css/certs/cert.pem)
    ASGI_TLS_KEY   — PEM key path     (default: ~/.css/certs/key.pem)
"""

from css.core.logger import getLogger
import asyncio
import os
import ssl
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from tortoise import Tortoise

from css.config import ENVIRONMENT, MARKETPLACE_CONFIG, POSTGRES_DATABASE
from css.core.asgi.middleware import HTTPSRedirectMiddleware, RateLimitMiddleware, TelemetryMiddleware
from css.core.loader import build_tortoise_db_url, build_tortoise_modules, mount_app_routers
from css.core.tools.base import get_tool_registry

log = getLogger(__name__)


# ── Port / TLS configuration ─────────────────────────────────────────────────

ASGI_HOST = os.environ.get("ASGI_HOST", "127.0.0.1")
ASGI_PORT = int(os.environ.get("ASGI_PORT", "8000"))
ASGI_TLS_PORT = int(os.environ.get("ASGI_TLS_PORT", "8433"))
ASGI_TLS_CERT = os.environ.get(
    "ASGI_TLS_CERT",
    str(Path.home() / ".css" / "certs" / "cert.pem"),
)
ASGI_TLS_KEY = os.environ.get(
    "ASGI_TLS_KEY",
    str(Path.home() / ".css" / "certs" / "key.pem"),
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
        db_url = build_tortoise_db_url(POSTGRES_DATABASE)
        tortoise_apps = build_tortoise_modules()
        marketplace_update_task: asyncio.Task | None = None
        marketplace_update_stop = asyncio.Event()

        async def _periodic_marketplace_update_check() -> None:
            from css.core.marketplace.seeder import MarketplaceSeeder

            update_interval = int(MARKETPLACE_CONFIG["update_check_interval"])
            while not marketplace_update_stop.is_set():
                try:
                    async with MarketplaceSeeder() as seeder:
                        await seeder.check_for_updates()
                except Exception as exc:
                    log.warning("Marketplace periodic update check failed: %s", exc)

                try:
                    await asyncio.wait_for(marketplace_update_stop.wait(), timeout=update_interval)
                except asyncio.TimeoutError:
                    continue

        await Tortoise.init(
            config={
                "connections": {"default": db_url},
                "apps": tortoise_apps,
            }
        )
        if ENVIRONMENT == "development":
            await Tortoise.generate_schemas(safe=True)

        # Load async tool-registry runtime state after DB init.
        tool_registry = get_tool_registry()
        await tool_registry.initialize_runtime_state()
        log.info(
            "ToolRegistry ready: %d builtin tools, %d hybrid tools",
            len(tool_registry.tools),
            len(tool_registry.hybrid_tools),
        )

        try:
            from css.core.marketplace.seeder import seed_marketplace_on_startup

            await seed_marketplace_on_startup()
            marketplace_update_task = asyncio.create_task(_periodic_marketplace_update_check())
        except Exception as exc:
            log.warning("Marketplace startup integration failed: %s", exc)

        try:
            yield
        finally:
            log.info("CyberSecSuite shutting down")
            marketplace_update_stop.set()
            if marketplace_update_task is not None:
                marketplace_update_task.cancel()
                try:
                    await marketplace_update_task
                except asyncio.CancelledError:
                    pass
            await Tortoise.close_connections()

    _app = FastAPI(
        title="CyberSecSuite",
        description="Cybersecurity forensics platform — AI agents hub",
        version="1.0.0",
        lifespan=lifespan,
    )
    _app.add_middleware(HTTPSRedirectMiddleware, tls_enabled=TLS_AVAILABLE)
    _app.add_middleware(TelemetryMiddleware)
    _app.add_middleware(RateLimitMiddleware)

    # Health check
    @_app.get("/health", tags=["core"])
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    # Mount core endpoints (marketplace API)
    try:
        from css.core.marketplace.endpoints import router as marketplace_router
        _app.include_router(marketplace_router)
        log.info("Mounted core endpoints: marketplace")
    except Exception as e:
        log.warning(f"Failed to mount marketplace endpoints: {e}")

    # Auto-discover and mount all modules/*/endpoints.py routers
    mounted = mount_app_routers(_app)
    log.info("App endpoints mounted: %s", mounted or ["(none)"])

    return _app


app = create_app()

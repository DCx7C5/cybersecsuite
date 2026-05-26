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
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from tortoise import Tortoise

from css.core.asgi.middleware import HTTPSRedirectMiddleware, RateLimitMiddleware, TelemetryMiddleware
from css.core.db.models.menu import sync_default_menu_items
from css.core.exceptions import BaseCoreException, ConfigurationError
from css.core.loader import (
    build_tortoise_connection,
    build_tortoise_modules,
    mount_app_routers,
)
from css.core.marketplace.endpoints import router as marketplace_router
from css.core.marketplace.registry import wire_registry_events
from css.core.marketplace.seeder import seed_marketplace_on_startup
from css.core.menu.endpoints import router as menu_router
from css.core.settings.config import ENVIRONMENT, MARKETPLACE_CONFIG, POSTGRES_DATABASE


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
        tortoise_modules = build_tortoise_modules()
        css_model_paths = sorted({
            model_path
            for model_paths in tortoise_modules.values()
            for model_path in model_paths
        })
        # Core db models are not discoverable via entry points — include them all.
        core_db_model_paths = [
            "css.core.db.models.accounts",
            "css.core.db.models.events",
            "css.core.db.models.llm_models",
            "css.core.db.models.marketplace",
            "css.core.db.models.memory",
            "css.core.db.models.menu",
            "css.core.db.models.orchestrator",
            "css.core.db.models.permissions",
            "css.core.db.models.provider",
            "css.core.db.models.quotas",
            "css.core.db.models.scope",
            "css.core.db.models.tasks",
            "css.core.db.models.team",
            "css.core.db.models.user",
        ]
        for path in core_db_model_paths:
            if path not in css_model_paths:
                css_model_paths.append(path)
        css_model_paths.sort()
        tortoise_apps = {
            "models": {
                "models": css_model_paths,
                "default_connection": "default",
            },
        }
        marketplace_update_task: asyncio.Task | None = None
        marketplace_update_stop = asyncio.Event()

        async def _periodic_marketplace_update_check() -> None:
            from css.core.marketplace.seeder import MarketplaceSeeder

            update_interval = int(MARKETPLACE_CONFIG["update_check_interval"])
            while not marketplace_update_stop.is_set():
                try:
                    async with MarketplaceSeeder() as seeder:
                        await seeder.check_for_updates()
                except BaseCoreException as exc:
                    log.warning("Marketplace periodic update check failed: %s", exc)

                try:
                    await asyncio.wait_for(marketplace_update_stop.wait(), timeout=update_interval)
                except asyncio.TimeoutError:
                    continue

        db_ready = False
        marketplace_db_ready = False
        try:
            await Tortoise.init(
                config={
                    "connections": {"default": build_tortoise_connection(POSTGRES_DATABASE)},
                    "apps": tortoise_apps,
                },
                _enable_global_fallback=True,
            )
            if ENVIRONMENT == "development":
                await Tortoise.generate_schemas(safe=True)
            db_ready = True
            marketplace_db_ready = True
        except BaseCoreException as db_init_error:
            log.warning("DB init failed; continuing without DB-backed startup services: %s", db_init_error)
            try:
                await Tortoise.close_connections()
            except BaseCoreException:
                pass
            try:
                # Keep marketplace available even when broader model graph is broken.
                marketplace_db_config: dict[str, Any] = dict(POSTGRES_DATABASE)
                if not marketplace_db_config.get("host"):
                    marketplace_db_config["host"] = "127.0.0.1"
                if not marketplace_db_config.get("port"):
                    marketplace_db_config["port"] = "5432"
                if marketplace_db_config.get("database") in {None, "", "cybersec"}:
                    marketplace_db_config["database"] = "cybersec_forensics"
                await Tortoise.init(
                    config={
                        "connections": {"default": build_tortoise_connection(marketplace_db_config)},
                        "apps": {
                            "models": {
                                "models": [
                                    "css.core.db.models.accounts",
                                    "css.core.db.models.marketplace",
                                    "css.core.db.models.menu",
                                    "css.modules.tags.models",
                                ],
                                "default_connection": "default",
                            },
                        },
                    },
                    _enable_global_fallback=True,
                )
                if ENVIRONMENT == "development":
                    await Tortoise.generate_schemas(safe=True)
                marketplace_db_ready = True
                log.info("Marketplace-only DB init succeeded")
            except BaseCoreException as marketplace_db_error:
                log.warning("Marketplace-only DB init failed: %s", marketplace_db_error)

        # Load async tool-registry runtime state after DB init.
        if db_ready:
            from css.modules.tools.registry import ToolRegistry

            tool_registry = ToolRegistry()
            await tool_registry.initialize_runtime_state()
            log.info(
                "ToolRegistry ready: %d builtin tools, %d hybrid tools",
                len(tool_registry.tools),
                len(tool_registry.hybrid_tools),
            )

        # Register model discovery providers for dynamic model fetching.
        try:
            from css.core.models.discovery_integration import register_model_discovery_providers
            await register_model_discovery_providers()
        except BaseCoreException as discovery_error:
            log.warning("Failed to register model discovery providers: %s", discovery_error)

        # Wire registry cache invalidation to marketplace events.
        try:
            wire_registry_events()
            log.info("Registry event invalidation wired")
        except BaseCoreException as wire_error:
            log.warning("Failed to wire registry events: %s", wire_error)

        if marketplace_db_ready:
            try:
                await sync_default_menu_items()
                await seed_marketplace_on_startup(force=False)
                marketplace_update_task = asyncio.create_task(_periodic_marketplace_update_check())
            except BaseCoreException as startup_error:
                log.warning("Marketplace startup integration failed: %s", startup_error)

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
            if db_ready or marketplace_db_ready:
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
        _app.include_router(marketplace_router)
        _app.include_router(marketplace_router, prefix="/api")
        log.info("Mounted core endpoints: marketplace")
    except BaseCoreException as marketplace_mount_error:
        log.warning(f"Failed to mount marketplace endpoints: {marketplace_mount_error}")

    try:
        _app.include_router(menu_router)
        log.info("Mounted core endpoints: menu")
    except BaseCoreException as menu_mount_error:
        log.warning(f"Failed to mount menu endpoints: {menu_mount_error}")

    # Auto-discover and mount all modules/*/endpoints.py routers
    mounted = mount_app_routers(_app)
    log.info("App endpoints mounted: %s", mounted or ["(none)"])

    # Mount frontend static build if available
    frontend_dist = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist"
    if frontend_dist.is_dir():
        _app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="frontend_assets")

        @_app.api_route("/{full_path:path}", methods=["GET"])
        async def serve_frontend(full_path: str) -> FileResponse:
            file_path = frontend_dist / full_path
            if full_path and file_path.is_file():
                return FileResponse(str(file_path))
            return FileResponse(str(frontend_dist / "index.html"))

        log.info("Mounted frontend static build from %s", frontend_dist)
    else:
        log.info("No frontend dist at %s — frontend not served", frontend_dist)

    return _app



app = create_app()

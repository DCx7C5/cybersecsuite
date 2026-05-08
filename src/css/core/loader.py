"""
Auto-discovery loader for modules via entry_points (Phase 6 P4).

Convention — each module entry point should expose:

``router: APIRouter``       (required)  — app-scoped routes, typically with a prefix
``root_router: APIRouter``  (optional) — root-level routes (e.g. /.well-known/...)
``tortoise_models: list``   (optional) — Tortoise ORM models to register

Entry points are configured in pyproject.toml under [project.entry-points."css.modules"]
and [project.entry-points."css.api_services"].

The loader discovers entry points, imports them, and collects routers and models.
"""

import importlib
import importlib.metadata
from collections.abc import Iterator
from typing import NamedTuple

from fastapi import APIRouter, FastAPI

from css.core.logger import getLogger
log = getLogger(__name__)


class AppRouters(NamedTuple):
    app_name: str
    router: APIRouter | None
    root_router: APIRouter | None


class ModelModule(NamedTuple):
    """Tortoise ORM model module."""
    module_name: str
    model_path: str  # Python dot path for Tortoise config


def build_tortoise_db_url(db_config: dict) -> str:
    """Build Tortoise ORM-compatible asyncpg connection string.

    Supports both TCP (host:port) and Unix socket modes.

    Args:
        db_config: Database config dict with host, port, user, password, database

    Returns:
        Tortoise connection URL like "asyncpg://user:pass@host:port/dbname"
    """
    host = db_config.get("host")
    port = db_config.get("port")
    user = db_config.get("user", "cybersec")
    password = db_config.get("password", "change_me")
    database = db_config.get("database", "cybersec_forensics")

    if host:
        # TCP mode
        port_val = port or 5432
        return f"asyncpg://{user}:{password}@{host}:{port_val}/{database}"
    else:
        # Unix socket mode
        return f"asyncpg://{user}:{password}@/{database}?host=/var/run/postgresql"


def iter_app_routers(entry_point_group: str = "css.modules") -> Iterator[AppRouters]:
    """Yield ``AppRouters`` for every entry point in css.modules or css.api_services.

    Args:
        entry_point_group: Entry point group name (default "css.modules")

    Raises:
        Any exception raised by a broken module — fail-fast so
        missing routes are never silently dropped in production.
    """
    try:
        entry_points = importlib.metadata.entry_points(group=entry_point_group)
    except Exception as exc:
        log.error("Failed to load entry_points group %s: %s", entry_point_group, exc)
        raise

    for ep in entry_points:
        app_name = ep.name

        try:
            # Load the entry point value (module or callable)
            mod_or_callable = ep.load()

            # If it's a callable, call it to get the module
            if callable(mod_or_callable):
                mod = mod_or_callable()
            else:
                mod = mod_or_callable

        except Exception as exc:
            log.error("%s: entry_point load failed: %s", app_name, exc)
            raise

        router = getattr(mod, "router", None)
        root_router = getattr(mod, "root_router", None)

        if router is None and root_router is None:
            log.debug("%s: no router/root_router exposed — skipped", app_name)
            continue

        route_count = len(getattr(router, "routes", [])) + len(getattr(root_router, "routes", []))
        log.info("Discovered endpoints: %s (%d routes)", app_name, route_count)
        yield AppRouters(app_name=app_name, router=router, root_router=root_router)


def iter_model_modules(entry_point_group: str = "css.modules") -> Iterator[ModelModule]:
    """Discover Tortoise ORM model modules from entry points.

    Args:
        entry_point_group: Entry point group name (default "css.modules")

    Yields:
        ModelModule with module_name and Tortoise-compatible path
    """
    try:
        entry_points = importlib.metadata.entry_points(group=entry_point_group)
    except Exception as exc:
        log.error("Failed to load entry_points group %s: %s", entry_point_group, exc)
        return

    for ep in entry_points:
        app_name = ep.name

        try:
            mod_or_callable = ep.load()
            if callable(mod_or_callable):
                mod = mod_or_callable()
            else:
                mod = mod_or_callable

            models = getattr(mod, "tortoise_models", None)
            if models:
                # Assume models list contains Tortoise model classes
                # Convert to module paths (simplified: use module name)
                module_path = getattr(mod, "__name__", f"css.modules.{app_name}")
                yield ModelModule(
                    module_name=app_name,
                    model_path=module_path,
                )
                log.info("Discovered models: %s", app_name)

        except Exception as exc:
            log.error("%s: models discovery failed: %s", app_name, exc)
            # Don't raise — missing models are non-fatal


def build_tortoise_modules() -> dict[str, list[str]]:
    """Build Tortoise ORM modules dict for Tortoise.init().

    Returns:
        Dict mapping app names to lists of model module paths
    """
    modules: dict[str, list[str]] = {}

    # Discover from both css.modules and css.api_services
    for group in ["css.modules", "css.api_services"]:
        for model_module in iter_model_modules(entry_point_group=group):
            if model_module.module_name not in modules:
                modules[model_module.module_name] = []
            if model_module.model_path not in modules[model_module.module_name]:
                modules[model_module.module_name].append(model_module.model_path)

    return modules


def mount_app_routers(app: FastAPI, entry_point_group: str = "css.modules") -> list[str]:
    """Discover and mount all app routers from entry_points onto ``app``.

    Args:
        app: FastAPI application instance
        entry_point_group: Entry point group name (default "css.modules")

    Returns:
        List of app names that were successfully mounted.
    """
    mounted: list[str] = []
    for app_routers in iter_app_routers(entry_point_group=entry_point_group):
        if app_routers.router is not None:
            app.include_router(app_routers.router)
        if app_routers.root_router is not None:
            app.include_router(app_routers.root_router)
        mounted.append(app_routers.app_name)

    if mounted:
        log.info("Mounted %s endpoints: %s", entry_point_group, ", ".join(mounted))
    else:
        log.warning("No endpoints discovered in %s", entry_point_group)

    return mounted

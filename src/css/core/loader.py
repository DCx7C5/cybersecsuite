"""
Auto-discovery loader for modules/<app>/endpoints.py modules.

Convention — each ``modules/<app>/endpoints.py`` may expose:

``router: APIRouter``       (required)  — app-scoped routes, typically with a prefix
``root_router: APIRouter``  (optional) — root-level routes (e.g. /.well-known/...)

The loader discovers all sub-packages of the ``modules`` package, attempts to
import ``modules.<app>.endpoints``, collects the routers, and mounts them onto
a FastAPI application.

Errors from app sub-packages that have no ``endpoints.py`` are silently
ignored (not every app needs HTTP routes). Import errors from modules that
*do* exist are logged and re-raised — broken endpoints are never silently
swallowed so that startup failures surface immediately.

Also supports auto-discovery of Tortoise ORM models:
- ``modules/*/user.py``
- ``api_services/*/user.py``
- ``core/db/models/*.py``
"""

import importlib
import logging
import pkgutil
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

from fastapi import APIRouter, FastAPI

import css.modules as apps_pkg
import css.api_services as api_services_pkg
import css.core.db as core_db_pkg

log = logging.getLogger(__name__)


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


def iter_app_routers() -> Iterator[AppRouters]:
    """Yield ``AppRouters`` for every sub-package of ``modules`` that has an
    ``endpoints.py`` exposing a ``router`` or ``root_router``.

    Raises:
        Any exception raised by a broken endpoints module — fail-fast so
        missing routes are never silently dropped in production.
    """
    for finder, app_name, ispkg in pkgutil.iter_modules(apps_pkg.__path__):
        module_name = f"css.modules.{app_name}.endpoints"

        try:
            mod = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            # Only suppress "no endpoints.py" — re-raise internal import failures
            if exc.name == module_name:
                log.debug("modules/%s: no endpoints module — skipped", app_name)
                continue
            log.error("modules/%s: endpoints import failed: %s", app_name, exc)
            raise
        except Exception as exc:
            log.error("modules/%s: endpoints import crashed: %s", app_name, exc)
            raise

        router = getattr(mod, "router", None)
        root_router = getattr(mod, "root_router", None)

        if router is None and root_router is None:
            log.warning(
                "modules/%s/endpoints.py has neither `router` nor `root_router` — skipped",
                app_name,
            )
            continue

        route_count = len(getattr(router, "routes", [])) + len(getattr(root_router, "routes", []))
        log.info("Discovered endpoints: modules/%s (%d routes)", app_name, route_count)
        yield AppRouters(app_name=app_name, router=router, root_router=root_router)


def iter_model_modules() -> Iterator[ModelModule]:
    """Discover Tortoise ORM model modules.

    Searches:
    - ``modules/*/user.py``
    - ``api_services/*/user.py``
    - ``core/db/models/*.py``

    Yields:
        ModelModule with module_name and Tortoise-compatible path
    """
    # Search modules/*/user.py
    for finder, app_name, ispkg in pkgutil.iter_modules(apps_pkg.__path__):
        module_name = f"css.modules.{app_name}.models"
        try:
            importlib.import_module(module_name)
            yield ModelModule(
                module_name=app_name,
                model_path=f"css.modules.{app_name}.models",
            )
            log.info("Discovered model: %s", module_name)
        except ModuleNotFoundError:
            # No user.py in this module — skip
            pass
        except Exception as exc:
            log.error("modules/%s: models import failed: %s", app_name, exc)
            raise

    # Search api_services/*/user.py
    for finder, svc_name, ispkg in pkgutil.iter_modules(api_services_pkg.__path__):
        module_name = f"css.api_services.{svc_name}.models"
        try:
            importlib.import_module(module_name)
            yield ModelModule(
                module_name=svc_name,
                model_path=f"css.api_services.{svc_name}.models",
            )
            log.info("Discovered model: %s", module_name)
        except ModuleNotFoundError:
            pass
        except Exception as exc:
            log.error("api_services/%s: models import failed: %s", svc_name, exc)
            raise

    # Search core/db/models/*.py
    db_models_path = Path(core_db_pkg.__file__).parent / "models"
    if db_models_path.exists():
        for model_file in db_models_path.glob("*.py"):
            if model_file.name.startswith("_"):
                continue
            model_name = model_file.stem
            module_name = f"css.core.db.models.{model_name}"
            try:
                importlib.import_module(module_name)
                yield ModelModule(
                    module_name=model_name,
                    model_path=module_name,
                )
                log.info("Discovered model: %s", module_name)
            except Exception as exc:
                log.error("core/db/models/%s: import failed: %s", model_name, exc)
                raise


def build_tortoise_modules() -> dict[str, list[str]]:
    """Build Tortoise ORM modules dict for Tortoise.init().

    Returns:
        Dict mapping app names to lists of model module paths
    """
    modules: dict[str, list[str]] = {}

    for model_module in iter_model_modules():
        if model_module.module_name not in modules:
            modules[model_module.module_name] = []
        if model_module.model_path not in modules[model_module.module_name]:
            modules[model_module.module_name].append(model_module.model_path)

    return modules


def mount_app_routers(app: FastAPI) -> list[str]:
    """Discover and mount all app routers onto ``app``.

    Returns the list of app names that were successfully mounted.
    Call this once during app construction (not on every startup).
    """
    mounted: list[str] = []
    for app_routers in iter_app_routers():
        if app_routers.router is not None:
            app.include_router(app_routers.router)
        if app_routers.root_router is not None:
            app.include_router(app_routers.root_router)
        mounted.append(app_routers.app_name)

    if mounted:
        log.info("Mounted app endpoints: %s", ", ".join(mounted))
    else:
        log.warning("No app endpoints discovered — check modules/ sub-packages")

    return mounted

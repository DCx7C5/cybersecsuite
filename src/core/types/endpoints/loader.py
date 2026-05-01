"""
Auto-discovery loader for modules/<app>/endpoints.py modules.

Convention — each ``modules/<app>/endpoints.py`` may expose:

``router: APIRouter``       (required)  — app-scoped routes, typically with a prefix
``root_router: APIRouter``  (optional)  — root-level routes (e.g. /.well-known/...)

The loader discovers all sub-packages of the ``modules`` package, attempts to
import ``modules.<app>.endpoints``, collects the routers, and mounts them onto
a FastAPI application.

Errors from app sub-packages that have no ``endpoints.py`` are silently
ignored (not every app needs HTTP routes). Import errors from modules that
*do* exist are logged and re-raised — broken endpoints are never silently
swallowed so that startup failures surface immediately.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from collections.abc import Iterator
from typing import NamedTuple

from fastapi import APIRouter, FastAPI

import modules as apps_pkg

log = logging.getLogger(__name__)


class AppRouters(NamedTuple):
    app_name: str
    router: APIRouter | None
    root_router: APIRouter | None


def iter_app_routers() -> Iterator[AppRouters]:
    """Yield ``AppRouters`` for every sub-package of ``modules`` that has an
    ``endpoints.py`` exposing a ``router`` or ``root_router``.

    Raises:
        Any exception raised by a broken endpoints module — fail-fast so
        missing routes are never silently dropped in production.
    """
    for finder, app_name, ispkg in pkgutil.iter_modules(apps_pkg.__path__):
        module_name = f"modules.{app_name}.endpoints"

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

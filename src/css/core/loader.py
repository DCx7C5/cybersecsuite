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
import importlib.util
import os
import pkgutil
from collections.abc import Iterator
from typing import NamedTuple
from urllib.parse import parse_qs, urlparse

from fastapi import APIRouter, FastAPI

from css.core.logger import getLogger
log = getLogger(__name__)

DbConfigValue = str | int | float | bool | None


def _as_int(value: DbConfigValue, default: int) -> int:
    if value is None:
        return default
    return int(value)


class AppRouters(NamedTuple):
    app_name: str
    router: APIRouter | None
    root_router: APIRouter | None


class ModelModule(NamedTuple):
    """Tortoise ORM model module."""
    module_name: str
    model_path: str  # Python dot path for Tortoise config


def build_tortoise_db_url(db_config: dict[str, DbConfigValue]) -> str:
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


def build_tortoise_connection(db_config: dict[str, DbConfigValue]) -> dict[str, object]:
    """Build asyncpg connection config with explicit pool credentials.

    This avoids URL-only mode so asyncpg pool settings (min/max size and
    command timeout) are always applied by Tortoise.
    """

    credentials: dict[str, object] = {
        "minsize": _as_int(db_config.get("min_size"), 5),
        "maxsize": _as_int(db_config.get("max_size"), 20),
        "command_timeout": _as_int(db_config.get("command_timeout"), 30),
    }

    for key in ("max_cached_statement_lifetime", "max_cacheable_statement_size"):
        value = db_config.get(key)
        if value is None:
            continue
        credentials[key] = int(value)

    url = db_config.get("url")
    if isinstance(url, str) and url:
        parsed = urlparse(url)
        if parsed.username:
            credentials["user"] = parsed.username
        if parsed.password:
            credentials["password"] = parsed.password
        if parsed.hostname:
            credentials["host"] = parsed.hostname
        if parsed.port is not None:
            credentials["port"] = int(parsed.port)
        database = parsed.path.lstrip("/")
        if database:
            credentials["database"] = database

        query = parse_qs(parsed.query)
        if "host" in query and query["host"]:
            credentials["host"] = query["host"][-1]
        if "port" in query and query["port"]:
            credentials["port"] = int(query["port"][-1])
    else:
        host = db_config.get("host")
        port = db_config.get("port")
        if host:
            credentials["host"] = host
            credentials["port"] = int(port) if port else 5432
        else:
            credentials["host"] = "/var/run/postgresql"
        credentials["user"] = db_config.get("user", "cybersec")
        credentials["password"] = db_config.get("password", "change_me")
        credentials["database"] = db_config.get("database", "cybersec_forensics")

    return {
        "engine": "tortoise.backends.asyncpg",
        "credentials": credentials,
    }


def iter_app_routers(entry_point_group: str = "css.modules") -> Iterator[AppRouters]:
    """Yield ``AppRouters`` for every entry point in css.modules or css.api_services.

    Args:
        entry_point_group: Entry point group name (default "css.modules")

    Notes:
        Broken modules are logged and skipped so the ASGI app can still boot
        with healthy routers.
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
            continue

        router = getattr(mod, "router", None)
        root_router = getattr(mod, "root_router", None)

        if router is None and root_router is None:
            log.debug("%s: no router/root_router exposed — skipped", app_name)
            continue

        route_count = len(getattr(router, "routes", [])) + len(getattr(root_router, "routes", []))
        log.info("Discovered endpoints: %s (%d routes)", app_name, route_count)
        yield AppRouters(app_name=app_name, router=router, root_router=root_router)


def _get_declared_entrypoint_names(entry_point_group: str) -> set[str]:
    try:
        entry_points = importlib.metadata.entry_points(group=entry_point_group)
    except Exception as exc:
        log.error("Failed to load entry_points group %s: %s", entry_point_group, exc)
        return set()

    return {entry_point.name for entry_point in entry_points}


def _discover_router_modules(package_name: str = "css.modules") -> set[str]:
    package = importlib.import_module(package_name)
    package_paths = getattr(package, "__path__", None)
    if not package_paths:
        return set()

    router_modules: set[str] = set()
    for _, module_name, is_pkg in pkgutil.iter_modules(package_paths):
        if not is_pkg:
            continue
        endpoints_module_name = f"{package_name}.{module_name}.endpoints"
        try:
            endpoints_mod = importlib.import_module(endpoints_module_name)
        except ModuleNotFoundError as exc:
            if exc.name == endpoints_module_name:
                continue
            log.warning("%s: failed to import endpoints module: %s", endpoints_module_name, exc)
            continue
        except Exception as exc:
            log.warning("%s: failed to import endpoints module: %s", endpoints_module_name, exc)
            continue

        if getattr(endpoints_mod, "router", None) is not None or getattr(endpoints_mod, "root_router", None) is not None:
            router_modules.add(module_name)

    return router_modules


def validate_module_entrypoint_coverage(entry_point_group: str = "css.modules") -> None:
    """Ensure every router-bearing module is declared as an entry-point.

    Modules can be explicitly suppressed by setting
    ``CSS_DISABLED_MODULE_ENTRYPOINTS=mod1,mod2``.
    """
    if entry_point_group != "css.modules":
        return

    disabled_modules = {
        value.strip()
        for value in os.environ.get("CSS_DISABLED_MODULE_ENTRYPOINTS", "").split(",")
        if value.strip()
    }
    declared_modules = _get_declared_entrypoint_names(entry_point_group)
    router_modules = _discover_router_modules("css.modules")
    missing_modules = sorted(router_modules - declared_modules - disabled_modules)
    if missing_modules:
        log.warning(
            "css.modules: entry-point registration missing for routers: %s",
            ", ".join(missing_modules),
        )


def _discover_model_paths(mod: object) -> set[str]:
    model_paths: set[str] = set()
    models = getattr(mod, "tortoise_models", None)
    if isinstance(models, (list, tuple, set)):
        for model in models:
            module_path = getattr(model, "__module__", None)
            if isinstance(module_path, str) and module_path:
                model_paths.add(module_path)

    module_name = getattr(mod, "__name__", "")
    if isinstance(module_name, str) and module_name:
        package_name = module_name.rsplit(".", 1)[0]
        fallback_path = f"{package_name}.models"
        try:
            if importlib.util.find_spec(fallback_path) is not None:
                model_paths.add(fallback_path)
        except ModuleNotFoundError:
            pass

    return model_paths


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

            model_paths = _discover_model_paths(mod)
            if model_paths:
                for model_path in sorted(model_paths):
                    yield ModelModule(module_name=app_name, model_path=model_path)
                log.info("Discovered models for %s: %s", app_name, ", ".join(sorted(model_paths)))

        except Exception as exc:
            log.error("%s: models discovery failed: %s", app_name, exc)
            fallback_candidates: list[str] = []
            value = ep.value
            if isinstance(value, str) and value:
                target = value.split(":", 1)[0]
                if target.endswith(".endpoints"):
                    target = target[: -len(".endpoints")]
                fallback_candidates.append(f"{target}.models")
                fallback_candidates.append("css.core.db.models")

            for model_path in fallback_candidates:
                try:
                    if importlib.util.find_spec(model_path) is None:
                        continue
                except ModuleNotFoundError:
                    continue
                yield ModelModule(module_name=app_name, model_path=model_path)
                break


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
    validate_module_entrypoint_coverage(entry_point_group=entry_point_group)

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

"""Bootstrap Tortoise ORM — initializes schema and intelligence data."""

import os
import asyncpg
from tortoise.context import TortoiseContext

_initialized = False
_ctx: TortoiseContext | None = None


def get_database_config() -> dict:
    """Read DB config from environment. Socket paths (/) omit port automatically."""
    host = os.environ.get("CYBERSEC_DB_HOST", "localhost")
    cfg: dict = {
        "host": host,
        "user": os.environ.get("CYBERSEC_DB_USER", "cybersec"),
        "password": os.environ.get("CYBERSEC_DB_PASSWORD", ""),
        "database": os.environ.get("CYBERSEC_DB_NAME", "cybersec_forensics"),
    }
    # Always include port — asyncpg needs it to construct the Unix socket
    # filename (e.g. /tmp/.s.PGSQL.5432) even when host is a directory path.
    cfg["port"] = int(os.environ.get("CYBERSEC_DB_PORT", "5432"))
    return cfg


def get_tortoise_config() -> dict:
    from db.models import MODEL_MODULES

    return {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": get_database_config(),
            }
        },
        "apps": {
            "models": {
                "models": MODEL_MODULES,
                "default_connection": "default",
            }
        },
        "use_tz": False,
        "timezone": "UTC",
    }


async def _ensure_database_exists(db_config: dict) -> None:
    """Create target DB if absent."""
    db_name = db_config["database"]
    connect_kwargs: dict = {
        "host": db_config.get("host", "localhost"),
        "user": db_config["user"],
        "password": db_config["password"],
        "database": "postgres",
    }
    if "port" in db_config:
        connect_kwargs["port"] = db_config["port"]
    conn = await asyncpg.connect(**connect_kwargs)
    try:
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", db_name)
        if not exists:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
    finally:
        await conn.close()


async def init_tortoise_async(
    create_db: bool = False,
    bootstrap_intel: bool = False,
) -> None:
    """Initialize Tortoise ORM. Optionally create DB, tables, and seed intelligence."""
    global _initialized, _ctx
    if not _initialized:
        db_config = get_database_config()
        if create_db:
            await _ensure_database_exists(db_config)
        _ctx = TortoiseContext()
        await _ctx.__aenter__()
        await _ctx.init(config=get_tortoise_config(), _enable_global_fallback=True)
        _initialized = True
    if create_db and _ctx is not None:
        await _ctx.generate_schemas(safe=True)
    if bootstrap_intel:
        await bootstrap_intelligence_async(force=False, include_feeds=True)


async def close_tortoise() -> None:
    global _initialized, _ctx
    if _initialized and _ctx is not None:
        await _ctx.__aexit__(None, None, None)
        _ctx = None
        _initialized = False


async def bootstrap_intelligence_async(
    force: bool = False,
    include_feeds: bool = True,
) -> dict:
    """Bootstrap NVD/CVE, CWE, CAPEC, MITRE, MISP, OpenCTI intelligence into PostgreSQL."""
    from db.intel_loader import bootstrap_intelligence_async as _load

    return await _load(force=force, include_feeds=include_feeds)


def get_status() -> dict:
    return {
        "initialized": _initialized,
        "config": get_database_config(),
    }


async def get_database_health_async(
    check_connection: bool = True,
    include_counts: bool = False,
    create_db: bool = False,
    bootstrap_intel: bool = False,
) -> dict:
    """Full database health check with optional table counts."""
    if create_db:
        await init_tortoise_async(create_db=True, bootstrap_intel=bootstrap_intel)

    health: dict = {
        "status": "ok",
        "config": get_database_config(),
        "initialized": _initialized,
    }

    if not check_connection:
        return health

    try:
        await init_tortoise_async()
        from tortoise import Tortoise

        # Use ORM describe_model to list registered tables instead of raw SQL
        registered_models = Tortoise.apps.get("models", {})
        tables = sorted(
            model.Meta.table
            for model in registered_models.values()
            if hasattr(model, "Meta") and hasattr(model.Meta, "table")
        )

        health.update(
            {
                "table_count": len(tables),
                "tables": tables,
            }
        )
    except Exception as exc:
        health["status"] = "error"
        health["error"] = str(exc)
        health["intel_bootstrapped"] = False
        return health

    if include_counts and health["status"] == "ok":
        try:
            from tortoise import Tortoise

            registered_models = Tortoise.apps.get("models", {})
            counts = {}
            for model in registered_models.values():
                if hasattr(model, "Meta") and hasattr(model.Meta, "table"):
                    table_name = model.Meta.table
                    counts[table_name] = await model.all().count()
            health["counts"] = counts
        except Exception:
            pass

    health["intel_bootstrapped"] = False
    return health

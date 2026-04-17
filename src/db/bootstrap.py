"""Bootstrap Tortoise ORM for csdb-mcp — global scope, initial tables only."""
import os
import asyncpg
from tortoise import Tortoise

_initialized = False


def get_database_config() -> dict:
    """Read DB config from environment. Socket paths (/) omit port automatically."""
    host = os.environ.get("CYBERSEC_DB_HOST", "localhost")
    cfg: dict = {
        "host": host,
        "user": os.environ.get("CYBERSEC_DB_USER", "cybersec"),
        "password": os.environ.get("CYBERSEC_DB_PASSWORD", ""),
        "database": os.environ.get("CYBERSEC_DB_NAME", "cybersec_forensics"),
    }
    if not host.startswith("/"):
        cfg["port"] = int(os.environ.get("CYBERSEC_DB_PORT", "5432"))
    return cfg


def get_tortoise_config() -> dict:
    from skills.csdb.db.models import MODEL_MODULES
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
    """Create target DB if absent. DDL-only — allowed exception per project rules."""
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


async def init_tortoise_async(create_db: bool = False) -> None:
    """Initialize Tortoise ORM. Optionally create DB + tables."""
    global _initialized
    if not _initialized:
        db_config = get_database_config()
        if create_db:
            await _ensure_database_exists(db_config)
        await Tortoise.init(config=get_tortoise_config())
        _initialized = True
    if create_db:
        await Tortoise.generate_schemas(safe=True)


async def close_tortoise() -> None:
    global _initialized
    if _initialized:
        await Tortoise.close_connections()
        _initialized = False


def get_status() -> dict:
    return {
        "initialized": _initialized,
        "config": get_database_config(),
    }


async def get_health_async(check_connection: bool = True) -> dict:
    """Full health check — connects to DB, lists tables."""
    health: dict = {
        "status": "ok",
        "config": get_database_config(),
        "initialized": _initialized,
    }
    if not check_connection:
        return health
    try:
        await init_tortoise_async()
        conn = Tortoise.get_connection("default")
        version_result = await conn.execute_query("SELECT version() AS version")
        tables_result = await conn.execute_query(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
        tables = [row["table_name"] for row in tables_result[1]]
        health.update({
            "database_version": version_result[1][0]["version"] if version_result[1] else None,
            "table_count": len(tables),
            "tables": tables,
        })
    except Exception as exc:
        health["status"] = "error"
        health["error"] = str(exc)
    return health


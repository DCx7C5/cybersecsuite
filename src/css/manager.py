"""
CyberSecSuite CLI entry point.

Provides commands for:
- Database initialization
- FastAPI server startup
- Health checks
"""

import asyncio
import logging
from types import CoroutineType
from typing import Any

import click
import uvicorn
from tortoise.context import TortoiseContext

from css.config import POSTGRES_DATABASE, A2A_SERVER
from css.core.loader import build_tortoise_modules, build_tortoise_db_url

log = logging.getLogger(__name__)


def init_tortoise_db(db_config: dict, apps: dict[str, list[str]] | None = None) -> CoroutineType[
    Any, Any, TortoiseContext]:
    """Initialize Tortoise ORM with the given database configuration.

    Supports both TCP (host:port) and Unix socket modes.

    Args:
        db_config: Database configuration dict with host, port, user, password, database
        apps: Optional Tortoise apps dict. Auto-discovered if None.
    """
    from tortoise import Tortoise

    db_url = build_tortoise_db_url(db_config)

    tortoise_config = {
        "connections": {"default": db_url},
        "apps": apps or build_tortoise_modules(),
    }

    log.info("Initializing Tortoise ORM with %s", db_url.replace(db_config.get("password", ""), "***"))
    return Tortoise.init(config=tortoise_config)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """CyberSecSuite CLI - Forensics and threat intelligence platform."""
    pass


@cli.command()
@click.option("--db-host", default=None, help="PostgreSQL host (default: from config)")
@click.option("--db-port", default=None, help="PostgreSQL port (default: from config)")
@click.option("--db-user", default=None, help="PostgreSQL user (default: from config)")
@click.option("--db-password", default=None, help="PostgreSQL password (default: from config)")
@click.option("--db-name", default=None, help="Database name (default: from config)")
@click.option("--generate-schemas/--no-generate-schemas", default=True, help="Generate DB schemas")
def init_db(db_host, db_port, db_user, db_password, db_name, generate_schemas):
    """Initialize the database and create tables."""
    from css.config import POSTGRES_DATABASE
    
    db_config = {
        "host": db_host or POSTGRES_DATABASE.get("host"),
        "port": db_port or POSTGRES_DATABASE.get("port"),
        "user": db_user or POSTGRES_DATABASE.get("user"),
        "password": db_password or POSTGRES_DATABASE.get("password"),
        "database": db_name or POSTGRES_DATABASE.get("database"),
    }

    apps = build_tortoise_modules()
    if not apps:
        click.echo("No model modules discovered — database will be empty.")
        return

    click.echo(f"Discovered {len(apps)} app modules with models:")
    for app_name, modules in apps.items():
        click.echo(f"  - {app_name}: {', '.join(modules)}")

    async def _init():
        await init_tortoise_db(db_config, apps)
        if generate_schemas:
            from tortoise import Tortoise
            await Tortoise.generate_schemas()
        click.echo("Database initialized successfully!")
        from tortoise import Tortoise
        await Tortoise.close_connections()

    asyncio.run(_init())


@cli.command()
@click.option("--host", default=None, help="Bind host (default: from config / ASGI_HOST env)")
@click.option("--port", default=None, type=int, help="Bind port (default: from config / ASGI_PORT env)")
@click.option("--reload", is_flag=True, default=False, help="Enable hot-reload (dev only)")
@click.option("--workers", default=1, type=int, help="Number of worker processes (prod, no reload)")
@click.option("--log-level", default=None, help="Log level: debug|info|warning|error|critical")
def serve(host, port, reload, workers, log_level):
    """Start the CyberSecSuite ASGI server."""
    import os
    from css.config import LOG_LEVEL

    server_host = host or os.environ.get("ASGI_HOST", A2A_SERVER.get("host", "127.0.0.1"))
    server_port = int(port or os.environ.get("ASGI_PORT", A2A_SERVER.get("port", 8000)))
    effective_log_level = log_level or LOG_LEVEL

    click.echo(f"Starting CyberSecSuite on http://{server_host}:{server_port}")
    if reload:
        click.echo("  Hot-reload enabled (dev mode)")
    elif workers > 1:
        click.echo(f"  Workers: {workers}")

    uvicorn.run(
        # String import required for --reload; fine for normal start too
        "css.core.asgi.app:app",
        host=server_host,
        port=server_port,
        reload=reload,
        workers=workers if not reload else 1,
        log_level=effective_log_level,
    )


@cli.command(name="run")
@click.pass_context
def run_alias(ctx):
    """Alias for 'serve'."""
    ctx.invoke(serve)



@cli.command()
def check():
    """Run system health checks."""
    click.echo("CyberSecSuite health check:")
    
    # Check database connection
    async def _check():
        import asyncpg
        
        db_config = POSTGRES_DATABASE
        try:
            conn = await asyncpg.connect(
                host=db_config.get("host"),
                port=int(db_config.get("port", 5432)),
                user=db_config.get("user"),
                password=db_config.get("password"),
                database=db_config.get("database"),
            )
            await conn.close()
            click.echo("  ✓ Database connection: OK")
        except Exception as e:
            click.echo(f"  ✗ Database connection: {e}")
    
    asyncio.run(_check())


def main():
    """Main entry point."""
    cli()


def main_sync():
    """Sync wrapper for pyproject.toml script entry."""
    main()


if __name__ == "__main__":
    main()

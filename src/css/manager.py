"""
CyberSecSuite CLI entry point.

Provides commands for:
- Database initialization
- FastAPI server startup (managed subprocess)
- Health checks
"""

from css.core.logger import getLogger
import asyncio
import os
import signal
from pathlib import Path
from typing import Any, Protocol, cast

import click

from css.core.settings.config import POSTGRES_DATABASE, A2A_SERVER
from css.core.asgi.process import UvicornProcessManager
from css.core.loader import build_tortoise_connection, build_tortoise_modules, build_tortoise_db_url
from css.core.settings.config import LOG_LEVEL

log = getLogger(__name__)


class _TortoiseApi(Protocol):
    @staticmethod
    async def init(*, config: dict[str, Any]) -> None: ...

    @staticmethod
    async def generate_schemas() -> None: ...

    @staticmethod
    async def close_connections() -> None: ...


def _tortoise_api() -> _TortoiseApi:
    from tortoise import Tortoise

    return cast(_TortoiseApi, cast(object, Tortoise))


def _require_str(value: object, key_name: str) -> str:
    if value is None:
        raise click.ClickException(f"Missing required config value: {key_name}")
    if not isinstance(value, str):
        raise click.ClickException(f"Invalid config value type for {key_name}: expected str")
    return value


async def _serve_impl(
    host: str | None,
    port: int | None,
    reload: bool,
    workers: int,
    log_level: str | None,
) -> None:

    configured_host = A2A_SERVER.get("host", "127.0.0.1")
    server_host = str(host or os.environ.get("ASGI_HOST") or configured_host)

    configured_port = A2A_SERVER.get("port", 8000)
    server_port = int(port if port is not None else (os.environ.get("ASGI_PORT") or configured_port))
    effective_log_level = str(log_level or LOG_LEVEL).lower()

    frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    has_frontend_build = frontend_dist.is_dir()
    click.echo(f"Starting CyberSecSuite on http://{server_host}:{server_port}")
    if has_frontend_build:
        click.echo("  Frontend: serving static build")
    else:
        click.echo("  Frontend: NOT available (no dist/ build found)")
        click.echo(f"    Build with: cd src/frontend && bun run build")
        click.echo(f"    Dev server: cd src/frontend && bun run dev  (→ http://localhost:5173)")
    if reload:
        click.echo("  Hot-reload enabled (dev mode)")
    elif workers > 1:
        click.echo(f"  Workers: {workers}")
    click.echo("Press Ctrl+C to stop the server.")

    shutdown = asyncio.Event()

    def _on_shutdown() -> None:
        if shutdown.is_set():
            return
        click.echo("\nGracefully shutting down...")
        shutdown.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _on_shutdown)
        except NotImplementedError:
            pass

    manager = UvicornProcessManager(
        host=server_host,
        port=server_port,
        reload=reload,
        workers=workers,
        log_level=effective_log_level,
    )

    try:
        await manager.start()
        await shutdown.wait()
    finally:
        click.echo("Waiting for active requests to drain...")
        await manager.stop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.remove_signal_handler(sig)
            except (ValueError, NotImplementedError):
                pass
        click.echo("Server stopped.")


async def init_tortoise_db(db_config: dict[str, Any], apps: dict[str, list[str]] | None = None) -> None:
    """Initialize Tortoise ORM with the given database configuration.

    Supports both TCP (host:port) and Unix socket modes.

    Args:
        db_config: Database configuration dict with host, port, user, password, database
        apps: Optional Tortoise apps dict. Auto-discovered if None.
    """
    db_url = build_tortoise_db_url(db_config)

    tortoise_config: dict[str, Any] = {
        "connections": {"default": build_tortoise_connection(db_config)},
        "apps": apps or build_tortoise_modules(),
    }

    password = str(db_config.get("password") or "")
    log.info("Initializing Tortoise ORM with %s", db_url.replace(password, "***"))
    await _tortoise_api().init(config=tortoise_config)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """CyberSecSuite CLI - Forensics and threat intelligence platform."""
    pass


@cli.command()
@click.option("--db-host", default=None, help="PostgreSQL host (default: from config)")
@click.option("--db-port", default=None, type=int, help="PostgreSQL port (default: from config)")
@click.option("--db-user", default=None, help="PostgreSQL user (default: from config)")
@click.option("--db-password", default=None, help="PostgreSQL password (default: from config)")
@click.option("--db-name", default=None, help="Database name (default: from config)")
@click.option("--generate-schemas/--no-generate-schemas", default=True, help="Generate DB schemas")
def init_db(
    db_host: str | None,
    db_port: int | None,
    db_user: str | None,
    db_password: str | None,
    db_name: str | None,
    generate_schemas: bool,
) -> None:
    """Initialize the database and create tables."""

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
            await _tortoise_api().generate_schemas()
        click.echo("Database initialized successfully!")
        await _tortoise_api().close_connections()

    asyncio.run(_init())


@cli.command()
@click.option("--host", default=None, help="Bind host (default: from config / ASGI_HOST env)")
@click.option("--port", default=None, type=int, help="Bind port (default: from config / ASGI_PORT env)")
@click.option("--reload", is_flag=True, default=False, help="Enable hot-reload (dev only)")
@click.option("--workers", default=1, type=int, help="Number of worker processes (prod, no reload)")
@click.option("--log-level", default=None, help="Log level: debug|info|warning|error|critical")
def serve(
    host: str | None,
    port: int | None,
    reload: bool,
    workers: int,
    log_level: str | None,
) -> None:
    """Start the CyberSecSuite ASGI server."""
    try:
        asyncio.run(_serve_impl(host, port, reload, workers, log_level))
    except KeyboardInterrupt:
        click.echo("\nServer stopped.")


@cli.command(name="run")
@click.option("--host", default=None, help="Bind host (default: from config / ASGI_HOST env)")
@click.option("--port", default=None, type=int, help="Bind port (default: from config / ASGI_PORT env)")
@click.option("--reload", is_flag=True, default=False, help="Enable hot-reload (dev only)")
@click.option("--workers", default=1, type=int, help="Number of worker processes (prod, no reload)")
@click.option("--log-level", default=None, help="Log level: debug|info|warning|error|critical")
def run_alias(
    host: str | None,
    port: int | None,
    reload: bool,
    workers: int,
    log_level: str | None,
) -> None:
    """Alias for 'serve'."""
    try:
        asyncio.run(_serve_impl(host, port, reload, workers, log_level))
    except KeyboardInterrupt:
        click.echo("\nServer stopped.")



@cli.command()
def check() -> None:
    """Run system health checks."""
    click.echo("CyberSecSuite health check:")

    # Check database connection
    async def _check() -> None:
        import asyncpg

        db_config = POSTGRES_DATABASE
        db_host = _require_str(db_config.get("host"), "POSTGRES_DATABASE.host")
        db_user = _require_str(db_config.get("user"), "POSTGRES_DATABASE.user")
        db_name = _require_str(db_config.get("database"), "POSTGRES_DATABASE.database")

        try:
            conn = await asyncpg.connect(
                host=db_host,
                port=int(db_config.get("port", 5432)),
                user=db_user,
                password=db_config.get("password"),
                database=db_name,
            )
            await conn.close()
            click.echo("  ✓ Database connection: OK")
        except (asyncpg.PostgresError, OSError, ValueError) as exc:
            click.echo(f"  ✗ Database connection: {exc}")

    asyncio.run(_check())


def main() -> None:
    """Main entry point."""
    cli()


def main_sync() -> None:
    """Sync wrapper for pyproject.toml script entry."""
    main()


if __name__ == "__main__":
    main()

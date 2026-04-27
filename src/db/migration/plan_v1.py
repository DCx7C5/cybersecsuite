"""plan_v1 migration — add target_files column to tasks table.

Adds target_files column (TEXT, DEFAULT '') to tasks table for storing JSON-serialized
list of file paths that an agent will modify. This enables scoping of ruff fixes to
only changed files as managed by agent_hooks.

Idempotent: uses ADD COLUMN IF NOT EXISTS so it can be re-run safely.

Usage:
    uv run python -m db.migration.plan_v1

Reference:
    src/db/models/plan.py — Task model
    src/hooks/agent_hooks.py — Ruff scoping and dry-run mode
"""
from __future__ import annotations

import asyncio
import logging
from typing import Final

import asyncpg

logger = logging.getLogger("db.migration.plan_v1")

PLAN_TABLES: Final[list[str]] = [
    "tasks",
]

# SQL migrations
MIGRATIONS: Final[dict[str, str]] = {
    "tasks": """
    ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS target_files TEXT DEFAULT '';
    """,
}


async def run_migrations(pool: asyncpg.Pool) -> None:
    """Execute all migrations idempotently."""
    async with pool.acquire() as conn:
        for table, sql in MIGRATIONS.items():
            try:
                await conn.execute(sql)
                logger.info(f"✓ Applied migration for {table}")
            except asyncpg.PostgresError as e:
                logger.error(f"✗ Failed to migrate {table}: {e}")
                raise


async def main() -> None:
    """Connect to database and run migrations."""
    import os
    
    host = os.environ.get("CYBERSEC_DB_HOST", "localhost")
    port = int(os.environ.get("CYBERSEC_DB_PORT", "5432"))
    user = os.environ.get("CYBERSEC_DB_USER", "postgres")
    password = os.environ.get("CYBERSEC_DB_PASSWORD", "")
    dbname = os.environ.get("CYBERSEC_DB_NAME", "cybersec")
    
    logger.info(f"Connecting to {user}@{host}:{port}/{dbname}")
    
    dsn = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)
    
    try:
        await run_migrations(pool)
        logger.info("✓ All migrations completed successfully")
    finally:
        await pool.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
    )
    asyncio.run(main())

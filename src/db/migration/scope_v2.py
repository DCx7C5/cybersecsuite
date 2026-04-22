"""scope_v2 migration — add 5-level scope columns to ScopedEntry-derived tables.

Adds three columns to every table that inherits ScopedEntry:
    runtime_id    VARCHAR(64)  NULL  — container/pod runtime identity
    worktree_path VARCHAR(1024) NULL — absolute path to .ccs/<runtime-id>/worktree-<SID>/
    scope_level   VARCHAR(16)  NULL  DEFAULT 'session' — one of: global, app, project, runtime, session

Idempotent: uses ADD COLUMN IF NOT EXISTS so it can be re-run safely.

Usage:
    uv run python -m db.migration.scope_v2

Referenz:
    plan.md T045 — Phase 5: Database Optimization
    plan.md §1 Scope Model (5 Levels)
    src/db/models/scope.py — ScopedEntry abstract base
"""
from __future__ import annotations

import asyncio
import logging
from typing import Final

import asyncpg

logger = logging.getLogger("db.migration.scope_v2")

# Tables that inherit ScopedEntry (ORM-managed, non-abstract)
SCOPED_TABLES: Final[list[str]] = [
    "findings",
    "iocs",
    "risks",
    "mitre_techniques",
    "case_intakes",
    "shared_entries",
    "artifacts",
    "audit_logs",
    "compliance_checks",
    "defense_recommendations",
    "vulnerabilities",
    "yara_rules",
    "user_guidances",
    "baselines",
    "forensic_iocs",
    "threat_profiles",
]

_COLUMNS: Final[list[tuple[str, str, str]]] = [
    # (name, type, default)
    ("runtime_id",    "VARCHAR(64)",   "NULL"),
    ("worktree_path", "VARCHAR(1024)", "NULL"),
    ("scope_level",   "VARCHAR(16)",   "DEFAULT 'session'"),
]

_ADD_COLUMN_SQL = "ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {type} {default};"
_ADD_INDEX_SQL  = "CREATE INDEX IF NOT EXISTS idx_{table}_scope_level ON {table}(scope_level);"


async def _run_migration(dsn: str) -> dict[str, list[str]]:
    """Execute the scope_v2 migration and return a report of changes."""
    conn: asyncpg.Connection = await asyncpg.connect(dsn)
    report: dict[str, list[str]] = {}
    try:
        for table in SCOPED_TABLES:
            applied: list[str] = []
            for col, dtype, default in _COLUMNS:
                sql = _ADD_COLUMN_SQL.format(table=table, col=col, type=dtype, default=default)
                try:
                    await conn.execute(sql)
                    applied.append(col)
                    logger.debug("  ✓ %s.%s", table, col)
                except asyncpg.UndefinedTableError:
                    logger.warning("Table '%s' does not exist — skipping", table)
                    break
                except Exception as exc:
                    logger.warning("Could not add %s.%s: %s", table, col, exc)
            # Add index on scope_level for filtering performance
            if "scope_level" in applied:
                try:
                    await conn.execute(_ADD_INDEX_SQL.format(table=table))
                    logger.debug("  ✓ idx_%s_scope_level", table)
                except Exception as exc:
                    logger.warning("Could not create index on %s.scope_level: %s", table, exc)
            if applied:
                report[table] = applied
    finally:
        await conn.close()
    return report


async def migrate() -> None:
    """Run scope_v2 migration."""
    from db.bootstrap import get_database_config  # noqa: PLC0415
    cfg = get_database_config()
    dsn = (
        f"postgresql://{cfg['user']}:{cfg.get('password', '')}@"
        f"{cfg['host']}:{cfg.get('port', 5432)}/{cfg['database']}"
    )
    display = f"{cfg['host']}:{cfg.get('port', 5432)}/{cfg['database']}"
    logger.info("Starting scope_v2 migration on %s", display)
    report = await _run_migration(dsn)
    if report:
        for table, cols in report.items():
            logger.info("  %s: added %s", table, ", ".join(cols))
        logger.info("scope_v2 migration complete — %d table(s) updated", len(report))
    else:
        logger.info("scope_v2 migration: nothing to do (columns already exist)")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(migrate())


if __name__ == "__main__":
    main()

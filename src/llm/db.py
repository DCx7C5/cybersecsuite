"""asyncpg helpers for llm_sessions and llm_calls.

These helpers bypass Tortoise ORM so they can be called from
scripts/worktree-session-manager.py (which may run outside the ASGI process)
and from fire-and-forget background tasks.
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

log = logging.getLogger("llm.db")

_pool = None


def _dsn() -> str:
    explicit = os.environ.get("CYBERSEC_DB_DSN")
    if explicit:
        return explicit
    return (
        "postgresql://{user}:{pw}@{host}:{port}/{db}".format(
            user=os.environ.get("CYBERSEC_DB_USER", "cybersec"),
            pw=os.environ.get("CYBERSEC_DB_PASSWORD", ""),
            host=os.environ.get("CYBERSEC_DB_HOST", "localhost"),
            port=os.environ.get("CYBERSEC_DB_PORT", "5432"),
            db=os.environ.get("CYBERSEC_DB_NAME", "cybersec_forensics"),
        )
    )


async def get_pool():
    """Return (or create) the shared asyncpg connection pool."""
    global _pool
    if _pool is None:
        import asyncpg
        _pool = await asyncpg.create_pool(_dsn(), min_size=1, max_size=5)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def open_session(sid: str, repo_root: str = "", branch: str = "") -> None:
    """Create an llm_sessions row for this worktree. Idempotent (ON CONFLICT DO NOTHING)."""
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO llm_sessions (sid, repo_root, branch, opened_at)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (sid) DO NOTHING
        """,
        sid,
        repo_root,
        branch,
        datetime.now(timezone.utc),
    )
    log.info("llm_session opened sid=%s", sid)


async def _ensure_session_exists(pool, sid: str) -> None:
    """Ensure a session row exists before inserting llm_calls rows."""
    await pool.execute(
        """
        INSERT INTO llm_sessions (sid, repo_root, branch, opened_at)
        VALUES ($1, '', '', $2)
        ON CONFLICT (sid) DO NOTHING
        """,
        sid,
        datetime.now(timezone.utc),
    )



async def close_session(sid: str) -> dict[str, Any]:
    """Set closed_at on the session. Returns summary dict (totals from OO, not PG)."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        UPDATE llm_sessions SET closed_at = $2
        WHERE sid = $1
        RETURNING sid, total_input_tokens, total_output_tokens, total_cost_usd, total_calls
        """,
        sid,
        datetime.now(timezone.utc),
    )
    return dict(row) if row else {}


async def cost_report(sid: str) -> dict[str, Any]:
    """Return session metadata. Per-model breakdown is now in OpenObserve (llm-calls stream)."""
    pool = await get_pool()
    session = await pool.fetchrow(
        "SELECT * FROM llm_sessions WHERE sid=$1", sid
    )
    return {
        "sid": sid,
        "session": dict(session) if session else {},
        "by_model": [],
    }


def run_sync(coro) -> Any:
    """Run an async coroutine synchronously (for CLI use)."""
    return asyncio.run(coro)

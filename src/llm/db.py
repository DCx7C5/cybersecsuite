"""asyncpg helpers for llm_sessions and llm_calls.

These helpers bypass Tortoise ORM so they can be called from
worktree-session-manager.py (which may run outside the ASGI process)
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


async def persist_call(
    *,
    sid: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int = 0,
    cache_write_tokens: int = 0,
    cost_usd: Decimal,
    latency_ms: float,
    stream: bool,
    success: bool,
    error: str | None = None,
    request_id: str | None = None,
) -> None:
    """Insert one llm_calls row. Intended to be called as a fire-and-forget task."""
    pool = await get_pool()
    await _ensure_session_exists(pool, sid)
    await pool.execute(
        """
        INSERT INTO llm_calls
          (sid, model, input_tokens, output_tokens,
           cache_read_tokens, cache_write_tokens,
           cost_usd, latency_ms, stream, success, error, request_id, called_at)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
        """,
        sid,
        model,
        input_tokens,
        output_tokens,
        cache_read_tokens,
        cache_write_tokens,
        float(cost_usd),
        latency_ms,
        stream,
        success,
        error,
        request_id,
        datetime.now(timezone.utc),
    )


async def close_session(sid: str) -> dict[str, Any]:
    """Set closed_at, aggregate totals. Returns summary dict."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        UPDATE llm_sessions SET
            closed_at           = $2,
            total_input_tokens  = (SELECT COALESCE(SUM(input_tokens),  0) FROM llm_calls WHERE sid=$1),
            total_output_tokens = (SELECT COALESCE(SUM(output_tokens), 0) FROM llm_calls WHERE sid=$1),
            total_cost_usd      = (SELECT COALESCE(SUM(cost_usd),      0) FROM llm_calls WHERE sid=$1),
            total_calls         = (SELECT COUNT(*)                        FROM llm_calls WHERE sid=$1)
        WHERE sid = $1
        RETURNING sid, total_input_tokens, total_output_tokens, total_cost_usd, total_calls
        """,
        sid,
        datetime.now(timezone.utc),
    )
    # Refresh materialized view (best-effort)
    try:
        await pool.execute(
            "REFRESH MATERIALIZED VIEW CONCURRENTLY llm_cost_by_model"
        )
    except Exception:
        pass
    return dict(row) if row else {}


async def cost_report(sid: str) -> dict[str, Any]:
    """Return per-model cost breakdown for a session."""
    pool = await get_pool()
    rows = await pool.fetch(
        """
        SELECT
            model,
            COUNT(*)           AS calls,
            SUM(input_tokens)  AS input_tokens,
            SUM(output_tokens) AS output_tokens,
            SUM(cost_usd)      AS cost_usd
        FROM llm_calls
        WHERE sid = $1
        GROUP BY model
        ORDER BY cost_usd DESC
        """,
        sid,
    )
    session = await pool.fetchrow(
        "SELECT * FROM llm_sessions WHERE sid=$1", sid
    )
    return {
        "sid": sid,
        "session": dict(session) if session else {},
        "by_model": [dict(r) for r in rows],
    }


def run_sync(coro) -> Any:
    """Run an async coroutine synchronously (for CLI use)."""
    return asyncio.run(coro)

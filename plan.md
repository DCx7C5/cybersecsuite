# LLM Orchestration Layer — Anthropic + PostgreSQL + OpenObserve

> **Sprint blueprint** — Session-aware, streaming, fully observable LLM layer
> bolted on top of the existing Git worktree session manager.

---

## 1. Project Overview

CyberSecSuite already ships a multi-provider AI proxy (`src/ai_proxy/`), an in-memory usage tracker, an OpenObserve async bulk-writer, and a Tortoise ORM `ApiUsageLog` model — but these components are **not bound to Git worktree sessions** and have **no OTEL tracing**. This sprint adds a production-grade `src/llm/` package that ties every Anthropic API call, its token usage, and cost to the running worktree session ID (`<sid>`). All calls are persisted in two new Postgres tables (`llm_sessions`, `llm_calls`), emitted as OTEL spans to OpenObserve, and streamed via `AsyncAnthropic` with structured outputs. The `worktree-session-manager.py` CLI gains two new sub-commands (`llm-session-open` / `llm-session-close`) that create/close a DB session row on worktree create/teardown respectively. The result is full per-agent observability: every token, every cost, every trace, isolated by `worktree-<sid>`.

---

## 2. Exploration Validation Summary

### Command outputs (executed 2026-04-20)

**`pwd && ls -la .`**
```
/home/daen/Projects/cybersecsuite
worktree-session-manager.py  (22884 bytes, executable -rwx------)
plan.md, pyproject.toml, scripts/, src/, tests/, .git/
```

**`ls -la worktree-session-manager.py`**
```
-rwx------ 1 daen daen 22884 20. Apr 18:54 worktree-session-manager.py  ✅ exists
```

**`cat worktree-session-manager.py | head -n 80`**
```
SID_PATTERN = re.compile(r"^[0-9a-f]{12}$")
MARKER_FILE = ".worktree-session"
DEFAULT_HOOKS_TEMPLATE_DIR = Path(__file__).parent / "scripts" / "hooks"
generate_sid(), validate_sid(), get_repo_root(), get_worktree_root() all present
create_worktree() accepts sid, branch, repo_root, hooks_template_dir, new_branch
```

**`git config --get extensions.worktreeConfig`**
```
true  ✅ already enabled
```

**`find . -name ".worktree-session" -o -name "hooks"`**
```
./.claude/hooks  ./src/hooks  ./scripts/hooks  ./templates/hooks  ./src/agent_ts/hooks
No active .worktree-session markers → no live worktrees at audit time
```

**`.git layout`**
```
.git/config  .git/hooks/  .git/objects/  .git/refs/
No .git/worktrees/ directory → no linked worktrees currently active
```

**`grep -r "sid" . --include="*.py" --include="*.sh"`**
```
worktree-session-manager.py: generate_sid, validate_sid, worktree_exists(sid), get_worktree_root(sid)
scripts/gwt-aliases.sh: GWT_SID, --sid flag, export
src/dashboard/api/workflows.py: sid used as step-id variable (unrelated)
src/db/models/api_usage_log.py: session_id = fields.CharField(max_length=64, null=True)  ← hook point
```

### Validation conclusions

- ✅ `worktree-<sid>` structure confirmed: 12-char hex, `extensions.worktreeConfig=true`, `scripts/hooks/*.tpl` in place.
- ✅ Integration points identified:
  1. `worktree-session-manager.py` → add `cmd_llm_session_open` / `cmd_llm_session_close`
  2. `src/db/models/` → new `llm_sessions.py`, `llm_calls.py` Tortoise models (raw asyncpg DDL also provided for standalone use)
  3. `src/openobserve/writer.py` → already has `bulk_index` — wire LLM telemetry into it
  4. `src/ai_proxy/services/usage_tracker.py` → already tracks per-provider tokens; extend to accept `worktree_sid`
  5. New `src/llm/` package → `AsyncLLMClient`, `LLMOrchestrator`, OTEL instrumentation

---

## 3. Detailed Requirements

### Functional

- **Session binding** — every LLM call must carry the active `worktree_sid`; calls made outside a managed worktree use `sid="global"`.
- **Async streaming** — use `AsyncAnthropic` with `stream=True`; yield tokens to callers in real-time.
- **Structured outputs** — support `response_format` / tool-use for JSON-schema-constrained replies.
- **DB persistence** — persist `llm_sessions` (one row per worktree lifecycle) and `llm_calls` (one row per API call) via asyncpg.
- **Token accounting** — store `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens`, and `cost_usd` (computed from published Anthropic pricing).
- **OTEL tracing** — wrap every `AsyncAnthropic` call in an OpenTelemetry span; export to OpenObserve OTLP endpoint.
- **OpenObserve logging** — fire-and-forget `bulk_index("llm-calls", [...])` via existing writer; do NOT log full prompt/response bodies by default.
- **CLI hooks** — `worktree-session-manager.py llm-session-open <sid>` and `llm-session-close <sid>` to create/close DB rows alongside worktree lifecycle.
- **Cost report** — `worktree-session-manager.py llm-cost <sid>` queries Postgres and prints token/cost summary.

### Non-functional

- **Isolation** — each worktree gets a separate `llm_sessions` row; no cross-session data leakage.
- **Token efficiency** — NEVER store raw prompt text in Postgres by default; store only metadata + token counts; use `log_prompts=False` flag.
- **Observability** — p50/p95/p99 latency per model; error rate per provider; all via OTEL + OpenObserve.
- **Async-safe** — all DB writes are fire-and-forget `asyncio.create_task`; never block the streaming response path.
- **Idempotency** — `llm-session-open` is idempotent; re-opening an existing sid is a no-op.
- **Graceful degradation** — if Postgres is unreachable, log to OpenObserve only and continue; never crash the LLM call.
- **Python 3.14** — all new code targets Python ≥ 3.14; use `asyncio.TaskGroup` where appropriate.

---

## 4. Architecture & Best Practices

### Design rationale

Per-worktree isolation is achieved by threading `worktree_sid` through the entire call stack rather than using a global context variable. This avoids the asyncio `ContextVar` footgun where a `create_task` call can accidentally inherit the wrong context.

The `LLMOrchestrator` wraps `AsyncAnthropic`, automatically:
1. Resolves the current `worktree_sid` (from `GWT_SID` env var or `.worktree-session` file)
2. Opens an OTEL span with `worktree.sid` attribute
3. Calls the Anthropic API (streaming or non-streaming)
4. On completion: schedules a background asyncio task to persist the call to Postgres
5. Fires `bulk_index("llm-calls", [...])` for OpenObserve

### Flow diagram

```mermaid
flowchart TD
    A[gwt-create main] -->|python wsm.py create| B[worktree-&lt;sid&gt; created]
    B -->|python wsm.py llm-session-open SID| C[(llm_sessions INSERT)]
    C --> D[Developer / agent calls LLMOrchestrator.chat]
    D --> E{resolve_sid}
    E -->|GWT_SID env / .worktree-session| F[sid = abc123def456]
    F --> G[OTEL span START\nworktree.sid=abc123...]
    G --> H[AsyncAnthropic.messages.stream]
    H -->|chunk| I[yield token to caller]
    H -->|on_message_done| J[usage = input+output tokens]
    J --> K[compute cost_usd]
    K --> L[asyncio.create_task persist_call_bg]
    K --> M[bulk_index llm-calls to OpenObserve]
    G --> N[OTEL span END\nlatency_ms, tokens, model]
    L --> O[(llm_calls INSERT)]
    P[gwt-teardown SID] -->|python wsm.py llm-session-close SID| Q[(llm_sessions UPDATE closed_at)]
```

### Integration into worktree-session-manager.py

The manager already imports only stdlib modules. The LLM commands are **optional**: they import `src/llm/` lazily only if `asyncpg` and `anthropic` are available; otherwise they print a helpful error. This keeps the manager script usable even without the full Python environment.

```python
# In worktree-session-manager.py — new optional import guard
def _require_llm():
    try:
        from llm.db import open_session, close_session, cost_report
        return open_session, close_session, cost_report
    except ImportError as e:
        raise SystemExit(f"[WSM] LLM layer not installed: {e}. Run: uv sync") from e
```

---

## 5. Repository File Structure (Updated)

```
cybersecsuite/
├── worktree-session-manager.py        ← UPDATED: +llm-session-open/close/cost commands
├── plan.md                            ← this file
├── scripts/
│   ├── gwt-aliases.sh
│   └── hooks/
│       ├── pre-commit.tpl
│       ├── pre-push.tpl
│       └── ...
├── src/
│   ├── llm/                           ← NEW PACKAGE
│   │   ├── __init__.py                ← exports LLMOrchestrator, AsyncLLMClient
│   │   ├── client.py                  ← AsyncLLMClient wrapper around AsyncAnthropic
│   │   ├── orchestrator.py            ← LLMOrchestrator: session-aware, traced
│   │   ├── pricing.py                 ← Anthropic token pricing table + cost_usd()
│   │   ├── otel.py                    ← OTEL tracer/meter setup, span helpers
│   │   ├── db.py                      ← asyncpg helpers: open_session, persist_call, close_session
│   │   └── schema.sql                 ← DDL for llm_sessions + llm_calls
│   ├── db/
│   │   └── models/
│   │       ├── llm_session.py         ← NEW Tortoise model
│   │       └── llm_call.py            ← NEW Tortoise model
│   ├── openobserve/                   ← UNCHANGED (writer.py used as-is)
│   └── ai_proxy/
│       └── services/
│           └── usage_tracker.py       ← MINOR UPDATE: accept worktree_sid kwarg
├── tests/
│   ├── test_worktree_manager.py       ← existing 42 tests
│   └── test_llm_orchestrator.py       ← NEW: 30+ tests for LLM layer
└── pyproject.toml                     ← MINOR: add opentelemetry deps
```

---

## 6. Detailed Implementation Plan

### Phase 0 — Prerequisites & dependency audit

1. Confirm `anthropic>=0.84.0` is in `pyproject.toml` ✅ (already present)
2. Confirm `asyncpg>=0.30` is in `pyproject.toml` ✅ (already present)
3. Add OpenTelemetry packages to `pyproject.toml`:
   ```
   opentelemetry-sdk>=1.28
   opentelemetry-exporter-otlp-proto-http>=1.28
   opentelemetry-instrumentation-httpx>=0.49
   ```
4. Run `uv sync`
5. Verify `OPENOBSERVE_OTLP_ENDPOINT` is set in `.env.example`

**Effort:** 30 min

### Phase 1 — Database schema

1. Write `src/llm/schema.sql` with `llm_sessions` and `llm_calls` tables
2. Write Tortoise models `src/db/models/llm_session.py` and `src/db/models/llm_call.py`
3. Write `src/llm/db.py` with raw asyncpg helpers (for use outside the Tortoise ORM context)
4. Register new models in `src/db/models/__init__.py`
5. Apply migration: `psql cybersec_forensics < src/llm/schema.sql`
6. Write tests: `tests/test_llm_db.py` (insert + query via asyncpg)

**Effort:** 2 hours

### Phase 2 — Pricing table

1. Write `src/llm/pricing.py` with published Anthropic pricing for claude-3-5-sonnet, claude-3-haiku, claude-opus-4 etc.
2. `cost_usd(model, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens) -> Decimal`
3. Prices sourced from `https://anthropic.com/pricing` — include a `PRICING_LAST_UPDATED` constant
4. Write unit tests

**Effort:** 1 hour

### Phase 3 — OTEL setup

1. Write `src/llm/otel.py`:
   - `get_tracer()` returns a module-level `opentelemetry.trace.Tracer`
   - `get_meter()` returns a module-level `opentelemetry.metrics.Meter`
   - `setup_otel(endpoint, service_name)` configures OTLP HTTP exporter pointing to OpenObserve
   - Instruments httpx via `HTTPXClientInstrumentor`
2. Wire `setup_otel()` into the ASGI lifespan startup in `src/proxy/asgi.py`
3. Write integration test asserting span is exported (mock OTLP endpoint)

**Effort:** 2 hours

### Phase 4 — AsyncLLMClient

1. Write `src/llm/client.py`:
   - `AsyncLLMClient(model, sid, log_prompts=False)` wraps `AsyncAnthropic`
   - `async def chat(messages, *, stream=True, tools=None, response_format=None) -> AsyncIterator[str] | Message`
   - Streaming path: uses `async with client.messages.stream(...)` context manager
   - Non-streaming path: uses `await client.messages.create(...)`
   - Emits OTEL span for every call
   - On completion fires background task to `db.persist_call()`
2. Honour `ANTHROPIC_BASE_URL` env var (routes through local AI proxy if set)
3. Write mock-based unit tests (no live API calls in CI)

**Effort:** 3 hours

### Phase 5 — LLMOrchestrator

1. Write `src/llm/orchestrator.py`:
   - `LLMOrchestrator(default_model, db_pool, sid=None)` — sid auto-detected if `None`
   - `sid` resolution order: constructor arg → `GWT_SID` env var → `.worktree-session` file walk → `"global"`
   - `async def chat(messages, **kwargs)` — delegates to `AsyncLLMClient`, attaches sid
   - `async def structured(messages, schema: type[BaseModel], **kwargs) -> BaseModel` — uses tool_use for structured output
   - `async def summarize(text, max_tokens=256) -> str` — single-turn summarisation helper
2. Expose singleton `get_orchestrator()` with lazy init

**Effort:** 3 hours

### Phase 6 — worktree-session-manager.py integration

1. Add three new subcommands:
   - `llm-session-open <sid>` — creates `llm_sessions` row; idempotent
   - `llm-session-close <sid>` — sets `closed_at`, computes total cost
   - `llm-cost <sid>` — prints token/cost report from Postgres
2. Integrate `llm-session-open` call into `create_worktree()` (optional, behind `--with-llm` flag)
3. Integrate `llm-session-close` call into `teardown_worktree()` (same flag)
4. Update `scripts/gwt-aliases.sh` with `gwt-llm-cost <sid>` alias

**Effort:** 2 hours

### Phase 7 — OpenObserve wiring

1. In `AsyncLLMClient`, after each call fire `bulk_index("llm-calls", [{...}])` with:
   - `worktree_sid`, `model`, `input_tokens`, `output_tokens`, `cost_usd`, `latency_ms`, `stream`, `success`
   - **Never** include prompt text
2. In `LLMOrchestrator`, fire `bulk_index("llm-sessions", [{...}])` on session open/close
3. Verify events appear in OpenObserve dashboard

**Effort:** 1 hour

### Phase 8 — Tests

1. Write `tests/test_llm_orchestrator.py`:
   - Unit tests with `AsyncAnthropic` mocked via `respx` or `unittest.mock`
   - DB tests with a real Postgres test database (skip if unavailable)
   - OTEL span tests with an in-memory exporter
   - SID resolution tests
2. Target ≥ 80% coverage on `src/llm/`

**Effort:** 3 hours

### Phase 9 — Playwright stealth browser + dashboard test

1. Ensure playwright-stealth MCP server is running
2. Navigate to `http://localhost:8000` and run a full dashboard audit via screenshots
3. Verify all 7 critical tabs load (telemetry, agent-factory, agent-crafter, team-builder, workflows, opensearch, explorer)
4. Fix any new failures found

**Effort:** 1 hour

---

## 7. Code Files to Create / Update

### `src/llm/__init__.py`

```python
"""LLM orchestration layer — session-aware, OTEL-traced, cost-tracked."""
from llm.orchestrator import LLMOrchestrator, get_orchestrator
from llm.client import AsyncLLMClient
from llm.pricing import cost_usd

__all__ = ["LLMOrchestrator", "AsyncLLMClient", "cost_usd", "get_orchestrator"]
```

### `src/llm/pricing.py`

```python
"""Anthropic token pricing — updated 2026-04."""
from decimal import Decimal

PRICING_LAST_UPDATED = "2026-04-01"

# (input_per_mtok, output_per_mtok, cache_write_per_mtok, cache_read_per_mtok)
_PRICES: dict[str, tuple[Decimal, Decimal, Decimal, Decimal]] = {
    "claude-opus-4-5":        (Decimal("15.00"), Decimal("75.00"), Decimal("18.75"), Decimal("1.50")),
    "claude-sonnet-4-5":      (Decimal("3.00"),  Decimal("15.00"), Decimal("3.75"),  Decimal("0.30")),
    "claude-haiku-4-5":       (Decimal("0.80"),  Decimal("4.00"),  Decimal("1.00"),  Decimal("0.08")),
    "claude-3-5-sonnet-20241022": (Decimal("3.00"), Decimal("15.00"), Decimal("3.75"), Decimal("0.30")),
    "claude-3-haiku-20240307":    (Decimal("0.25"), Decimal("1.25"), Decimal("0.30"), Decimal("0.03")),
}
_DEFAULT_PRICE = (Decimal("3.00"), Decimal("15.00"), Decimal("3.75"), Decimal("0.30"))

def cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_write_tokens: int = 0,
    cache_read_tokens: int = 0,
) -> Decimal:
    inp, out, cw, cr = _PRICES.get(model, _DEFAULT_PRICE)
    mtok = Decimal("1_000_000")
    return (
        inp  * Decimal(input_tokens)       / mtok
        + out * Decimal(output_tokens)     / mtok
        + cw  * Decimal(cache_write_tokens)/ mtok
        + cr  * Decimal(cache_read_tokens) / mtok
    )
```

### `src/llm/otel.py`

```python
"""OpenTelemetry setup for the LLM layer."""
from __future__ import annotations
import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

_tracer: trace.Tracer | None = None
_meter: metrics.Meter | None = None

def setup_otel(
    endpoint: str | None = None,
    service_name: str = "cybersecsuite-llm",
) -> None:
    global _tracer, _meter
    ep = endpoint or os.environ.get(
        "OPENOBSERVE_OTLP_ENDPOINT", "http://localhost:5080/api/default"
    )
    headers = {
        "Authorization": "Basic " + _basic_auth(),
    }
    tp = TracerProvider()
    tp.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{ep}/v1/traces", headers=headers)))
    trace.set_tracer_provider(tp)

    mr = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=f"{ep}/v1/metrics", headers=headers))
    mp = MeterProvider(metric_readers=[mr])
    metrics.set_meter_provider(mp)

    HTTPXClientInstrumentor().instrument()
    _tracer = trace.get_tracer(service_name)
    _meter  = metrics.get_meter(service_name)

def get_tracer() -> trace.Tracer:
    return _tracer or trace.get_tracer("cybersecsuite-llm")

def get_meter() -> metrics.Meter:
    return _meter or metrics.get_meter("cybersecsuite-llm")

def _basic_auth() -> str:
    import base64, os
    u = os.environ.get("OPENOBSERVE_EMAIL", "admin@cybersec.local")
    p = os.environ.get("OPENOBSERVE_PASSWORD", "cYb3rS3c!")
    return base64.b64encode(f"{u}:{p}".encode()).decode()
```

### `src/llm/db.py`

```python
"""asyncpg helpers for llm_sessions and llm_calls — no Tortoise ORM dependency."""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import asyncpg

log = logging.getLogger("llm.db")

_pool: asyncpg.Pool | None = None

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        dsn = os.environ.get(
            "CYBERSEC_DB_DSN",
            "postgresql://{user}:{pw}@{host}:{port}/{db}".format(
                user=os.environ.get("CYBERSEC_DB_USER", "cybersec"),
                pw=os.environ.get("CYBERSEC_DB_PASSWORD", ""),
                host=os.environ.get("CYBERSEC_DB_HOST", "localhost"),
                port=os.environ.get("CYBERSEC_DB_PORT", "5432"),
                db=os.environ.get("CYBERSEC_DB_NAME", "cybersec_forensics"),
            ),
        )
        _pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)
    return _pool

async def open_session(sid: str, repo_root: str, branch: str) -> None:
    """Create an llm_sessions row for this worktree. Idempotent."""
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO llm_sessions (sid, repo_root, branch, opened_at)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (sid) DO NOTHING
        """,
        sid, repo_root, branch, datetime.now(timezone.utc),
    )
    log.info("llm_session opened for sid=%s", sid)

async def persist_call(
    sid: str, model: str,
    input_tokens: int, output_tokens: int,
    cache_read_tokens: int, cache_write_tokens: int,
    cost_usd: Decimal, latency_ms: float,
    stream: bool, success: bool, error: str | None,
    request_id: str | None,
) -> None:
    """Insert one llm_calls row. Fire-and-forget safe."""
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO llm_calls
          (sid, model, input_tokens, output_tokens,
           cache_read_tokens, cache_write_tokens,
           cost_usd, latency_ms, stream, success, error, request_id, called_at)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
        """,
        sid, model, input_tokens, output_tokens,
        cache_read_tokens, cache_write_tokens,
        cost_usd, latency_ms, stream, success, error, request_id,
        datetime.now(timezone.utc),
    )

async def close_session(sid: str) -> dict[str, Any]:
    """Set closed_at and compute aggregated totals. Returns summary dict."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        UPDATE llm_sessions SET
            closed_at = $2,
            total_input_tokens  = (SELECT COALESCE(SUM(input_tokens),0)  FROM llm_calls WHERE sid=$1),
            total_output_tokens = (SELECT COALESCE(SUM(output_tokens),0) FROM llm_calls WHERE sid=$1),
            total_cost_usd      = (SELECT COALESCE(SUM(cost_usd),0)      FROM llm_calls WHERE sid=$1),
            total_calls         = (SELECT COUNT(*)                        FROM llm_calls WHERE sid=$1)
        WHERE sid = $1
        RETURNING sid, total_input_tokens, total_output_tokens, total_cost_usd, total_calls
        """,
        sid, datetime.now(timezone.utc),
    )
    return dict(row) if row else {}

async def cost_report(sid: str) -> dict[str, Any]:
    """Return cost summary for a session."""
    pool = await get_pool()
    rows = await pool.fetch(
        """
        SELECT model,
               COUNT(*) AS calls,
               SUM(input_tokens) AS input_tokens,
               SUM(output_tokens) AS output_tokens,
               SUM(cost_usd) AS cost_usd
        FROM llm_calls WHERE sid=$1
        GROUP BY model ORDER BY cost_usd DESC
        """, sid,
    )
    return {"sid": sid, "by_model": [dict(r) for r in rows]}
```

### `src/llm/client.py`

```python
"""AsyncLLMClient — session-aware AsyncAnthropic wrapper with OTEL tracing."""
from __future__ import annotations
import asyncio
import logging
import os
import time
from collections.abc import AsyncIterator
from decimal import Decimal
from typing import Any

import anthropic
from anthropic import AsyncAnthropic, AsyncStream
from anthropic.types import Message, MessageStreamEvent

from llm.otel import get_tracer
from llm.pricing import cost_usd as _cost_usd

log = logging.getLogger("llm.client")

class AsyncLLMClient:
    """Thin session-aware wrapper around AsyncAnthropic."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-5",
        sid: str = "global",
        log_prompts: bool = False,
        db_persist_fn: Any = None,
        oo_index_fn: Any = None,
    ) -> None:
        self.model = model
        self.sid = sid
        self.log_prompts = log_prompts
        self._persist = db_persist_fn   # async callable or None
        self._oo_index = oo_index_fn    # async callable or None
        base_url = os.environ.get("ANTHROPIC_BASE_URL")
        self._client = AsyncAnthropic(base_url=base_url) if base_url else AsyncAnthropic()

    async def chat(
        self,
        messages: list[dict],
        *,
        max_tokens: int = 4096,
        stream: bool = True,
        tools: list[dict] | None = None,
        system: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str] | Message:
        if stream:
            return self._stream(messages, max_tokens=max_tokens, tools=tools, system=system, **kwargs)
        return await self._complete(messages, max_tokens=max_tokens, tools=tools, system=system, **kwargs)

    async def _stream(self, messages, **kwargs) -> AsyncIterator[str]:
        tracer = get_tracer()
        t0 = time.perf_counter()
        with tracer.start_as_current_span("llm.stream") as span:
            span.set_attribute("worktree.sid", self.sid)
            span.set_attribute("llm.model", self.model)
            input_tokens = output_tokens = cache_read = cache_write = 0
            error: str | None = None
            try:
                async with self._client.messages.stream(
                    model=self.model, messages=messages, **kwargs
                ) as stream:
                    async for text in stream.text_stream:
                        yield text
                    final = await stream.get_final_message()
                    u = final.usage
                    input_tokens  = u.input_tokens
                    output_tokens = u.output_tokens
                    cache_read    = getattr(u, "cache_read_input_tokens", 0) or 0
                    cache_write   = getattr(u, "cache_creation_input_tokens", 0) or 0
            except Exception as exc:
                error = str(exc)
                span.record_exception(exc)
                raise
            finally:
                latency = (time.perf_counter() - t0) * 1000
                cost = _cost_usd(self.model, input_tokens, output_tokens, cache_write, cache_read)
                span.set_attribute("llm.input_tokens",  input_tokens)
                span.set_attribute("llm.output_tokens", output_tokens)
                span.set_attribute("llm.cost_usd",      float(cost))
                span.set_attribute("llm.latency_ms",    latency)
                asyncio.create_task(self._bg_persist(
                    input_tokens, output_tokens, cache_read, cache_write,
                    cost, latency, stream=True, error=error,
                ))

    async def _complete(self, messages, **kwargs) -> Message:
        tracer = get_tracer()
        t0 = time.perf_counter()
        with tracer.start_as_current_span("llm.complete") as span:
            span.set_attribute("worktree.sid", self.sid)
            span.set_attribute("llm.model", self.model)
            try:
                msg = await self._client.messages.create(
                    model=self.model, messages=messages, **kwargs
                )
                u = msg.usage
                cost = _cost_usd(
                    self.model, u.input_tokens, u.output_tokens,
                    getattr(u, "cache_creation_input_tokens", 0) or 0,
                    getattr(u, "cache_read_input_tokens", 0) or 0,
                )
                latency = (time.perf_counter() - t0) * 1000
                asyncio.create_task(self._bg_persist(
                    u.input_tokens, u.output_tokens,
                    getattr(u, "cache_read_input_tokens", 0) or 0,
                    getattr(u, "cache_creation_input_tokens", 0) or 0,
                    cost, latency, stream=False, error=None,
                ))
                return msg
            except Exception as exc:
                span.record_exception(exc)
                raise

    async def _bg_persist(
        self,
        input_tokens: int, output_tokens: int,
        cache_read: int, cache_write: int,
        cost: Decimal, latency_ms: float,
        stream: bool, error: str | None,
    ) -> None:
        try:
            if self._persist:
                await self._persist(
                    sid=self.sid, model=self.model,
                    input_tokens=input_tokens, output_tokens=output_tokens,
                    cache_read_tokens=cache_read, cache_write_tokens=cache_write,
                    cost_usd=cost, latency_ms=latency_ms,
                    stream=stream, success=error is None, error=error, request_id=None,
                )
            if self._oo_index:
                await self._oo_index("llm-calls", [{
                    "worktree_sid": self.sid, "model": self.model,
                    "input_tokens": input_tokens, "output_tokens": output_tokens,
                    "cost_usd": float(cost), "latency_ms": latency_ms,
                    "stream": stream, "success": error is None,
                }])
        except Exception:
            log.exception("Background persist failed (non-fatal)")
```

### `src/llm/orchestrator.py`

```python
"""LLMOrchestrator — session-aware high-level API."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from llm.client import AsyncLLMClient
from llm.db import persist_call, get_pool

_instance: LLMOrchestrator | None = None

def resolve_sid(sid: str | None = None) -> str:
    if sid:
        return sid
    env = os.environ.get("GWT_SID") or os.environ.get("CYBERSEC_SESSION_ID")
    if env:
        return env
    # Walk up looking for .worktree-session
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        marker = parent / ".worktree-session"
        if marker.exists():
            return marker.read_text().strip()
    return "global"


class LLMOrchestrator:
    def __init__(
        self,
        default_model: str = "claude-sonnet-4-5",
        sid: str | None = None,
        log_prompts: bool = False,
    ) -> None:
        self.sid = resolve_sid(sid)
        self._model = default_model
        self._log_prompts = log_prompts

    def _client(self, model: str | None = None) -> AsyncLLMClient:
        from openobserve.writer import bulk_index
        return AsyncLLMClient(
            model=model or self._model,
            sid=self.sid,
            log_prompts=self._log_prompts,
            db_persist_fn=persist_call,
            oo_index_fn=bulk_index,
        )

    async def chat(self, messages: list[dict], model: str | None = None, **kwargs: Any):
        return await self._client(model).chat(messages, **kwargs)

    async def structured(
        self,
        messages: list[dict],
        schema: type[BaseModel],
        model: str | None = None,
        **kwargs: Any,
    ) -> BaseModel:
        import json
        tool = {
            "name": "structured_output",
            "description": "Return a structured JSON response matching the schema",
            "input_schema": schema.model_json_schema(),
        }
        msg = await self._client(model).chat(
            messages, stream=False, tools=[tool],
            tool_choice={"type": "tool", "name": "structured_output"}, **kwargs,
        )
        for block in msg.content:
            if block.type == "tool_use" and block.name == "structured_output":
                return schema.model_validate(block.input)
        raise ValueError("No structured output block in response")

    async def summarize(self, text: str, max_tokens: int = 256, model: str | None = None) -> str:
        messages = [{"role": "user", "content": f"Summarize concisely:\n\n{text}"}]
        parts = []
        async for chunk in await self._client(model).chat(messages, max_tokens=max_tokens):
            parts.append(chunk)
        return "".join(parts)


def get_orchestrator(**kwargs: Any) -> LLMOrchestrator:
    global _instance
    if _instance is None:
        _instance = LLMOrchestrator(**kwargs)
    return _instance
```

### `src/db/models/llm_session.py`

```python
from tortoise import fields
from tortoise.models import Model

class LlmSession(Model):
    """One row per worktree session lifecycle."""
    sid          = fields.CharField(max_length=12, pk=True)
    repo_root    = fields.CharField(max_length=512, default="")
    branch       = fields.CharField(max_length=256, default="")
    opened_at    = fields.DatetimeField()
    closed_at    = fields.DatetimeField(null=True)
    total_input_tokens  = fields.BigIntField(default=0)
    total_output_tokens = fields.BigIntField(default=0)
    total_cost_usd      = fields.DecimalField(max_digits=14, decimal_places=8, default=0)
    total_calls         = fields.IntField(default=0)
    class Meta:
        table = "llm_sessions"
```

### `src/db/models/llm_call.py`

```python
from tortoise import fields
from tortoise.models import Model

class LlmCall(Model):
    """One row per Anthropic API call, bound to a worktree session."""
    id                  = fields.BigIntField(pk=True, generated=True)
    sid                 = fields.CharField(max_length=12, db_index=True)
    model               = fields.CharField(max_length=128)
    input_tokens        = fields.IntField(default=0)
    output_tokens       = fields.IntField(default=0)
    cache_read_tokens   = fields.IntField(default=0)
    cache_write_tokens  = fields.IntField(default=0)
    cost_usd            = fields.DecimalField(max_digits=14, decimal_places=8, default=0)
    latency_ms          = fields.FloatField(default=0)
    stream              = fields.BooleanField(default=True)
    success             = fields.BooleanField(default=True)
    error               = fields.TextField(null=True)
    request_id          = fields.CharField(max_length=64, null=True)
    called_at           = fields.DatetimeField(auto_now_add=True)
    class Meta:
        table = "llm_calls"
        indexes = [("sid", "called_at"), ("model", "called_at")]
```

---

## 8. Database Schema & OpenObserve Configuration

### `src/llm/schema.sql`

```sql
-- LLM Sessions — one per worktree lifecycle
CREATE TABLE IF NOT EXISTS llm_sessions (
    sid                  CHAR(12)         PRIMARY KEY,
    repo_root            TEXT             NOT NULL DEFAULT '',
    branch               TEXT             NOT NULL DEFAULT '',
    opened_at            TIMESTAMPTZ      NOT NULL,
    closed_at            TIMESTAMPTZ,
    total_input_tokens   BIGINT           NOT NULL DEFAULT 0,
    total_output_tokens  BIGINT           NOT NULL DEFAULT 0,
    total_cost_usd       NUMERIC(14, 8)   NOT NULL DEFAULT 0,
    total_calls          INTEGER          NOT NULL DEFAULT 0
);

-- LLM Calls — one per Anthropic API request
CREATE TABLE IF NOT EXISTS llm_calls (
    id                   BIGSERIAL        PRIMARY KEY,
    sid                  CHAR(12)         NOT NULL REFERENCES llm_sessions(sid) ON DELETE CASCADE,
    model                VARCHAR(128)     NOT NULL,
    input_tokens         INTEGER          NOT NULL DEFAULT 0,
    output_tokens        INTEGER          NOT NULL DEFAULT 0,
    cache_read_tokens    INTEGER          NOT NULL DEFAULT 0,
    cache_write_tokens   INTEGER          NOT NULL DEFAULT 0,
    cost_usd             NUMERIC(14, 8)   NOT NULL DEFAULT 0,
    latency_ms           DOUBLE PRECISION NOT NULL DEFAULT 0,
    stream               BOOLEAN          NOT NULL DEFAULT TRUE,
    success              BOOLEAN          NOT NULL DEFAULT TRUE,
    error                TEXT,
    request_id           VARCHAR(64),
    called_at            TIMESTAMPTZ      NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS llm_calls_sid_called_at    ON llm_calls (sid, called_at DESC);
CREATE INDEX IF NOT EXISTS llm_calls_model_called_at  ON llm_calls (model, called_at DESC);
CREATE INDEX IF NOT EXISTS llm_sessions_opened_at     ON llm_sessions (opened_at DESC);

-- Materialized view for fast per-model cost aggregation
CREATE MATERIALIZED VIEW IF NOT EXISTS llm_cost_by_model AS
SELECT
    sid,
    model,
    COUNT(*) AS calls,
    SUM(input_tokens)  AS total_input,
    SUM(output_tokens) AS total_output,
    SUM(cost_usd)      AS total_cost
FROM llm_calls
GROUP BY sid, model;

CREATE UNIQUE INDEX IF NOT EXISTS llm_cost_by_model_idx ON llm_cost_by_model (sid, model);
```

### OpenObserve OTEL environment variables

Add to `.env` (and `.env.example`):

```env
# OpenObserve OTLP endpoint (HTTP)
OPENOBSERVE_OTLP_ENDPOINT=http://localhost:5080/api/default

# OpenObserve credentials (used for Basic Auth in OTLP headers)
OPENOBSERVE_EMAIL=admin@cybersec.local
OPENOBSERVE_PASSWORD=cYb3rS3c!

# Optional: override OTEL service name
OTEL_SERVICE_NAME=cybersecsuite-llm

# Route LLM calls through local AI proxy (optional)
ANTHROPIC_BASE_URL=http://localhost:8000/v1
```

### OTEL instrumentation streams in OpenObserve

| Stream name pattern | Contents |
|---|---|
| `cybersecsuite-llm-calls-YYYY.MM.DD` | Per-call token/cost/latency events |
| `cybersecsuite-llm-sessions-YYYY.MM.DD` | Session open/close events |
| OTLP traces → `default._traces` | Full OTEL spans with worktree.sid attribute |
| OTLP metrics → `default._metrics` | p50/p95/p99 latency, token counters |

---

## 9. Risk Register & Mitigations

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Postgres unreachable at call time | Medium | Medium | Try/except in `_bg_persist`; fall back to OO-only; never crash stream | Dev |
| OTEL exporter network failure | Medium | Low | `BatchSpanProcessor` with retry; errors suppressed | Dev |
| Prompt text accidentally logged | Low | High | `log_prompts=False` default; grep CI check for "content" in OO payloads | Dev |
| Anthropic API key exposed in logs | Low | Critical | Mask `Authorization` header in OTEL instrumentation; add `REDACT_HEADERS` list | Dev |
| asyncpg pool exhaustion under load | Low | Medium | `max_size=5` pool; circuit breaker; queue background writes | Dev |
| SID collision (1/2^48) | Very Low | Low | `worktree_exists()` guard already in place; DB `PRIMARY KEY` constraint | Dev |
| `GWT_SID` env var not set | Medium | Low | Falls back to `.worktree-session` file walk then `"global"` | Dev |
| Pricing table staleness | Medium | Low | `PRICING_LAST_UPDATED` constant; quarterly review reminder in TODO | Dev |
| Materialized view staleness | Low | Low | `REFRESH MATERIALIZED VIEW CONCURRENTLY llm_cost_by_model` in teardown | Dev |
| Python 3.14 asyncio breaking changes | Low | Medium | Pin to `asyncio.TaskGroup`; avoid deprecated `ensure_future` | Dev |

---

## 10. Setup & Usage Instructions

### Initial setup (run once)

```bash
# 1. Add OpenTelemetry deps
cd /home/daen/Projects/cybersecsuite
uv add opentelemetry-sdk opentelemetry-exporter-otlp-proto-http opentelemetry-instrumentation-httpx

# 2. Apply DB schema
psql $CYBERSEC_DB_DSN -f src/llm/schema.sql

# 3. Copy env vars to your .env
cat >> .env <<'EOF'
OPENOBSERVE_OTLP_ENDPOINT=http://localhost:5080/api/default
OPENOBSERVE_EMAIL=admin@cybersec.local
OPENOBSERVE_PASSWORD=cYb3rS3c!
OTEL_SERVICE_NAME=cybersecsuite-llm
EOF
```

### Creating a session-bound LLM worktree

```bash
# Create worktree with LLM session
SID=$(python3 worktree-session-manager.py create --branch main)
python3 worktree-session-manager.py llm-session-open $SID

# Or combined (if --with-llm flag implemented)
SID=$(python3 worktree-session-manager.py create --branch main --with-llm)

# Jump into the worktree
cd ../worktree-$SID
export GWT_SID=$SID  # auto-detected if .worktree-session exists
```

### Using the LLM layer in Python

```python
import asyncio
from llm import get_orchestrator

async def main():
    orc = get_orchestrator()  # picks up GWT_SID automatically
    print(f"Session: {orc.sid}")

    # Streaming chat
    async for chunk in await orc.chat([
        {"role": "user", "content": "Analyse this CVE: CVE-2024-12345"}
    ]):
        print(chunk, end="", flush=True)

    # Structured output
    from pydantic import BaseModel
    class ThreatAnalysis(BaseModel):
        severity: str
        affected_systems: list[str]
        recommended_actions: list[str]

    result = await orc.structured(
        [{"role": "user", "content": "Analyse CVE-2024-12345"}],
        ThreatAnalysis,
    )
    print(result.model_dump_json(indent=2))

asyncio.run(main())
```

### Cost report

```bash
python3 worktree-session-manager.py llm-cost $SID
# Output:
# SID: abc123def456
# ┌──────────────────────────────┬───────┬──────────────┬───────────────┬──────────────┐
# │ Model                        │ Calls │ Input tokens │ Output tokens │ Cost (USD)   │
# ├──────────────────────────────┼───────┼──────────────┼───────────────┼──────────────┤
# │ claude-sonnet-4-5            │    42 │       84,231 │        12,445 │    $0.44     │
# └──────────────────────────────┴───────┴──────────────┴───────────────┴──────────────┘
```

### Teardown

```bash
# Teardown with LLM session close and cost summary
python3 worktree-session-manager.py teardown $SID

# Or explicit close first
python3 worktree-session-manager.py llm-session-close $SID
python3 worktree-session-manager.py teardown $SID
```

### Shell aliases (add to `~/.bashrc` or `~/.zshrc`)

```bash
source /home/daen/Projects/cybersecsuite/scripts/gwt-aliases.sh

# After sourcing, usage:
gwt-create main          # creates worktree + exports GWT_SID
gwt-teardown $GWT_SID    # tears down
gwt-sid                  # prints current SID
gwt-list                 # lists all worktrees
```

---

## 11. Token Optimization Notes & Warnings

### ⚠️ Critical: never log prompt text to OpenObserve or Postgres

The `bulk_index("llm-calls", [...])` payload **must never** contain `messages`, `content`, or `response_text` fields. Only metadata goes into OO:

```python
# CORRECT — metadata only
{"worktree_sid": sid, "model": model, "input_tokens": 1234, "cost_usd": 0.004}

# WRONG — never do this
{"worktree_sid": sid, "messages": messages, "response": full_response_text}
```

### Async background writes

All DB writes go through `asyncio.create_task(self._bg_persist(...))` — they are fully fire-and-forget and never block the streaming response. Errors in `_bg_persist` are caught and logged at WARNING level.

### Streaming vs. non-streaming token efficiency

- Use `stream=True` (default) for interactive responses — yields tokens immediately, no buffer memory overhead
- Use `stream=False` only for structured outputs and batch processing

### Anthropic prompt caching

Structure messages to maximise cache hits:
1. Put static system prompt **first** (marked with `"cache_control": {"type": "ephemeral"}`)
2. Put dynamic user content **last**
3. Cache read tokens cost 10× less than regular input tokens

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": STATIC_SYSTEM_CONTEXT,
             "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": dynamic_query},
        ]
    }
]
```

### OTEL sampling in production

Set sampling rate to 10% in production to reduce OTLP overhead:

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
sampler = TraceIdRatioBased(0.1)  # 10% sampling
```

### Postgres write batching

If call volume exceeds 100 req/s, switch `_bg_persist` to a write queue with 500ms flush:

```python
asyncio.create_task(write_queue.push(call_record))
# Background loop flushes queue to Postgres every 500ms
```

### OpenObserve stream retention

Set a 30-day retention policy on `cybersecsuite-llm-*` streams in the OpenObserve admin UI to prevent unbounded disk growth.

---

## 12. Future Extensions

1. **Per-model cost budget guard** — extend `LLMOrchestrator` to enforce a `max_cost_usd_per_session` limit; raise `BudgetExceededError` and close the DB session automatically.

2. **Prompt hash deduplication** — hash message arrays with BLAKE2b-256; store hash in `llm_calls.prompt_hash`; detect identical prompts and return cached responses (semantic cache layer).

3. **Multi-provider routing** — route LLM calls through the existing `src/ai_proxy/` smart router (`smart_route()`), making `AsyncLLMClient` provider-agnostic and retrying on failure.

4. **C++ SID detector hook** — compile a minimal C extension (via `ctypes` or `pybind11`) that reads the `.worktree-session` marker with zero Python import overhead, usable from pre-commit hooks in compiled agents.

5. **Real-time cost dashboard panel** — add a new `/api/llm/cost` endpoint in `src/dashboard/api/` and a live-updating panel in the forensic dashboard, fed from `llm_cost_by_model` materialized view.

6. **OTEL traces in Grafana** — expose OpenObserve OTLP data to Grafana Tempo for distributed trace UI, linking git worktree spans to upstream agent spans.

7. **Conversation replay** — if `log_prompts=True` is explicitly set, store compressed message arrays in a separate `llm_conversations` table (ZSTD-compressed JSONB), enabling full session replay and debugging.

---

---

# Dashboard UX & Platform Overhaul Sprint

> **Sprint blueprint** — Full-stack UI/UX overhaul of the CyberSecSuite dashboard:
> CRUD everywhere, provider intelligence, Intel Feed, sidebar reorder, DB deduplication.

---

## 1. Problem Statement

The live dashboard has read-only views for most entities (Cases, Tasks, Findings, IOCs, Investigations, A2A, PoC, Prompts, Workflows, Templates), incomplete provider intelligence (NVIDIA credentials ignored, Grok/Ollama always green regardless of auth state), confusing sidebar structure, a broken vault path, and redundant DB tables. This sprint delivers a complete overhaul.

---

## 2. Scope

### 2.1 CRUD Surfaces Needed
| Tab | Current State | Target |
|-----|--------------|--------|
| Prompts | Read-only plugin lister | Full CRUD — create/edit/delete stored prompts in DB |
| Workflows | In-memory only, empty UI | Persist to DB + CRUD UI (create, run, edit, delete) |
| Cases | Read-only table | Modal CRUD (create, update status, close, delete) |
| Tasks | Read-only table | Modal CRUD |
| PoC | `simple_panel` loading text | CRUD + seed dropdown (CVE, GHDB, custom URL, manual) |
| A2A | `simple_panel` loading text | Full CRUD (create task, view, cancel, delete) |
| Investigations | `simple_panel` loading text | CRUD (open/close investigation, edit, delete) |
| Findings | Table + heatmap, no forms | Modal CRUD |
| IOCs | Table + breakdown, no forms | Modal CRUD |
| Templates & Workflows | Stat counters + table | Full CRUD for templates; separate from Workflow tab |
| Intel Feed | MITRE/CVE stats, no source mgmt | Add Intel Feed Sources CRUD + news/RSS source mgmt |

### 2.2 Provider Hub Fixes
- **NVIDIA** (and all `api_key` auth providers): credentials added via AccountManager (DB) are ignored by `is_available` which only checks `os.environ`. Fix: `api_providers_hub` must check `accounts_by_provider` — if a provider has an active account, treat it as `available`.
- **Grok (x.com + grok.com)** (`auth_type=BROWSER`): currently always `available` because `is_available` returns `True` for `BROWSER` auth. Must only be green when a valid browser session/cookies exist for those domains.
- **Ollama + LM Studio** (`auth_type=NONE`, `is_free=True`): currently always `available`. Must only be green when the local endpoint is reachable AND reports at least one loaded model (use existing `api_local_llm_status` logic).
- **Free tier providers** (`is_free=True`, requires account): show as `free_tier` status (green-ish) only when a free account exists; otherwise show `no_account` (amber). Make it visually clear these are tiered.
- **On/Off toggle**: replace `● On / ○ Off` text buttons with a styled CSS toggle switch.

### 2.3 Navigation / Sidebar Overhaul
- **Remove** `network` tab from forensics group.
- **Remove** `dbcounts` tab from data group.
- **Reorder sidebar**: Chat first, then AI PROXY group, then AGENTS group (Agent Factory, Crafter, Team Builder, Query, Chat, Workflows, Flowgraph, Prompts, SDK Lab), then remaining groups.
- **SETTINGS**: keep as last collapsible dropdown; remove the "SETTINGS" group header label from sidebar rendering. Claude SDK and CyberSecSuite settings should have the same form layout/quality.
- **Remove** the `<select id="settings-project-select">` project scope widget from both settings panels.
- **Remove** vault widget (`_vault_widget`) from settings — remove entirely from nav + rendering.
- **Memory Vault path**: fix `_VAULT_PATH` default from `./data/vault` → `~/.cybersecsuite/data/vault`.

### 2.4 Intel Feed Sources
- Create new DB model `IntelFeedSource` with fields: `id`, `name`, `url`, `feed_type` (rss/atom/json/html), `category` (cti/nvd/news/blog/gov), `is_active`, `last_fetched_at`, `description`, `created_at`, `updated_at`.
- Bootstrap with ~20 pre-seeded URLs (CVE feeds, CISA alerts, threat intel blogs, etc.).
- CRUD API + UI for managing sources.
- Intel Feed panel: replace static MITRE/CVE stats with source management + recent articles view.

### 2.5 DB Redundancy Audit

#### `llm_sessions` vs `sessions` — Verdict: **NOT redundant, keep both as-is**

After deep inspection of `src/db/models/llm_session.py`, `src/db/models/scope.py`, `src/db/models/forensic.py`, and `src/llm/db.py`, the full session hierarchy is:

```
Project  ─FK─►  Session (scope)  ─FK─►  ForensicSession  ─FK─►  ForensicFinding / IOC
                                                                  (investigation scope)

LlmSession (worktree SID)  ─FK─►  LlmCall
(git worktree lifecycle / LLM cost tracker)
```

**`LlmSession`** (`table: llm_sessions`):
- PK is a **12-char hex git worktree SID** (generated by `worktree-session-manager.py`)
- Written via **raw asyncpg** in `src/llm/db.py` — intentionally bypasses Tortoise ORM so the CLI can call it outside the ASGI process
- Tracks: `repo_root`, `branch`, `opened_at`, `closed_at`, token totals, cost totals
- FK'd to by `LlmCall` (one row per Anthropic API call)
- **Purpose**: git-worktree-scoped LLM cost/token observability

**`Session`** (`table: sessions`):
- PK is an auto-increment int; `session_id` is a UUID-128 string
- Managed by the forensic/ASGI application, tied to a `Project`
- FK'd to by: `AuditLog`, `Artifacts`, `Compliance`, `Defense`, `Vulnerability`, `UserGuidance`, `ForensicSession`
- **Purpose**: forensic/operational scope anchor for all investigation data

**`ForensicSession`** (`table: forensic_sessions`):
- Bridges `Session` (via `scope_session` FK) and `ForensicProject`
- Holds system context, phase, investigator, verdicts
- **Purpose**: the actual investigation session with full system/case context

**Why no FK correlation is needed**: the two systems (`LlmSession` and `Session`) are truly orthogonal — one is bound to a git worktree (which can span multiple forensic sessions), the other to a forensic investigation scoped by Project. Adding a FK from `Session` to `LlmSession` was proposed earlier; **this is dropped** — the SID mismatch (12-char hex vs UUID) and different lifecycle managers make it noise without benefit.

**Action**: No schema changes needed. Just add clear docstrings to both models explaining their distinct purpose. Remove the `db-session-correlation` todo.

#### Scope tables (`Project`, `Application`, `Session`, `ScopedEntry`)
- All needed as FK roots. Keep as-is.
- `Application` model is currently unused in the UI and has no FKs from other models — **mark as deprecated**, do not delete yet (migration risk).

#### Other redundancy
- `src/db/models/artifact.py` and `src/db/models/artifacts.py` — two files with similar names. Check if both export different models or one is a duplicate. Audit only; no deletion without confirmation.
- Remove the project scope `<select>` from the dashboard UI (the `settings-project-select`) since project switching is unnecessary complexity.

### 2.6 Button / Color System
- Currently, all action buttons use `btn btn-primary` (blue). Introduce semantic color variants:
  - `btn-primary` (blue) — main CTA (submit, save)
  - `btn-success` (green) — create/confirm
  - `btn-danger` (red) — delete/revoke
  - `btn-warning` (amber) — disable/deactivate
  - `btn-ghost` (neutral) — cancel/close/secondary
- Apply consistently across all panels and modals.

### 2.7 Routing Panel
- Currently `simple_panel("routing", ...)` shows a loading spinner forever.
- Replace with proper forms: strategy selector, combo editor, resilience profile, simulate route form, explain route form. Use Playwright to inspect current state first.

---

## 3. Files Affected — Full Detail

### 3.1 Database Models

#### `src/db/models/vault_source.py` *(NEW)*
Create `IntelFeedSource` Tortoise model:
```python
class IntelFeedSource(Model):
    id = IntField(pk=True)
    name = CharField(max_length=255, unique=True)
    url = CharField(max_length=1024)
    feed_type = CharField(max_length=32, default="rss")   # rss|atom|json|html
    category = CharField(max_length=64, default="cti")    # cti|nvd|news|blog|gov
    is_active = BooleanField(default=True)
    last_fetched_at = DatetimeField(null=True)
    description = TextField(default="")
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)
    class Meta:
        table = "intel_feed_sources"
```

#### `src/db/models/__init__.py`
Register `IntelFeedSource` in the model registry list.

#### `src/db/models/llm_session.py`
Add a docstring clarifying this is git-worktree scoped (not a forensic session). No schema change needed.

#### `src/db/models/scope.py`
Add optional `llm_sid` field to `Session` for correlation to `LlmSession`. Document `Application` as deprecated-pending-removal.

#### `src/db/seeds/intel_feed_sources.py` *(NEW)*
Seed script with ~20 pre-seeded sources:
- CISA Known Exploited Vulnerabilities (`https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`)
- NVD CVE feed (`https://nvd.nist.gov/feeds/json/cve/1.1/`)
- MITRE ATT&CK STIX (`https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json`)
- Krebs on Security RSS
- Schneier on Security RSS
- The Hacker News RSS
- BleepingComputer RSS
- Threatpost RSS
- SANS Internet Storm Center RSS
- AlienVault OTX recent pulses API
- Recorded Future free threat intel
- MISP threat sharing feeds
- CERT/CC vulnerability notes
- US-CERT alerts
- etc.

### 3.2 AI Proxy — Provider Status

#### `src/ai_proxy/providers/registry.py`
**Change `is_available`**: Add a new optional callable hook `_availability_override: Callable[[ProviderConfig], bool | None] | None = None` that external code can set to inject runtime checks (local LLM reachability, browser session state). This keeps the registry pure while allowing overrides.

#### `src/dashboard/api/core.py` — `api_providers_hub`
This is the main fix surface:

1. **NVIDIA / API-key providers with DB accounts**: After building `accounts_by_provider`, compute a corrected status:
   ```python
   # If provider has active DB accounts → treat as available regardless of env
   has_active_account = any(a["active"] for a in accounts_by_provider.get(p.id, []))
   if p.auth_type == AuthType.API_KEY and has_active_account:
       status = "available"
   ```

2. **Ollama / LM Studio**: Call the internal `api_local_llm_status` logic inline (or cache it in a module-level dict refreshed every 30s). If endpoint reachable + models > 0 → `available`, else `no_model_loaded`.

3. **Grok browser providers**: Check if a browser profile directory exists and contains cookies for `x.com` / `grok.com`. Use a lightweight cookie-jar parse:
   ```python
   # Check brave/chrome profile for x.com cookies
   profile_dir = Path(p.browser_profile or "")
   cookie_file = profile_dir / "Default" / "Cookies"
   has_session = _check_browser_cookies(cookie_file, domain=".x.com")
   status = "available" if has_session else "browser_not_authenticated"
   ```
   Add helper `_check_browser_cookies(cookie_file, domain)` that reads SQLite cookies DB.

4. **Free tier providers** (`is_free=True`, `auth_type=NONE` but NOT local): return new status `"free_tier"` rather than `"available"`, so the UI can style them distinctly.

5. Add new status value `"browser_not_authenticated"` and `"no_model_loaded"` for the frontend to handle.

#### `src/ai_proxy/providers/_providers.py`
No schema changes needed. Add `# local provider` comments to Ollama/LM Studio entries.

### 3.3 Dashboard API Layer

#### `src/dashboard/api/vault_status.py`
Change default vault path:
```python
_DEFAULT_VAULT = Path.home() / ".cybersecsuite" / "data" / "vault"
_VAULT_PATH = os.getenv("CYBERSEC_VAULT_PATH", str(_DEFAULT_VAULT))
```

#### `src/dashboard/api/cases.py` *(NEW or extend existing)*
Check if cases CRUD API already exists in `forensic.py` or `tables.py`. If not, create:
```
GET  /api/cases          → list with pagination/filter
POST /api/cases          → create
GET  /api/cases/{id}     → get one
PATCH /api/cases/{id}    → update (status, name, desc)
DELETE /api/cases/{id}   → soft-delete
```
Uses `CaseIntake` model (`src/db/models/case_intake.py`).

#### `src/dashboard/api/tasks.py` *(NEW)*
Full CRUD for `A2ATask` model (`src/db/models/a2a_task.py`):
```
GET    /api/tasks
POST   /api/tasks
GET    /api/tasks/{id}
PATCH  /api/tasks/{id}
DELETE /api/tasks/{id}
```

#### `src/dashboard/api/pocs.py` *(NEW or extend)*
CRUD for PoC (`src/db/models/poc.py`) + seed endpoint:
```
GET    /api/pocs
POST   /api/pocs
PATCH  /api/pocs/{id}
DELETE /api/pocs/{id}
POST   /api/pocs/seed     → body: {source: "cve"|"ghdb"|"url"|"manual", value: "..."}
```

#### `src/dashboard/api/a2a_crud.py` *(NEW)*
CRUD for A2A tasks/agents that live in the DB (separate from in-flight A2A protocol tasks):
```
GET    /api/a2a/tasks
POST   /api/a2a/tasks
PATCH  /api/a2a/tasks/{id}
DELETE /api/a2a/tasks/{id}
```

#### `src/dashboard/api/forensic.py`
Extend with CRUD endpoints for Findings, IOCs, Investigations if not already present:
```
POST   /api/findings          → create
PATCH  /api/findings/{id}     → update severity/status
DELETE /api/findings/{id}     → soft-delete
POST   /api/iocs              → create
PATCH  /api/iocs/{id}
DELETE /api/iocs/{id}
POST   /api/investigations
PATCH  /api/investigations/{id}
DELETE /api/investigations/{id}
```

#### `src/dashboard/api/intel_feed.py` *(NEW)*
CRUD for `IntelFeedSource`:
```
GET    /api/intel/sources
POST   /api/intel/sources
PATCH  /api/intel/sources/{id}
DELETE /api/intel/sources/{id}
POST   /api/intel/sources/bootstrap   → seed defaults
POST   /api/intel/sources/{id}/fetch  → trigger fetch
```

#### `src/dashboard/api/prompts_crud.py` *(NEW)*
Replace read-only `api_prompts` in `tables.py` with full CRUD. Store prompts in a new `Prompt` DB model (text, name, category, tags). For now can be file-backed JSON if DB model not yet created.
```
GET    /api/prompts
POST   /api/prompts
PATCH  /api/prompts/{id}
DELETE /api/prompts/{id}
```

#### `src/dashboard/api/workflows.py`
Add DB persistence: create `Workflow` DB model (or use SharedEntry). Add `POST /api/workflows` (persist), `PATCH /api/workflows/{id}`, `DELETE /api/workflows/{id}` on top of existing in-memory logic.

#### `src/dashboard/api/template_registry.py`
Extend with CRUD: `POST /api/templates`, `PATCH /api/templates/{id}`, `DELETE /api/templates/{id}`.

#### `src/dashboard/api/settings.py`
Remove logic that serves the `settings-project-select` data (no longer needed in UI).

#### `src/dashboard/api/__init__.py`
Register all new API handlers and route them in `routes.py`.

#### `src/dashboard/routes.py`
Add routes for all new CRUD endpoints.

### 3.4 Dashboard Templates

#### `src/dashboard/templates/_tabs.py`
1. **Remove** `("network", "Network", ...)` entry from forensics group.
2. **Remove** `("dbcounts", "DB Counts", ...)` entry from data group.
3. **Remove** `("vault", "Memory Vault", ...)` from SETTINGS dropdown children.
4. **Move** `("chat", "Chat", ...)` to be the very first entry in sidebar (before PLATFORM or as its own top group).
5. **Rename** SETTINGS group: remove the group header label rendering entirely — keep the dropdown but suppress the `SETTINGS` section header.
6. **Reorder groups**: `["chat-top", "proxy", "agents", "ops", "forensics", "data", "settings"]`.
7. Update `_GROUPS` dict accordingly.

#### `src/dashboard/templates/panels/settings.py`
1. Remove `_vault_widget()` function and its registration.
2. Remove `settings-project-select` HTML from both `_settings()` and `_settings_cybersecsuite()`.
3. Make Claude SDK settings form and CyberSecSuite settings form use the same HTML component primitives (`form_field`, `form_input`, `form_select`). Both should use identical grid layout, label style, input style.
4. Remove the "SETTINGS Header" `<h2>` if it exists as a static element in any panel.

#### `src/dashboard/templates/panels/operations.py`
Replace minimal `_cases()`, `_tasks()`, `_pocs()`, `_a2a()` with full CRUD panels:

**`_cases()`**: Add create-case form section above the table (fields: name, severity, description, phase). Add per-row edit/delete action buttons column. Add modal for editing.

**`_tasks()`**: Same pattern — create form, table with actions.

**`_pocs()`**: Rebuild from `simple_panel` to `tab_panel` with: (a) create PoC form, (b) seed section with `<select>` for source type (CVE ID, GHDB dork, URL, manual entry), (c) table with actions.

**`_a2a()`**: Rebuild from `simple_panel` to `tab_panel` with: create A2A task form (agent, prompt, params), task list table with status badges, cancel/delete actions.

#### `src/dashboard/templates/panels/forensics.py`
1. **Remove** `_network()` function entirely.
2. Update `__all__` / imports in `panels/__init__.py`.
3. **`_investigations()`**: Rebuild from `simple_panel` to CRUD panel with create form and table.
4. **`_findings()`**: Add create-finding form section + per-row edit/delete buttons.
5. **`_iocs()`**: Add create-IOC form section + per-row edit/delete buttons.
6. **`_intel()`**: Replace MITRE/CVE stat cards with Intel Feed Sources management: source list table (URL, type, last fetch), add-source form, fetch-now buttons per source.

#### `src/dashboard/templates/panels/data.py`
1. **Remove** `_dbcounts()` function entirely.
2. **`_templates()`**: Rename to reflect Templates-only (Workflows has its own tab). Add create-template form section + per-row edit/delete.
3. Keep `_opensearch()` and `_explorer()` as-is (UI exists, data loading is a runtime concern).

#### `src/dashboard/templates/panels/agents.py`
1. **`_routing()`**: Replace `simple_panel` with proper form-based panel:
   - Strategy selector (`<select>` with all 13 routing strategies)
   - Resilience profile selector
   - Active combo display
   - Simulate-route form (model input + submit)
   - Explain-route form
   - No list view for combos (remove the combo list)
2. **`_prompts()`**: Replace `simple_panel` with CRUD panel: create-prompt form (name, content, category), table with edit/delete.

#### `src/dashboard/templates/panels/__init__.py`
1. Remove `_network` from imports and panel assembly.
2. Remove `_dbcounts` from imports and panel assembly.
3. Remove `_vault_widget` from imports and panel assembly.
4. Add new panel registrations as needed.

#### `src/dashboard/templates/_components.py`
Add `btn_toggle(id, checked, onchange)` component that renders a CSS toggle switch (not a button).

### 3.5 TypeScript Frontend

#### `src/dashboard/static/ts/providers_hub.ts`
1. **Status color map**: Add new status values:
   - `"browser_not_authenticated"` → amber (same as `no_credentials`)
   - `"no_model_loaded"` → amber  
   - `"free_tier"` → a distinct green-teal with a "FREE" badge
   - Rename group labels: `"Available"` (green), `"No Credentials / Unconfigured"` (amber), `"Disabled"` (gray).
2. **On/Off toggle**: Replace `btn btn-ghost` text buttons with CSS toggle switch component:
   ```html
   <label class="ph-toggle">
     <input type="checkbox" checked onclick="...">
     <span class="ph-toggle-slider"></span>
   </label>
   ```
   Add CSS for `.ph-toggle` (pill-style toggle, green when on, gray when off).
3. **Status re-computation after account add**: After `phSaveAccount()` success, reload hub data so NVIDIA etc. show green immediately.
4. **Free tier badge**: For `status === "free_tier"`, show a small `FREE` chip next to the provider name, tooltip: "Free tier — account required for higher limits".

#### `src/dashboard/static/ts/settings.ts`
1. Remove all code that populates or reads `settings-project-select`.
2. Ensure Claude and CCS settings forms use the same render helpers.

#### `src/dashboard/static/ts/refresh.ts`
1. Remove any periodic refresh calls for `dbcounts` endpoint.
2. Remove any network panel data refresh.

#### `src/dashboard/static/ts/sidebar.ts`
1. Update group rendering to suppress the SETTINGS section header label.
2. Handle the new `chat-top` special group (or just ensure chat appears first).

#### `src/dashboard/static/ts/index.ts`
1. Remove import/call for vault panel JS if any.
2. Remove DB counts initialization.
3. Remove network panel initialization.
4. Wire new CRUD panels: cases, tasks, pocs, a2a, investigations, findings crud, iocs crud, intel sources.

#### `src/dashboard/static/ts/routing.ts` *(NEW)*
Full routing panel TypeScript:
- `loadRoutingPanel()` — fetches `/api/routing/strategies`, `/api/routing/combos`, `/api/routing/resilience`
- `renderStrategyForm()` — dropdown + submit
- `renderSimulateForm()` — model + message + submit → show result
- `renderExplainForm()` — combo ID input + submit → show explanation
- Remove combo list rendering

#### New TS files for CRUD panels (or add to existing files):
- `src/dashboard/static/ts/cases.ts` — CRUD handlers for Cases
- `src/dashboard/static/ts/tasks_crud.ts` — CRUD handlers for Tasks
- `src/dashboard/static/ts/pocs.ts` — CRUD handlers for PoCs + seed
- `src/dashboard/static/ts/a2a_crud.ts` — CRUD handlers for A2A
- `src/dashboard/static/ts/intel_sources.ts` — CRUD handlers for Intel Feed Sources
- `src/dashboard/static/ts/prompts_crud.ts` — CRUD handlers for Prompts

### 3.6 CSS / Styles

#### `src/dashboard/static/` CSS (inline or separate file)
Add CSS:
```css
/* Toggle switch */
.ph-toggle { position: relative; display: inline-block; width: 36px; height: 20px; }
.ph-toggle input { opacity: 0; width: 0; height: 0; }
.ph-toggle-slider { position: absolute; cursor: pointer; top:0; left:0; right:0; bottom:0;
  background: var(--border); border-radius: 20px; transition: .2s; }
.ph-toggle input:checked + .ph-toggle-slider { background: var(--success); }
.ph-toggle-slider:before { content: ""; position: absolute; height: 14px; width: 14px;
  left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: .2s; }
.ph-toggle input:checked + .ph-toggle-slider:before { transform: translateX(16px); }

/* Button color variants */
.btn-success { background: var(--success); color: #000; }
.btn-danger  { background: var(--red); color: #fff; }
.btn-warning { background: var(--amber); color: #000; }
```

### 3.7 Build

#### `src/dashboard/tsconfig.json`
Ensure new `.ts` files are included in compilation (should auto-include via `include: ["static/ts/**/*"]`).

---

## 4. Migration Notes

- `IntelFeedSource` requires a new Aerich migration: `uv run aerich migrate --name add_intel_feed_sources`.
- `Session.llm_sid` optional FK needs migration too.
- Seed script `intel_feed_sources.py` should be callable via `uv run python -m manage seed-intel-feeds`.

---

## 5. Testing Plan

- Playwright smoke test: providers hub loads, NVIDIA shows green after account add, Grok shows amber when no browser session.
- Playwright: toggle switch works (on/off).
- API unit tests for all new CRUD endpoints (GET/POST/PATCH/DELETE).
- DB migration test: `aerich migrate` completes cleanly.
- Sidebar: network and dbcounts tabs absent; chat appears first.

---

## 6. Task Breakdown (SQL-tracked)

See SQL `todos` table for per-task status tracking.

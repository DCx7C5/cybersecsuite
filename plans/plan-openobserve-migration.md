# OpenObserve Migration Plan

## Goal
Move append-only / time-series tables from PostgreSQL → OpenObserve. Postgres stays the authoritative store for relational/operational data. OpenObserve is for observability: logs, metrics, usage, audit trails.

## Current state

| Table                      | PG model                     | OO stream                   | Status                                       |
|----------------------------|------------------------------|-----------------------------|----------------------------------------------|
| `audit_logs`               | `AuditLog`                   | `cybersecsuite-audit-*`     | migrate cmd ✅, not yet executed              |
| `api_usage_log`            | `ApiUsageLog`                | `cybersecsuite-api-usage-*` | migrate cmd ✅, not yet executed              |
| `llm_calls`                | `LlmCall`                    | `cybersecsuite-llm-calls-*` | dual-write ✅, **no migrate cmd**, no PG drop |
| `intel_update_log_entries` | `IntelligenceUpdateLogEntry` | —                           | no cmd, no stream                            |

### Already wired (ASGI lifespan)
- `ensure_streams()` + `start_flush_loop()` called on startup
- `flush_all()` + `stop_flush_loop()` + `close_client()` on shutdown
- `llm/client.py` already dual-writes to `llm-calls` stream via `_oo_index`
- Streams list in `src/openobserve/streams.py` only has 3: `telemetry`, `audit`, `api-usage`

### Not moving to OpenObserve
All intel KB tables (`intel_cves`, `intel_mitre_*`, `intel_cwes`, `intel_capec_*`, `intel_ioc_db_entries`, `intel_misp_*`, `intel_opencti_*`, `intel_feed_snapshots`) stay in Postgres — they are structured reference data with FK relations from operational models, not time-series.

---

## Phases

### Phase 1 — Register missing streams
**File:** `src/openobserve/streams.py`

Add `llm-calls` and `intel-update-log` to the `STREAMS` list so `ensure_streams()` verifies/creates them on startup.

### Phase 2 — `migrate-llm-calls` command
**File:** `src/manage/_commands.py`

Pattern matches `migrate_audit_command`. Steps:
1. Page all `LlmCall` rows ordered by `called_at`
2. Bulk-POST to `cybersecsuite-llm-calls-YYYY.MM.DD` stream via OO HTTP API
3. Verify OO record count ≥ migrated count
4. Prompt: drop PG table `llm_calls`

Register in `src/manage/__init__.py` as `migrate-llm-calls`.

After migration:
- Remove `LlmCall` from `MODEL_MODULES` in `src/db/models/__init__.py`
- Remove `db_persist_fn` / `llm/db.py` PG write path from `llm/client.py` — OO write becomes the only sink

### Phase 3 — `migrate-intel-update-log` command
**File:** `src/manage/_commands.py`

Page `IntelligenceUpdateLogEntry` rows → `cybersecsuite-intel-update-log-*` stream. Verify + prompt drop `intel_update_log_entries`.

Register in `src/manage/__init__.py` as `migrate-intel-update-log`.

After migration:
- Remove `IntelligenceUpdateLogEntry` from `MODEL_MODULES`
- Update intel bootstrap code that writes to this table to write to OO stream instead

### Phase 4 — Execute existing migrate commands
Run (in order, in production):
```
uv run python -m manage migrate-audit
uv run python -m manage migrate-api-usage
uv run python -m manage migrate-llm-calls
uv run python -m manage migrate-intel-update-log
```

Each command already prints count verification and requires manual `yes` confirmation before dropping PG tables.

### Phase 5 — Clean up PG models + ORM
After all four tables are confirmed dropped:
- Remove `db.models.audit` (re-export), `db.models.core.AuditLog` class
- Remove `db.models.api_usage_log.ApiUsageLog`
- Remove `db.models.llm_call.LlmCall`
- Remove `db.models.update_log_entry.IntelligenceUpdateLogEntry`
- Remove their entries from `MODEL_MODULES`
- Remove `AuditLog` FK reference in `db.models.core` (`ForensicSession.audit_logs` relation)

### Phase 6 — Dashboard OO stats panel fix
**File:** `src/dashboard/api/opensearch_stats.py`

Currently, calls `ensure_streams()` and returns dummy `docs=0`. Replace with real OO stats by calling the OpenObserve stream stats API (`/api/{org}/{stream}/_stats`) for each stream and returning actual doc count + size.

---

## Stream naming convention
All streams follow: `cybersecsuite-<name>-YYYY.MM.DD` (daily rollover, auto-stamped by `bulk_index()`).

| Stream base        | Source table               | Mapped in STREAMS  |
|--------------------|----------------------------|--------------------|
| `telemetry`        | in-process metrics         | ✅                  |
| `audit`            | `audit_logs`               | ✅                  |
| `api-usage`        | `api_usage_log`            | ✅                  |
| `llm-calls`        | `llm_calls`                | ❌ add in Phase 1   |
| `intel-update-log` | `intel_update_log_entries` | ❌ add in Phase 1   |

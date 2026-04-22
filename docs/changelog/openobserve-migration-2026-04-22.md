# OpenObserve Migration — 2026-04-22

## Summary

Four append-only / time-series PostgreSQL tables migrated to **OpenObserve** (OO).
The tables were write-heavy, never queried relationally, and carried no FK constraints
worth preserving in Postgres. OpenObserve is now the authoritative sink for all
observability data.

---

## Tables migrated → dropped

| PG table                  | ORM model                     | OO stream (base name)    |
|---------------------------|-------------------------------|--------------------------|
| `audit_logs`              | `AuditLog`                    | `cybersecsuite-audit`    |
| `api_usage_log`           | `ApiUsageLog`                 | `cybersecsuite-api-usage`|
| `llm_calls`               | `LlmCall`                     | `cybersecsuite-llm-calls`|
| `intel_update_log_entries`| `IntelligenceUpdateLogEntry`  | `cybersecsuite-intel-update-log` |

All four tables were empty at the time of migration (no historical data to transfer).

---

## What changed

### `src/openobserve/streams.py`
Added `"llm-calls"` and `"intel-update-log"` to `STREAMS` so `ensure_streams()`
registers them on startup.

### `src/manage/_commands.py`
- Fixed `migrate_audit_command` — was using OpenSearch API methods on the OO client
  (broken since initial implementation).
- Fixed `migrate_api_usage_command` — same issue.
- Added `migrate_llm_calls_command` — pages `LlmCall` rows → OO `llm-calls` stream,
  then drops `llm_calls` table.
- Added `migrate_intel_update_log_command` — pages `IntelligenceUpdateLogEntry` rows
  → OO `intel-update-log` stream, then drops `intel_update_log_entries`.

### `src/manage/__init__.py`
Registered `migrate-llm-calls` and `migrate-intel-update-log` in the command dispatch.
Updated usage text (was incorrectly labelled "OpenSearch").

### `src/llm/orchestrator.py`
Removed `db_persist_fn=persist_call` — the PG write path to `llm_calls`.
OO `oo_index_fn` remains the only persistence sink.

### `src/llm/db.py`
- `close_session` — removed aggregation subqueries over `llm_calls`; now just sets
  `closed_at`. Per-call totals are in OO.
- `cost_report` — removed per-model breakdown from `llm_calls`; returns session row
  only (detailed breakdown queryable from OO `llm-calls` stream).

### `src/db/intel/bootstrap.py`
`bootstrap_update_log_async` now writes parsed update-log entries to OO
`intel-update-log` stream via `bulk_index()`. Removed the `bulk_create` PG path and
the pre-run `delete()` call (OO is append-only; idempotency is handled by snapshot
checksumming upstream).

### `src/dashboard/api/charts.py`
`_token_trend` now queries per-day doc counts from OO `cybersecsuite-api-usage-*`
stream stats endpoint instead of counting `ApiUsageLog` rows.

### `src/dashboard/api/forensic.py`
`api_audit` now queries total doc count from OO `cybersecsuite-audit-*` stream stats
endpoint. Detailed recent-entries list is not yet implemented (returns empty list).

### `src/dashboard/api/opensearch_stats.py`
Fixed dummy `docs=0` — now fetches real doc counts and storage sizes per OO stream
via `GET /api/{org}/{stream}`.

### `src/db/models/core.py`
Removed `AuditLog` model class and its `AuditAction` enum import.

### `src/db/models/__init__.py`
Removed from `MODEL_MODULES`:
- `db.models.audit`
- `db.models.api_usage_log`
- `db.models.llm_call`
- `db.models.update_log_entry`

Removed `LlmCall` from exports and `__all__`.

### `docker-compose.yml`
Changed `cybersec-openobserve` from `expose: ["5080"]` to `ports: ["${OPENOBSERVE_PORT:-5080}:5080"]`.
This makes OO reachable at `localhost:5080` for local `manage` commands and dev tools.

### Deleted files
- `src/db/models/audit.py`
- `src/db/models/api_usage_log.py`
- `src/db/models/llm_call.py`
- `src/db/models/update_log_entry.py`

---

## What stays in PostgreSQL

Intel KB tables (`intel_cves`, `intel_mitre_*`, `intel_cwes`, `intel_capec_*`,
`intel_ioc_db_entries`, `intel_misp_*`, `intel_opencti_*`, `intel_feed_snapshots`)
are structured reference data with FK relations from operational models.
They are **not** time-series and remain in Postgres.

---

## Manage commands

```bash
# These commands now exist but the tables are already gone.
# Kept for future use if re-seeding from a backup.
uv run python -m manage migrate-audit
uv run python -m manage migrate-api-usage
uv run python -m manage migrate-llm-calls
uv run python -m manage migrate-intel-update-log
```

Each command pages through the source PG table in batches of 500, bulk-POSTs to the
OO stream, verifies doc count ≥ migrated count, then drops the table after a `yes`
confirmation.

---

## Stream naming convention

All streams: `cybersecsuite-<base>-YYYY.MM.DD` (daily rollover, stamped by `bulk_index()`).

| Stream base         | Source                         |
|---------------------|--------------------------------|
| `telemetry`         | in-process OTEL metrics        |
| `audit`             | `audit_logs` (dropped)         |
| `api-usage`         | `api_usage_log` (dropped)      |
| `llm-calls`         | `llm_calls` (dropped)          |
| `intel-update-log`  | `intel_update_log_entries` (dropped) |

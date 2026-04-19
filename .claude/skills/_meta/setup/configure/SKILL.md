---
name: setup-configure
description: CyberSecSuite DB setup — initialize PostgreSQL via Tortoise ORM migrations, check connection/table status, or reset (destructive). Wraps manage.py with env-variable-driven config.
domain: cybersecurity
subdomain: ops
tags:
- setup
- database
- postgresql
- migrations
- tortoise-orm
mitre_attack: []
cve: []
cwe: []
nist_csf: []
capec: []
---
## Overview

One-stop database lifecycle tool for CyberSecSuite. Reads DB credentials from environment variables, runs Tortoise ORM migrations via `manage.py`, and provides status checks. All three operations are idempotent except `reset` (destructive — drops all tables).

## Usage

```
setup init      — connect + run migrations (safe, idempotent)
setup status    — show connection info + table list
setup reset     — drop all tables then re-migrate (⚠ destructive)
```

## Environment Variables

| Variable | Default |
|---|---|
| `CYBERSEC_DB_NAME` | `cybersec_forensics` |
| `CYBERSEC_DB_USER` | `cybersec` |
| `CYBERSEC_DB_PASSWORD` | `change-me-now` |
| `CYBERSEC_DB_HOST` | (empty → localhost) |
| `CYBERSEC_DB_PORT` | (empty → 5432) |

## Notes

- Uses `db.bootstrap.init_tortoise` and `manage.py` as subprocess
- `hooks.database.write_entry_sync` called on each lifecycle event for audit trail
- Equivalent to: `uv run python -m manage migrate` but with status output and safety guards

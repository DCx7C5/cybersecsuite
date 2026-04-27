# Deprecation Audit: `src/accounts/`

**Verdict:** KEPT (ACTIVE)

**Audit date:** 2025-07-28

## Evidence

| Metric | Count |
|--------|-------|
| External import sites (non-accounts source files) | 2 |
| Test files covering this module | 1 |
| Test functions | 5 |
| Listed in `pyproject.toml` packages | Yes (`src/accounts`) |

### Import sites (external callers)

| File | Symbol |
|------|--------|
| `src/startup/first_run.py` | `accounts.sync.sync_providers_to_db` |
| `tests/test_accounts_sync.py` | `sync_providers_to_db`, `sync_auth_methods` |

### Module contents

| File | Purpose |
|------|---------|
| `manager.py` | `AccountManager` — singleton managing API provider credential entries |
| `models.py` | `AccountEntry` — Pydantic model for account metadata |
| `registry.py` | Low-level credential registry |
| `sync.py` | `sync_providers_to_db` / `sync_auth_methods` — syncs account data to DB on startup |

### Test files

| File | Tests | Status |
|------|-------|--------|
| `tests/test_accounts_sync.py` | 5 | ✅ Passing |

## Rationale

`src/accounts/` manages API provider credentials and is called during application first-run to synchronise credentials into the database. Its `sync_providers_to_db` function is invoked by the startup bootstrap path (`src/startup/first_run.py`), making it a critical initialisation dependency. All 5 tests pass. **No action taken — module is essential and must be kept.**

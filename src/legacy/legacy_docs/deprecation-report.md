# CyberSecSuite Deprecation Report

**Date:** 2026-04-27  
**Scope:** 5 source directories audited + 3 previously deleted modules  
**Outcome:** 0 of 5 audited directories deleted; 2 bugs fixed in `src/api/`; 3 directories confirmed already deleted

---

## 1. Executive Summary

A systematic deprecation audit was conducted across five `src/` directories: `a2a`, `agent`, `accounts`, `ai_proxy`, and `api`. Each directory was evaluated for external import coverage, test coverage, `pyproject.toml` registration, and ASGI mounting.

**All five audited modules are retained.** No module was deleted during this audit round. Two pre-existing bugs were discovered and fixed in `src/api/` (missing wheel registration and missing ASGI mounting). One pre-existing test-collection issue was noted in `src/a2a/` tests (missing `src/dashboard` dependency), flagged for Phase 13 follow-up.

Three directories (`src/ts_api/`, `src/agent_ts/`, `src/template_engine/`) had already been deleted prior to this audit and are documented in §5 for completeness.

---

## 2. Audit Summary Table

| Directory | Verdict | Reason | Import Count |
|---|---|---|---|
| `src/a2a/` | ✅ KEPT — Active | Core A2A orchestration layer; imported by ASGI proxy, MCP session handler, DB tool-seed loader, AI proxy, and agent runner/streaming stack | 8 |
| `src/agent/` | ✅ KEPT — Active | High-level Claude Agent SDK runner, session management, connection pooling, and hook pipeline; consumed by `src/a2a/` | 3 |
| `src/accounts/` | ✅ KEPT — Active | API provider credential management; called by startup bootstrap path (`src/startup/first_run.py`) | 2 |
| `src/ai_proxy/` | ✅ KEPT — Active | Core AI provider routing layer; 90+ import sites; exposes `/v1` proxy API, rate limiting, usage tracking, multi-provider routing | 90+ |
| `src/api/` | ✅ KEPT — Fixed | Worker management REST layer; missing `pyproject.toml` registration and ASGI mounting corrected; 141 tests passing | 5 |

---

## 3. Flagged for Phase 13

### 3.1 `src/a2a/` — Test collection errors (missing `src/dashboard`)

Two test files fail collection with a pre-existing `ModuleNotFoundError` for `src/dashboard`:

- `tests/test_agent_discovery.py` (3 tests) — ⚠️ collection error
- `tests/test_agent_streaming_backend.py` (4 tests) — ⚠️ collection error

**Action required:** Resolve or stub the `src/dashboard` dependency so these 7 tests can be collected and run cleanly.

### 3.2 `src/api/` — Production ASGI registration was missing

Both the `pyproject.toml` wheel entry and the ASGI mounting of the 5 worker routers were absent, meaning `/api/workers/*` routes returned 404 in production. These were fixed during the audit, but a smoke-test of the live worker API endpoints is recommended in Phase 13 to verify the mount is operating correctly end-to-end.

---

## 4. Per-Module Notes

### `src/a2a/`
- Implements the Google Agent-to-Agent (A2A) protocol.
- 23 tests in `test_a2a.py` pass; 7 tests in two other files blocked by missing `src/dashboard` (see §3.1).
- Listed in `pyproject.toml` under packages and description ("A2A agent orchestration").

### `src/agent/`
- Provides `AgentRunner`, `SessionManager`, `ClientPool`, hooks, `StreamingAdapter`, and `SessionLinking`.
- 11 tests in `tests/test_agent_sdk.py` — all passing.

### `src/accounts/`
- Manages `AccountEntry` credentials and syncs them to the DB via `sync_providers_to_db` / `sync_auth_methods`.
- 5 tests in `tests/test_accounts_sync.py` — all passing.

### `src/ai_proxy/`
- Exposes `cybersec-proxy` CLI entrypoint; mounted at `/v1` in `src/proxy/asgi.py`.
- 7 test files covering proxy behaviour, QoL controls, autopilot, scope middleware, and provider auth.

### `src/api/`
- 5 FastAPI routers: worker CRUD, lifecycle transitions, metrics, execution history, batch operations.
- **Fixes applied:**
  1. Added `"src/api"` to `[tool.hatch.build.targets.wheel].packages` in `pyproject.toml`.
  2. Created `_worker_api` FastAPI sub-app including all 5 routers and mounted it in `src/proxy/asgi.py`.
- 141 tests across 5 worker API test files — all passing.

---

## 5. Already Deleted (Prior to This Audit)

| Directory | Reason for Deletion |
|---|---|
| `src/ts_api/` | Dead Express.js backend — no Python callers, no active use |
| `src/agent_ts/` | Claude Code hooks — never integrated into the application |
| `src/template_engine/` | Jinja2 template engine removal |

---

## 6. Reference Docs

| Audit Doc | Module |
|---|---|
| [`docs/deprecation-a2a.md`](deprecation-a2a.md) | `src/a2a/` |
| [`docs/deprecation-agent.md`](deprecation-agent.md) | `src/agent/` |
| [`docs/deprecation-accounts.md`](deprecation-accounts.md) | `src/accounts/` |
| [`docs/deprecation-ai-proxy.md`](deprecation-ai-proxy.md) | `src/ai_proxy/` |
| [`docs/deprecation-api.md`](deprecation-api.md) | `src/api/` |

# Deprecation Audit: `src/agent/`

**Verdict:** KEPT (ACTIVE)

**Audit date:** 2025-07-28

## Evidence

| Metric | Count |
|--------|-------|
| External import sites (non-agent source files) | 3 |
| Test files covering this module | 1 |
| Test functions | 11 |
| Listed in `pyproject.toml` packages | Yes (`src/agent`) |

### Import sites (external callers)

| File | Symbol |
|------|--------|
| `src/a2a/agent_sdk.py` | `agent.session_linking.resolve_sdk_id`, `agent.session_linking.create_linked_session` |
| `tests/test_agent_sdk.py` | `AgentRunner`, `SessionManager`, `SessionRecord`, hooks |

### Module contents

| File | Purpose |
|------|---------|
| `runner.py` | `AgentRunner` — high-level Claude Agent SDK query runner |
| `sessions.py` | `SessionManager` + `SessionRecord` — session lifecycle |
| `client_pool.py` | `ClientPool` / `get_pool` — shared httpx async client pool |
| `hooks.py` | `security_hook`, `audit_hook`, `ioc_hook`, `cost_hook` |
| `streaming.py` | `StreamingAdapter` — SSE streaming wrapper |
| `session_linking.py` | `resolve_sdk_id` / `create_linked_session` — links agent runs to DB sessions |
| `options_manager.py` | Agent options builder |

### Test files

| File | Tests | Status |
|------|-------|--------|
| `tests/test_agent_sdk.py` | 11 | ✅ Passing |

## Rationale

`src/agent/` provides the high-level runner, session management, connection pooling, and hook pipeline that wraps the Claude Agent SDK. It is consumed by `src/a2a/agent_sdk.py` for session linking and by the test suite. All 11 tests pass. **No action taken — module is essential and must be kept.**

# ts_api Analysis

## Summary

**DELETE** — `src/ts_api/` is dead code: no active service calls its routes, the
dashboard layer that was meant to proxy traffic to it (`src/dashboard/`) no longer
exists, and the React `SdkLabPanel` was refactored to use the Python a2a SDK instead.

---

## Architecture Overview

```
Intended (at commit 163e2f24):
  Browser → React SdkLabPanel → /ts/* (Vite proxy) → ts_api :8765 → Anthropic API

Actual (current HEAD):
  Browser → React SdkLabPanel → /api/agent-query (Vite proxy) → Python a2a layer → Anthropic API
                                                                    (port 8765 unreachable;
                                                                     no caller reaches ts_api)
```

The Vite dev-server still declares a `/ts` proxy target (`http://localhost:8765`),
but no React component or Python service ever issues a request to that path.

---

## Findings

### Is ts_api Used by Frontend?

**Zero active references.** Exhaustive search of `src/frontend/src/`:

```
grep -rn "/ts/stream\|/ts/tools\|/ts/structured\|/ts/thinking\|/ts/memory\|8765" \
     src/frontend/src/ --include="*.ts" --include="*.tsx"
# → (no output)
```

`src/frontend/vite.config.ts` has the proxy stanza:

```ts
'/ts': process.env.BACKEND_URL ?? 'http://localhost:8765',
```

…but this is a leftover from the original design. The component that was supposed
to call these routes, `SdkLabPanel.tsx`, was later refactored:

```ts
// SdkLabPanel.tsx — current code
const res = await fetchApi<unknown>('/api/agent-query', { ... })
// ↑ Python google_a2a endpoint, not /ts/* at all
```

### Git History

| SHA | Date | Message |
|-----|------|---------|
| `163e2f24` | 2026-04-20 | `feat: TypeScript SDK API server + SDK Lab dashboard panel` |

ts_api was added in **a single commit** that also added:
- `src/dashboard/api/ts_proxy.py` — an httpx reverse-proxy to port 8765
- `src/dashboard/routes.py` — `Mount('/ts', ts_api_proxy)`
- `src/dashboard/static/ts/sdk_panel.ts` — a Vanilla-JS panel calling the ts routes

None of those dashboard files exist today (`src/dashboard/` was removed entirely).
The React `SdkLabPanel` is a re-implementation that bypasses ts_api.

### Integration Tests

**None.** `tests/` contains only Python files (`test_telemetry.py`, etc.).
There are no TypeScript/Jest tests targeting any `8765` or `/ts/*` endpoint.

```
find tests/ -name "*.ts" -o -name "*ts_api*"
grep -r "ts_api\|8765\|ts/stream" tests/ -l
# → (no output)
```

### ts_api Dependencies

`src/ts_api/package.json`:

| Package | Version | Purpose |
|---------|---------|---------|
| `@anthropic-ai/sdk` | ^0.90.0 | Direct Anthropic calls |
| `express` | ^4.21.0 | HTTP server |
| `zod` | ^3.24.0 | Structured output schemas |
| `cors` | ^2.8.5 | CORS headers |

All five routes (`stream`, `tools`, `structured`, `thinking`, `memory`) call
Anthropic directly using `ANTHROPIC_API_KEY` / `ANTHROPIC_BASE_URL`. **This
duplicates** the Python a2a layer (`src/a2a/agent_sdk.py`) which is the live
path used by the frontend today.

---

## Decision: DELETE

### Rationale

- **No caller exists.** The React frontend makes zero requests to `/ts/*` or
  port 8765. The Python backend makes zero requests to port 8765. The Vite proxy
  entry and the Makefile targets are stubs with no traffic.
- **The original consumer is gone.** `src/dashboard/` (the only planned caller)
  was removed in a subsequent refactor; the replacement `SdkLabPanel.tsx` routes
  through Python a2a instead.
- **Functionality is duplicated.** All capabilities (streaming, tool-use,
  structured output, extended thinking, memory) are already available via the
  Python a2a SDK layer that the frontend actively uses.
- **Single-commit provenance.** ts_api was added and immediately orphaned in one
  commit; there has been no follow-up integration work.

### Impact Assessment

| Concern | Risk |
|---------|------|
| Breaking a frontend feature | **None** — `SdkLabPanel` routes to Python, not ts_api |
| Breaking a Python service | **None** — no Python code references port 8765 |
| Losing unique capability | **None** — Python a2a layer provides equivalent SDK access |
| Removing Makefile targets (`ts-api-start`, `ts-api-dev`) | **Low** — internal dev convenience only |
| Removing Vite proxy entry for `/ts` | **Low** — proxy target is unreachable anyway |

---

## Action Plan

### DELETE (chosen path)

1. **Phase 13 deletion PR** — remove `src/ts_api/` directory entirely.
2. Remove the `/ts` proxy stanza from `src/frontend/vite.config.ts`.
3. Remove `ts-api-start` / `ts-api-dev` targets from `Makefile`.
4. Remove the `"127.0.0.1:8765:8000"` port mapping from `docker-compose.yml`
   (line 59).
5. Confirm `src/ts_api/server.ts` carries the deprecation comment (added now —
   see below) so any developer who clones an older branch is warned immediately.

### If reconsidering KEEP:

- Wire `ts-api-dev` into the `make dev` target alongside the frontend and Python
  backend.
- Add a `ts-api` service block to `docker-compose.yml` (currently only a stale
  port mapping exists; no service block is defined).
- Update `SdkLabPanel.tsx` to call `/ts/stream`, `/ts/tools`, etc. directly.
- Add integration tests under `tests/ts/` using `vitest` or `jest`.
- Document in `docs/setup.md`.

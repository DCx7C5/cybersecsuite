# QoL Output Controls — Phase 1 — 2026-04-22

_Last updated: 2026-04-22_

---

# QoL Output Controls — Phase 1 — 2026-04-22

Implemented server-side QoL output-control injection (plan.md T001–T015). Tool count: 83 → **87**.

## Changes

### New — `src/ai_proxy/qol_controls/` (package)

- `__init__.py` — exports `QoLToggle`, `QoLSettings`, `QoLManager`, `get_manager`
- `models.py` — `QoLToggle` enum (8 toggles), `QoLSettings` Pydantic v2 model, 5 builtin presets (`silent`, `code-only`, `structured`, `audit`, `plain-text`)
- `prompts.py` — 8 terse prompt fragments; `FILE_ONLY` contains required phrase "NOTHING ELSE MAY APPEAR"; `build_fragment_block()` cached and deterministic
- `manager.py` — `QoLManager` singleton: TTL-cached `build_injection`, `inject_into_request` (prepends to `system` key or inserts system message), `estimate_tokens`, telemetry emit via `record_event("qol.injection")`, per-scope save/load/reset, user preset CRUD

### Modified — `src/ai_proxy/routing/combo.py`

- Added `_qol_inject()` helper (lazy import, never raises)
- Called in `route_request()` after strategy resolution, before provider dispatch

### New — `src/csmcp/cybersec/qol_tools.py`

4 MCP tools: `qol_get`, `qol_set`, `qol_reset`, `qol_presets`

### Modified — `src/csmcp/cybersec/__init__.py`

- Imports and registers `qol_tools.ALL_TOOLS`; docstring tool count 83 → 87

### New — `src/dashboard/api/qol.py`

REST endpoints: `GET|POST|DELETE /api/qol`, `GET /api/qol/presets`, `POST /api/qol/presets/{name}`

### Modified — `src/dashboard/routes.py`

Wired 5 new `/api/qol/*` routes.

### New — `tests/test_qol.py`

27 tests (all passing): models, prompts, manager, MCP tools, combo injection hook.

### Updated docs / config

- `mcp.json` — description updated (83 → 87 tools)
- `CLAUDE.md` — tool counts updated; `qol_get/set/reset/presets` added to MCP table; `src/ai_proxy/qol_controls/` noted
- `docs/mcp/tools.md` — tool count 83 → 87; new QoL Output Controls section

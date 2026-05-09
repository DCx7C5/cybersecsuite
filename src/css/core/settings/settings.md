# @settings — Settings & Defaults Management

> **MOVED TO CORE**: Originally `modules/settings/`, now at `src/css/core/settings/`
> Reflects infrastructure nature of settings/cache configuration.

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

## Phase: 17 | Full plan in `.plan/plan.md` § Phase 17

---

## Purpose

DB-backed runtime configuration registry — sits on top of `config.py` (static env bootstrap) and provides:
- Live read/write of all settings via DB (no restart for most changes)
- Registry pattern: every setting is a registered `SettingDefinition` with type, default, description, scope, sensitivity flag
- Scoped settings: global → project-level overrides → session-level overrides
- Redis cache for hot settings (TTL = 3600s)
- REST API for frontend integration
- Named template profiles (development / red_team / blue_team / purple_team / minimal)

---

## Integration Points

| Component                      | Direction     | Relationship                                                              |
|--------------------------------|---------------|---------------------------------------------------------------------------|
| `css.core.types` (settings.py) | → consumes    | `SettingDefinition`, `SettingScope`, `SettingCategory`                    |
| `css.core.db`                  | → consumes    | `SettingRecord` ORM model (T17.1)                                         |
| `config.py`                    | → consumes    | Bootstrap values → seeded into DB on first startup                        |
| `@cache`                       | → consumes    | Redis for `css:settings:{scope}:{scope_id}:{key}` (CACHE_CONFIG_TTL=3600) |
| `@events` (Phase 14)           | → emits       | `settings.changed` event                                                  |
| `@projects`                    | ← consumed by | Project-level setting overrides                                           |
| Frontend                       | ← consumed by | REST endpoints `/api/settings/*`                                          |
| OTEL                           | → emits       | `@instrument("settings.get")` spans                                       |

### Phase 18 Frontend Note (2026-05-09)

- Colocated settings template surface now exists:
  - `src/css/core/settings/templates/index.tsx`
  - `src/css/core/settings/templates/hooks.ts`
  - `src/css/core/settings/templates/types.ts`
- This is scaffold-level wiring only. Full `frontend-settings-hooks` and `frontend-settings-panel` behavior remains blocked by `settings-rest-routes`.
- Navigation follow-up is tracked in `frontend-settings-nav-runtime`: settings navigation should be runtime-composed from `MenuItem(menu_id=\"settings\")` and aligned with the shared sidebar/topnav shell contract.

---

## File Layout

```
src/css/core/settings/
├── __init__.py
├── plan.md                     ← this file
├── registry.py                 ← SettingsRegistry class + SETTINGS_REGISTRY singleton
├── manager.py                  ← SettingsManager (get/set/reset/get_all/seed/export/import)
├── defaults.py                 ← DEFAULT_SETTINGS list (all config.py keys as SettingDefinitions)
├── routes.py                   ← REST endpoints (/api/settings/*)
├── profiles/                   ← YAML setting profiles (NOTE: not templates/ — that is reserved for React panel)
│   ├── development.yaml
│   ├── red_team.yaml
│   ├── blue_team.yaml
│   ├── purple_team.yaml
│   └── minimal.yaml
└── templates/                  ← React 19 panel (Phase 18)
    ├── index.tsx               ← default export: <SettingsPanel />
    ├── hooks.ts                ← TanStack Query hooks for /api/settings/*
    └── types.ts                ← TypeScript types matching SettingDefinition + API responses
```

---

## Key Design Decisions

### config.py is NOT replaced
`config.py` remains the env-var bootstrap (read on startup). It provides defaults for all `SettingDefinition.default` values. On first startup, `SettingsManager.seed_from_config_py()` writes these to the DB. After that, DB is the live source of truth. Critical infrastructure values (DB URL, secret keys) still respect env overrides at highest priority.

### Resolution Order (highest priority first)
1. Env override: `CSS_SETTING__<KEY_UPPER>` (e.g. `CSS_SETTING__LLM_ANTHROPIC_API_KEY`)
2. DB session-scope (scope_id = current session id)
3. DB project-scope (scope_id = project id)
4. DB global scope
5. `SettingDefinition.default` (from config.py bootstrap value)

### Registry Pattern (same as `@llm_models` ModelRegistry)
Settings are registered via `SettingsRegistry.register(definition)`. The registry validates types, enforces allowed scopes, and manages sensitivity flags.

### Sensitive settings
`sensitive=True` → never logged, returned as `"***"` in all REST GET responses, accepted for write. Includes: all API keys, passwords, SECRET_KEY, JWT_SECRET, ENCRYPTION_KEY.

---

## DB Schema (managed by T17.1)

```sql
settings(
  id UUID PK,
  key TEXT,                          -- dotted path: "llm.anthropic.api_key"
  value_json JSONB,                  -- any JSON-serializable value
  scope TEXT,                        -- 'global' | 'project' | 'session'
  scope_id TEXT,                     -- NULL for global, project_id or session_id otherwise
  category TEXT,                     -- 'llm' | 'cache' | 'system' | 'security' | etc.
  updated_at TIMESTAMPTZ,
  updated_by TEXT,                   -- agent_id or 'system'
  UNIQUE (key, scope, scope_id)
)
```

---

## REST API

| Method | Path                                 | Description                          |
|--------|--------------------------------------|--------------------------------------|
| GET    | `/api/settings/`                     | List all (sensitive masked)          |
| GET    | `/api/settings/categories/`          | List categories + setting counts     |
| GET    | `/api/settings/{key}`                | Single setting (masked if sensitive) |
| PUT    | `/api/settings/{key}`                | Update setting (type-validated)      |
| POST   | `/api/settings/{key}/reset`          | Reset to default                     |
| GET    | `/api/settings/export/`              | Export as YAML or JSON               |
| POST   | `/api/settings/import/`              | Import from YAML/JSON body           |
| GET    | `/api/settings/projects/{pid}/`      | Project-level overrides              |
| PUT    | `/api/settings/projects/{pid}/{key}` | Set project-level override           |

`requires_restart=True` settings: write succeeds, response includes `{"restart_required": true}`.

---

## Templates / Profiles

Pre-built profiles stored as YAML in `profiles/` (not `templates/` — that dir is reserved for the React panel). Applied with `SettingsManager.load_template("red_team")`. Each template overrides only the settings relevant to that mode — the rest resolve to global DB values.

- `development.yaml` — debug=true, log_level=DEBUG, cheap/fast models
- `red_team.yaml` — session_mode=red_team, full tool grants, aggressive timeouts
- `blue_team.yaml` — session_mode=blue_team, restricted outbound, defensive settings
- `purple_team.yaml` — session_mode=purple_team, hybrid
- `minimal.yaml` — local Ollama only, no external API calls, air-gapped mode

---

## Implementation Todos (Phase 17)

All synced in session.db. IDs match:

| Todo ID                       | Description                                            | Status  |
|-------------------------------|--------------------------------------------------------|---------|
| `settings-db-model`           | SettingRecord Tortoise ORM model                       | pending |
| `settings-db-migration`       | DB migration for settings table                        | pending |
| `settings-definition-struct`  | SettingDefinition + enums in core/types                | pending |
| `settings-registry-class`     | SettingsRegistry class                                 | pending |
| `settings-registry-singleton` | SETTINGS_REGISTRY singleton + DEFAULT_SETTINGS wire-up | pending |
| `settings-manager-core`       | SettingsManager get/set/reset/get_all                  | pending |
| `settings-manager-seed`       | seed_from_config_py() bootstrap                        | pending |
| `settings-manager-cache`      | Redis cache layer                                      | pending |
| `settings-manager-templates`  | load_template() + export/import YAML                   | pending |
| `settings-defaults-all`       | Complete DEFAULT_SETTINGS for all config.py keys       | pending |
| `settings-templates`          | 5 YAML template files                                  | pending |
| `settings-rest-routes`        | REST endpoints /api/settings/*                         | pending |
| `settings-event-emission`     | settings.changed event (BLOCKED: Phase 14)             | pending |

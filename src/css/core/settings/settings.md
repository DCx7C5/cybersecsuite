# @settings — Settings & Defaults Management

> **MOVED TO CORE**: Originally `modules/settings/`, now at `src/css/core/settings/`
> Reflects infrastructure nature of settings/cache configuration.

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This
document holds the executable specification for settings work. The current
documentation-movement pass intentionally does not mutate the tracker.

---

## Phase: 17 | Local Implementation Specification

Global navigation is in `.plan/plan.md`; query `.plan/session.db` for current
status when implementation begins.

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
├── settings.md                 ← this file
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

### Config ownership convergence (active)
Current repository state has overlapping config surfaces:
- `src/css/core/settings/config.py`
- `src/css/core/config.py`

Phase 17 now tracks consolidation so runtime configuration ownership is centralized under `core/settings`. The merged surface remains env-bootstrap first, then DB-backed runtime overrides via `SettingsManager`.

Source cleanup on 2026-05-25 repaired consumers that imported the nonexistent
`css.config` path so they use `css.core.settings.config`, and removed deleted
module registrations from `MODULES`. The separate `src/css/core/config.py`
surface still requires the tracked dual-source audit before removal.

### Provider bootstrap behavior (active)

Startup/provider seeding policy is now explicit:
- seed provider metadata from YAML only when provider table is empty
- if provider table is non-empty, skip destructive reseed and run non-destructive enrichment only
- provider and model bootstrap flows require explicit `Provider ↔ LLMModel` relation ownership before model upserts

### Resolution Order (highest priority first)
1. Env override: `CSS_SETTING__<KEY_UPPER>` (e.g. `CSS_SETTING__LLM_ANTHROPIC_API_KEY`)
2. DB session-scope (scope_id = current session id)
3. DB project-scope (scope_id = project id)
4. DB global scope
5. `SettingDefinition.default` (from config.py bootstrap value)

### Registry Pattern (same as `core/models` `ModelRegistry`)
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

The todo identifiers below map to the tracker; verify their live status in
`.plan/session.db` before implementation:

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
| `settings-config-dual-source-audit` | Audit overlap between `core/config.py` and `core/settings/config.py` | pending |
| `settings-config-merge-into-core-settings` | Merge both config sources into `core/settings` ownership | pending |
| `settings-config-import-cutover` | Cut runtime imports to consolidated settings config surface | pending |
| `orm-provider-llmmodel-relation` | Add Provider ↔ LLMModel relation contract for startup seeding | pending |
| `seed-providers-empty-table-yaml` | Auto-seed providers from YAML only when provider table is empty | pending |

## Executable Phase 17 Contract (2026-05-26)

### Exact File And Symbol Map

| Path | Current or planned symbols |
|------|----------------------------|
| `src/css/core/settings/config.py` | Current consolidated bootstrap configuration target. |
| `src/css/core/config.py` | Legacy overlapping surface to audit and reduce to compatibility only if still needed. |
| `src/css/core/settings/registry.py` | Planned `SettingsRegistry`, `SETTINGS_REGISTRY`. |
| `src/css/core/settings/manager.py` | Planned `SettingsManager.get()`, `set()`, `reset()`, `get_all()`, `seed_from_config_py()`. |
| `src/css/core/settings/defaults.py`, `src/css/core/settings/profiles/development.yaml`, `src/css/core/settings/profiles/red_team.yaml`, `src/css/core/settings/profiles/blue_team.yaml`, `src/css/core/settings/profiles/purple_team.yaml`, `src/css/core/settings/profiles/minimal.yaml` | Planned definitions and named profiles. |
| `src/css/core/settings/routes.py` | Planned `/api/settings/*` router. |
| `src/css/api_services/ai21/service.py`, `src/css/api_services/anthropic/service.py`, `src/css/api_services/cerebras/service.py`, `src/css/api_services/cloudflare/service.py`, `src/css/api_services/cohere/service.py`, `src/css/api_services/deepinfra/service.py`, `src/css/api_services/deepseek/service.py`, `src/css/api_services/fireworks/service.py`, `src/css/api_services/gemini/service.py`, `src/css/api_services/github/service.py`, `src/css/api_services/groq/service.py`, `src/css/api_services/huggingface/service.py`, `src/css/api_services/lambda_api/service.py`, `src/css/api_services/mistral/service.py`, `src/css/api_services/nscale/service.py`, `src/css/api_services/nvidia/service.py`, `src/css/api_services/ollama/service.py`, `src/css/api_services/openai/service.py`, `src/css/api_services/openrouter/service.py`, `src/css/api_services/perplexity/service.py`, `src/css/api_services/sambanova/service.py`, `src/css/api_services/together/service.py`, `src/css/api_services/xai/service.py` | Provider runtime import-cutover consumers. |
| `src/css/api_services/__init__.py`, `src/css/api_services/ollama/compat.py`, `src/css/api_services/opencode/service.py`, `src/css/core/marketplace/__init__.py`, `src/css/core/marketplace/cache.py`, `src/css/core/types/base_client.py` | Remaining runtime import-cutover consumers. |

### Sequencing And Import-Cutover Boundary

1. `settings-config-dual-source-audit` and
   `settings-config-merge-into-core-settings` establish the retained config
   surface before registry/manager/default/API work relies on it.
2. The 2026-05-25 cleanup repaired nonexistent `css.config` imports only. It
   did not complete `settings-config-import-cutover`: that pending todo must
   remove runtime imports from `css.core.config` in the explicit provider,
   marketplace, and base-client consumer list, leaving only a justified
   compatibility shim.
3. Implement definitions, persistence, manager/cache/profiles, routes, and
   event emission in dependency order; gate frontend settings work on the
   mounted REST routes.
4. Validate zero runtime `from css.core.config import` hits outside a retained
   shim, config/provider import smoke tests, secret masking, scope precedence,
   CRUD/profile routes, Redis invalidation, and settings-event behavior.

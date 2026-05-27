# core/marketplace — Catalog, Install State, and Package Control Plane

**Location**: `src/css/core/marketplace/`  
**Status**: Implemented control plane; prompt-link, SecureMD execution gate, and documentation mapping work remains pending

## Purpose

`core/marketplace` owns the **catalog and install lifecycle** for platform packages:
- agents
- skills
- prompts
- MCP server bundles/config entries
- future connector packages

It is **not** the runtime execution layer for MCP, tools, or SIEM integrations. It tracks what is available, installed, enabled, and described in metadata.

## Current Code Reality

| File | Reality |
|------|---------|
| `registry.py` | DB-backed `MarketplaceItemRegistry` around `MarketplaceItem` ORM rows |
| `endpoints.py` | Real FastAPI CRUD/install/toggle/list/detail routes plus Markdown preview display; preview is not trusted prompt ingestion. |
| `seeder.py` | Seeds built-in marketplace items, including `MarketplaceItemType.mcp` |
| `cache.py` | Local in-memory TTL cache, not Redis-backed |
| `installer.py` / `package_manager.py` | Package install/uninstall and local package orchestration |
| `types.py` | Request/response schemas |

## Executable Owner Contract

### Exact File And Symbol Map

| Path | Live symbols or planned edit boundary |
|------|---------------------------------------|
| `src/css/core/db/models/marketplace.py` | Canonical `MarketplaceItem`, `MarketplaceMeta`, `MarketplaceItemTag`, `MarketplaceItemManager`, `MarketplaceMetaManager` ORM/model surface. |
| `src/css/core/marketplace/registry.py` | `MarketplaceItemRegistry`, `wire_registry_events()`, `emit_marketplace_item_changed()`. |
| `src/css/core/marketplace/endpoints.py` | `list_marketplace_items()`, `get_marketplace_item()`, `install_item()`, `uninstall_item()`, `toggle_item()`, `marketplace_status()`, `get_marketplace_item_preview()`. |
| `src/css/core/marketplace/seeder.py` | `MarketplaceSeeder`, `seed_marketplace_on_startup()`. |
| `src/css/core/marketplace/types.py` | `MarketplaceItemCreate`, `MarketplaceItemResponse`, install/toggle/upgrade response structs. |
| `src/css/core/db/models/menu.py` | `DEFAULT_MENU_ITEMS`, `sync_default_menu_items()` for marketplace sidebar children. |

Phase 40 consolidation retained the rich ORM symbols above in
`src/css/core/db/models/marketplace.py`; future marketplace work must not
restore a competing catalog model file.

### Live Todo Map

| Todo ID | Status in `session.db` | Contract owned here |
|---------|------------------------|---------------------|
| `db40-lane-marketplace` | done | Canonical model reconciliation retained `MarketplaceItem`, `MarketplaceMeta`, `MarketplaceItemTag`, and their managers. |
| `db40-menu-marketplace-children-contract` | done | Seven stable sidebar children are seeded by `core/db/models/menu.py`. |
| `prompt-marketplace-wire` | pending | Link catalog prompt entries to prompt definitions without moving prompt content ownership into marketplace. |
| `securemd44-context-ingestion-gate` | pending | Require verified marketplace-origin prompt Markdown before prompt/agent execution; preserve preview as display-only. |
| `dep-map-modules-marketplace` | pending | Verify API, registry, seeder, ORM, templates, menu, MCP, and prompt relationships. |
| `market42-catalog-extensions` | pending | Extend marketplace metadata/types so ACP/LSP artifacts can be cataloged, versioned, and filtered. |
| `market42-manifest-seeding` | pending | Seed curated ACP/LSP manifests with version and prerequisite metadata in idempotent startup flow. |
| `market42-installer-runtime-hooks` | pending | Wire install/upgrade/remove hooks to ACP/LSP runtime configuration and cleanup boundaries. |
| `market42-frontend-workflows` | pending | Implement ACP/LSP marketplace discovery/install/configure/update UX flows aligned with sidebar-child contracts. |
| `market42-e2e-validation` | pending | Add end-to-end lifecycle validation for ACP/LSP marketplace operations and runtime binding integrity. |

### Numbered Execution And Validation

1. The completed `db40-menu-marketplace-children-contract` retains the menu
   seed/upsert contract; the ordered child labels are `Agents`,
   `Skills`, `MCPs`, `Workflows`, `Templates`, `Prompts`, and `Teams`.
   - Routes follow pattern: `/marketplace?kind={kind}` where kind is one of:
     `agent`, `skill`, `mcp`, `workflow`, `template`, `prompt`, `team`.
   - Old entries (`Installed`, nested `Marketplace` tab) are removed on sync runs.
   - Seed is idempotent: reruns upsert by identity key instead of duplicating.
2. For `prompt-marketplace-wire`, consume the existing
   `MarketplaceItemType.prompt` catalog kind and keep prompt versions and
   rendered content in the prompts owner.
3. For `securemd44-context-ingestion-gate`, keep
   `get_marketplace_item_preview()` display-only; verification is required
   when marketplace-origin Markdown enters prompt rendering or agent context.
4. For `dep-map-modules-marketplace`, inspect imports, mounted routes,
   registry event wiring, template bridge, and tracker state before changing
   integration prose.
5. Validate menu synchronization with `python manage.py init-db` and an
   ordered-child query; validate prompt linking through marketplace/prompt API
   tests; validate dependency mapping with `rg` over the exact files above.

## Frontend Template Surface (Phase 18)

- Colocated template entrypoint: `src/css/core/marketplace/templates/index.tsx`
- Colocated hooks/types bridge:
  - `src/css/core/marketplace/templates/hooks.ts`
  - `src/css/core/marketplace/templates/types.ts`
- Runtime UI implementation currently lives in `src/frontend/src/panels/marketplace/` and is re-exported through the colocated template files above so the module-colocated contract stays intact.
- New ownership directive is tracked by `frontend-core-templates-home-cutover`: move implementation ownership toward `core/templates/marketplace/*` while leaving `src/frontend` as shell/bootstrap.
- Active redesign directives:
  - Marketplace kind navigation should come from sidebar children (agents, skills, MCPs, workflows, templates, prompts, teams).
  - In-panel side tabs for kind switching are planned for removal.
  - Installed vs catalog surfaces should be presented in one coherent, dense UI flow (not split into disconnected screens).

## Architectural Role

Marketplace sits between planning/distribution and runtime modules:

```text
Marketplace item/package metadata
        ↓ install / enable / disable
Runtime modules load configuration from DB
        ↓
mcps/ connects to MCP servers
tools/ exposes callable tool entries
siem/ consumes installed MCP connectors
```

## Boundaries

- `core/marketplace` owns package metadata, status, install state, and seed data.
- `modules/mcps` owns MCP runtime config, connections, discovery, and tool calls.
- `modules/tools` owns provider builtin tool metadata plus the shared execution registry surface.
- `modules/siem` will consume installed MCP-backed connector packages, but does not own the marketplace.
- Navigation hierarchy (URL/path/breadcrumb) remains owned by `core/menu` via
  `MenuItem` (`BaseTreeModel`), not marketplace ORM rows.

## Known Drift / Planned Cleanup

- `MarketplaceItemRegistry` currently performs DB CRUD directly. Phase 9 will split this into:
  - a pure cache/registry contract
  - a DB-writing service layer
- ORM source was split between `marketplace_catalog.py` and `marketplace.py`. Phase 40 consolidated into `marketplace.py` as the canonical surface; `marketplace_catalog.py` was removed.
- Sidebar children contract is tracked in `db40-menu-marketplace-children-contract` and consumed by Phase 18 marketplace navigation todos.
- Registry invalidation wiring now reacts to item-level change events (`marketplace.item.changed`) and supports targeted cache eviction + `reload()` from manager-backed DB reads.
- Registry surface is now read/cache focused (`get`, `list`, `invalidate`, `reload`) with no DB write operations.
- Registry list filtering now happens through read-side predicates/service filters instead of ad-hoc CRUD helpers.
- The local cache is process memory today. Redis remains optional future infrastructure, not current behavior.
- Frontend refinement now targets shadcn-admin pattern reuse (`frontend-marketplace-ux-refine`) while keeping module-colocated `templates/` contract.

## Practical Rule

If a feature asks **“what packages/connectors are available or installed?”**, it belongs here.  
If it asks **“connect to this MCP server and call its tool”**, it belongs in `modules/mcps`.

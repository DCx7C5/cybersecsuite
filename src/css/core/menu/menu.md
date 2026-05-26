# core/menu — Runtime Navigation Composition

**Location**: `src/css/core/menu/`  
**Status**: 🟡 Active schema/runtime refinement in Phase 40 (`T40.2 Menu + Tree Modeling`)

## Purpose

`core/menu` owns runtime navigation composition APIs backed by `MenuItem` in `core/db/models/menu.py`.

- Sidebar items (`menu_id="sidebar"`)
- Settings navigation items (`menu_id="settings"`)
- Top navigation items (`menu_id="topnav"`)

## Current Surface

| File | Responsibility |
|------|----------------|
| `endpoints.py` | `/api/menu/items` endpoint with optional `?menu_id=` filter (sidebar/settings/topnav) |
| `../db/models/menu.py` | `MenuItem` ORM model, `sync_default_menu_items()`, tree helpers, breadcrumb helper |

## Runtime API Surface (`db40-menu-menuid-endpoints`)

### Endpoint: `/api/menu/items`

Query parameters:
- **`menu_id`** (optional): Filter results to one partition
  - Valid values: `sidebar`, `settings`, `topnav`
  - Missing or empty: returns all roots (all partitions, unfiltered)
  - Invalid value: returns HTTP 400 with error message

Examples:
- `GET /api/menu/items?menu_id=sidebar` — Returns only sidebar root(s) and their children
- `GET /api/menu/items?menu_id=settings` — Returns only settings root(s) and their children
- `GET /api/menu/items?menu_id=topnav` — Returns only topnav root(s) and their children
- `GET /api/menu/items` — Returns all roots from all partitions (fallback behavior)
- `GET /api/menu/items?menu_id=bogus` — Returns 400 Bad Request

Response: `{ "items": [ { id, parent_id, menu_id, name, url, icon_path, icon_url, order, children: [...] } ] }`

Serialization preserves `menu_id` on every node and never mixes children from different partitions than the requested root set.

## Phase 40 Work Queue (session.db)

- `db40-menu-sidebar-contract`
- `db40-menu-marketplace-children-contract`
- `db40-menu-menuid-upsert`
- `db40-menu-menuid-endpoints`
- `db40-menu-tree-constraints`
- `db40-basetree-candidate-inventory` (navigation-first tree candidates)

### Active execution snapshot (2026-05-09)

- `db40-menu-sidebar-contract` is now **done**.
- `db40-menu-menuid-upsert` is now **done**.
- `db40-lane-menu-tree` lane claim is complete and unblocked follow-up work is focused on:
  - `db40-menu-menuid-endpoints`
  - `db40-menu-marketplace-children-contract`
  - `db40-menu-tree-constraints`

## Rules

- Navigation hierarchy concerns (URL/path/breadcrumb trees) belong here.
- Tagging remains classification-first and is not a default substitute for navigation trees.
- Sidebar/settings/topnav should be feature-rich but not bloated, and backed by runtime menu data.
- Marketplace sidebar must expose child routes (agents, skills, MCPs, workflows, templates, prompts, teams) with deterministic ordering.
- Marketplace kind tabs inside the panel are planned for removal; sidebar child navigation + URL state is the canonical path.

## Validation Requirements

- Validate `menu_id` partition filtering for sidebar, settings, and topnav.
- Validate deterministic child ordering and no self-parent/cross-menu parent
  relationships.
- Validate the seeded Marketplace child routes are idempotent.

## BaseTreeModel candidate inventory (`db40-basetree-candidate-inventory`)

| Candidate surface | Current shape | Decision |
|-------------------|---------------|----------|
| `core/db/models/menu.py::MenuItem` | Already extends `BaseTreeModel`; owns `parent_id`, ordered children, and `breadcrumb()` helpers. | Keep as canonical navigation tree owner. |
| `core/marketplace/*` catalog records | Catalog/install metadata only; no navigation tree lifecycle. | Keep non-tree ORM; consume sidebar hierarchy from `MenuItem`. |
| `modules/tags/models.py::Tag` | Optional `parent_tag` hierarchy for classification metadata. | Keep in tagging lane scope; not promoted as navigation/breadcrumb tree owner. |

Inventory outcome: navigation URL/path/breadcrumb behavior remains menu-first,
with no additional `BaseTreeModel` adoption in this tranche.

Tag-adoption guardrail (`db40-basetree-tag-adoption-plan`):
1. Keep `Tag` on `BaseModel` by default while tag hierarchy is classification metadata.
2. Re-evaluate only if tagging explicitly needs navigation semantics (URL/path/breadcrumb routing, ordered tree traversal, and menu-style integrity constraints).

## Menu contract baseline (db40-menu-sidebar-contract)

- `MenuItem.menu_id` is the partition key for runtime navigation composition.
- Canonical values:
  - `sidebar`
  - `settings`
  - `topnav`
- `menu_id` participates in deterministic ordering (`menu_id`, `parent_id`, `order`, `id`) and read partitioning.

## menu_id upsert baseline (`db40-menu-menuid-upsert`)

- `sync_default_menu_items()` now upserts with the identity key
  (`menu_id`, `parent_id`, `name`) so partitions are deterministic.
- Seed data is explicit per partition (`sidebar`, `settings`, `topnav`) while
  current default endpoint behavior keeps returning sidebar roots.
- Root ordering and child upserts are stable under
  (`menu_id`, `parent_id`, `order`, `id`) ordering.

## Marketplace sidebar children contract (`db40-menu-marketplace-children-contract`)

The `Marketplace` root under the sidebar exposes exactly **7 deterministic children**
as the canonical kind navigation surface, replacing former tab-based internal navigation:

1. **Agents** → `/marketplace?kind=agent`
2. **Skills** → `/marketplace?kind=skill`
3. **MCPs** → `/marketplace?kind=mcp`
4. **Workflows** → `/marketplace?kind=workflow`
5. **Templates** → `/marketplace?kind=template`
6. **Prompts** → `/marketplace?kind=prompt`
7. **Teams** → `/marketplace?kind=team`

Implementation details:
- Old contract entries (`Installed`, nested `Marketplace` tab) are cleaned up on
  `sync_default_menu_items()` runs and removed from the DB to prevent duplication.
- Reruns upsert existing children by identity (`menu_id`, `parent_id`, `name`),
  so ordering and URLs are kept in sync deterministically.
- Frontend navigation tabs for kind switching are planned for removal; sidebar
  child routes are the source of truth for marketplace kind filtering.

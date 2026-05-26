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
| `endpoints.py` | `/api/menu/items` read surface (currently uses seeded/upserted `MenuItem` tree) |
| `../db/models/menu.py` | `MenuItem` ORM model, `sync_default_menu_items()`, tree helpers, breadcrumb helper |

## Phase 40 Work Queue (session.db)

- `db40-menu-sidebar-contract`
- `db40-menu-marketplace-children-contract`
- `db40-menu-menuid-upsert`
- `db40-menu-menuid-endpoints`
- `db40-menu-tree-constraints`
- `db40-basetree-candidate-inventory` (navigation-first tree candidates)

### Active execution snapshot (2026-05-09)

- `db40-menu-sidebar-contract` is now **done**.
- `db40-lane-menu-tree` lane claim is complete and unblocked follow-up work is focused on:
  - `db40-menu-menuid-upsert`
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

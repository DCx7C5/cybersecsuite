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
- `db40-menu-menuid-upsert`
- `db40-menu-menuid-endpoints`
- `db40-menu-tree-constraints`
- `db40-basetree-candidate-inventory` (navigation-first tree candidates)

## Rules

- Navigation hierarchy concerns (URL/path/breadcrumb trees) belong here.
- Tagging remains classification-first and is not a default substitute for navigation trees.
- Sidebar/settings/topnav should be feature-rich but not bloated, and backed by runtime menu data.

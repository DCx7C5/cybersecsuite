# core/templates — Frontend Ownership Surface

**Status**: 🟡 Active migration target | **Phase**: 18 (Frontend Foundation)

## Purpose

`src/css/core/templates/` is the canonical home for core frontend implementation surfaces.

- `src/frontend/` remains the runtime shell/bootstrap (router boot, bundler, providers).
- Feature/panel implementation should live under `core/templates/*` paths.
- Current high-priority target: marketplace/chat/dashboard/settings surfaces under template ownership.

## Active Directives

- Move frontend implementation ownership to template-localized files:
  - `core/templates/marketplace/*`
  - `core/templates/chat/*`
  - `core/templates/dashboard/*`
  - `core/templates/settings/*`
- Keep colocated module contracts intact while consolidating UI logic.
- Preserve import-order and runtime wiring discipline from `core/settings/config.py` module order rules.

## session.db Mapping

- `frontend-core-templates-home-cutover`
- `frontend-marketplace-installed-catalog-layout`
- `frontend-chat-thinking-task-visuals`
- `frontend-dashboard-tiles-workspace`

## Dependencies

- `src/frontend/` runtime shell
- `src/css/core/settings/`
- `src/css/core/menu/`
- `src/css/core/marketplace/`
- `src/css/modules/chat/`

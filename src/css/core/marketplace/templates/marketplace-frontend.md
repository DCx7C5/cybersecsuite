# Marketplace Templates Submodule

**Status**: 🟢 Active | **Area**: Marketplace API + frontend panel integration

## Purpose
Template-facing frontend bridge for marketplace browsing and management in the new React shell.

## Current Surface
- Canonical API base: `/marketplace/`
- Health/status: `/marketplace/status`
- Item listing: `/marketplace/items?page=1&per_page=20`
- Tag filter: `/marketplace/items/by-tags?tags=<tag>`
- Installation actions: `/marketplace/items/install`, `/marketplace/items/uninstall`

## Notes
- Frontend marketplace panel consumes `/marketplace/*` directly through the Vite proxy (`/marketplace` → backend target).
- When DB-backed marketplace models are unavailable, endpoints return index-backed fallback payloads so the UI remains usable.

## Dependencies
- `src/css/core/marketplace/`
- `src/frontend/src/panels/marketplace/`

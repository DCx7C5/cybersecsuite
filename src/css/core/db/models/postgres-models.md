# Core DB Models Submodule

**Status**: ✅ Active | **Phase**: 3/4 (Core Consistency)

## Purpose
Tortoise ORM models for all core infrastructure (teams, orchestrators, quotas, etc.).

## Files
- Multiple model files (team.py, orchestrator.py, quotas.py, etc.)

## TODOs
- [x] `db-add-taskassignment-updated-at` — Add `updated_at` to `TaskAssignment` (completed 2026-05-07)
- [ ] `db-fix-teamquota-reset-at` — Fix `TeamQuota.daily_reset_at` to nullable
- [ ] `db-soft-delete-mixin` — Add `SoftDeleteMixin` and apply to soft-delete models
- [ ] `orm-custom-managers` — Add custom Tortoise managers for Ring 2 query logic
- [ ] `orm-to-from-domain` — Add `to_domain()` / `from_domain()` bridges for ORM models

## Dependencies
- `src/css/core/db/`

**Last Updated**: 2026-05-07

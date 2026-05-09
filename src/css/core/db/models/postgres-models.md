# Core DB Models Submodule

**Status**: ✅ Active | **Phase**: 3/4 (Core Consistency)

## Purpose
Tortoise ORM models for all core infrastructure (teams, orchestrators, quotas, etc.).

## Files
- Multiple model files (team.py, orchestrator.py, quotas.py, etc.)

## TODOs
- [x] `db-add-taskassignment-updated-at` — Add `updated_at` to `TaskAssignment` (completed 2026-05-07)
- [x] `db-fix-teamquota-reset-at` — Fix `TeamQuota.daily_reset_at` to nullable
- [x] `db-soft-delete-mixin` — Add `SoftDeleteMixin` and apply to soft-delete models
- [x] `db-timestamp-mixin-rollout` — Roll out `TimestampMixin` to standard audit-pair ORM models
- [x] `db-frontmatter-field-semantics` — Split identifier `NameField` from human display-label semantics

### Field Semantics Decision (2026-05-09)
- **`NameField`**: Identifier semantics — ASCII Python identifier, unique, for programmatic keys (tool names, scope keys, model codenames, usernames, marketplace slugs, mixin `name` fields).
- **`LabelField`**: Display-name semantics — human-readable CharField, no identifier/uniqueness constraint, for entity names shown to users (human names, project names, webhook labels, tag display names).
- **Semantic boundary**: Input validation/sanitization belongs at the application boundary, not in the ORM field layer. HTML safety belongs at the output/render boundary.
- **Correct `NameField` usages**: `Account.username`, `LLMModel.name`, `MarketplaceItem.name`, `AppScope.name`, `ProjectScope.name`, `Organization.name`, `HybridToolDefinition.name`, `BaseFrontmatterMixin.name`
- **Migrated to `LabelField`**: `UserProfile.first_name`, `UserProfile.last_name`, `ProjectFile.name`, `Project.name`, `Tag.name`, `WebhookEndpoint.name`
- **Migrated to plain `CharField`**: `SessionScope.name` (default="", not an identifier), `SessionScope.phase` (not a name field)
- [x] `db-frontmatter-base-rollout` — Remove `BaseFBSModel`; `BaseFrontmatterMixin` kept for opt-in use by future identifier-style models
- [x] `db-version-mixin-rollout` — Audit complete: no model is an exact fit for `VersionMixin` without renaming. `BaseMarketPlace` has the contract but with domain-specific names (`remote_index_hash`/`local_index_hash`). Mixin kept for future opt-in use.
- [x] `orm-custom-managers` — Add custom Tortoise managers for Ring 2 query logic
- [x] `orm-to-from-domain` — Add `to_domain()` / `from_domain()` bridges for ORM models

### Recent Work (2026-05-09)
- Inline manager rollout is now reflected directly in the ORM files for `llm_models`, `scope`, `team`, `user`, `orchestrator`, `permissions`, `events`, and `marketplace`.
- `LLMModel` and scope/session records now carry richer domain conversion and lifecycle/query helpers instead of thin field-only declarations.
- Tree-model behavior remains in `BaseTreeModel`, but the concrete self-FK now lives in `menu.py` so the package imports cleanly under the current Tortoise version.

### Active Pending DB Consolidation (Phase 40 + Phase 17 startup seeding)
- `db40-provider-model-cutover` + `db40-user-vs-account-boundary` — finalize provider/account/user ownership boundaries.
- `orm-provider-llmmodel-relation` — explicit Provider ↔ LLMModel relation contract for startup seeding and query flows.
- `seed-providers-empty-table-yaml` — provider table cardinality gate (seed only when empty, otherwise non-destructive enrich).
- `db40-menu-sidebar-contract` + `db40-menu-menuid-upsert` + `db40-menu-menuid-endpoints` — runtime menu partitioning (`sidebar`, `settings`, `topnav`) and deterministic sidebar children.
- `db40-tag-junction-naming-standard` + `db40-model-meta-standardization` — singular class/table/meta conventions for rich junction models.

## Dependencies
- `src/css/core/db/`

**Last Updated**: 2026-05-09

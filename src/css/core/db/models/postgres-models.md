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
- [ ] `db-timestamp-mixin-rollout` — Roll out `TimestampMixin` to standard audit-pair ORM models
- [x] `db-frontmatter-field-semantics` — Split identifier `NameField` from human display-label semantics

### Field Semantics Decision (2026-05-09)
- **`NameField`**: Identifier semantics — ASCII Python identifier, unique, for programmatic keys (tool names, scope keys, model codenames, usernames, marketplace slugs, mixin `name` fields).
- **`LabelField`**: Display-name semantics — human-readable CharField, no identifier/uniqueness constraint, for entity names shown to users (human names, project names, webhook labels, tag display names).
- **Semantic boundary**: Input validation/sanitization belongs at the application boundary, not in the ORM field layer. HTML safety belongs at the output/render boundary.
- **Correct `NameField` usages**: `Account.username`, `LLMModel.name`, `MarketplaceItem.name`, `AppScope.name`, `ProjectScope.name`, `Organization.name`, `HybridToolDefinition.name`, `BaseFrontmatterMixin.name`
- **Migrated to `LabelField`**: `UserProfile.first_name`, `UserProfile.last_name`, `ProjectFile.name`, `Project.name`, `Tag.name`, `WebhookEndpoint.name`
- **Migrated to plain `CharField`**: `SessionScope.name` (default="", not an identifier), `SessionScope.phase` (not a name field)
- [x] `db-frontmatter-base-rollout` — Remove `BaseFBSModel`; `BaseFrontmatterMixin` kept for opt-in use by future identifier-style models
- [ ] `db-version-mixin-rollout` — Roll out `VersionMixin` to versioned/synced artifact models
- [ ] `orm-custom-managers` — Add custom Tortoise managers for Ring 2 query logic
- [ ] `orm-to-from-domain` — Add `to_domain()` / `from_domain()` bridges for ORM models

## Dependencies
- `src/css/core/db/`

**Last Updated**: 2026-05-09

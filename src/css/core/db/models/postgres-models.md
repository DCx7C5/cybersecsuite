# Core DB Models Submodule

**Status**: Active model owner | **Current gate**: Phase 41 preparation before Phase 40 implementation resumes
**Tracker authority**: `.plan/session.db`; this document owns executable model
consolidation guidance for the database package.

## Purpose
Tortoise ORM models for all core infrastructure (teams, orchestrators, quotas, etc.).

## Files

| File | Primary model responsibility | Reconciliation focus |
|------|------------------------------|----------------------|
| `base.py`, `mixins.py`, `enums.py` | Shared model base, lifecycle/version/frontmatter mixins, database enums. | Apply semantic fields and enum rules consistently. |
| `accounts.py`, `user.py`, `provider.py` | Account/organization, internal user/admin, external provider identity. | Preserve the explicit user vs provider-account boundary. |
| `llm_models.py` | Model metadata, pricing/capability persistence and query helpers. | Establish provider relationship before seeding/upsert work. |
| `marketplace.py` | Canonical marketplace model surface. `marketplace_catalog.py` removed in Phase 40. | No further reconciliation needed. |
| `memory.py` | Memory entry/snapshot persistence. | Phase 40 aligns consumers with the canonical surface. |
| `menu.py` | Navigation tree and `menu_id` partitioning. | Complete deterministic seed/filter/tree constraints. |
| `tasks.py`, `quotas.py` | Task results/assignments versus team quota storage. | Remove residual task ownership from quota paths. |
| `permissions.py`, `scope.py` | Existing permission/scope session records. | Reconcile with permissions redesign and unresolved scope/session replacement. |
| `events.py`, `orchestrator.py`, `team.py` | Event persistence and execution/team coordination. | Retain model/meta/index standards during audit remediation. |

### Active Phase 40 Symbol Surface

| Lane | Current symbols requiring deliberate consolidation |
|------|----------------------------------------------------|
| Marketplace | `BaseMarketPlace`, `MarketplaceMeta`, `MarketplaceMetaManager`, `MarketplaceItem`, `MarketplaceItemManager`, `MarketplaceItemTag`, and their `*Info` structs in `marketplace.py`. |
| Menu/tree | `MenuItem`, `MenuItemInfo`, `MenuItemManager`, `sync_default_menu_items` in `menu.py`. |

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

## Phase 40 Execution Contract

Phase 40 is ordered before Phase 9 in live tracker sort order.
`db40-lane-marketplace` and the menu tree/sidebar-contract rows are done; no
Phase 40 implementation row is active while the Phase 41 preparation gate is
being completed.

| Work lane | Required outcome |
|-----------|------------------|
| Memory | Audit imports, merge needed features into the canonical memory model, cut consumers over, then remove the legacy surface. |
| Marketplace | Audit both marketplace files, retain richer functionality in one canonical model, cut imports, remove the duplicate. |
| Task/provider/user | Move task ownership out of quota residuals; complete provider-model cutover; preserve internal user/admin versus provider-account separation. |
| Menu/tree | Use `MenuItem.menu_id` for `sidebar`, `settings`, and `topnav`; complete idempotent upsert, filtering, marketplace children, and integrity constraints. |
| Tagging/meta/fields | Define junction naming and model `Meta` standards before broad rollout; expand fields/mixins only where semantics match. |

## Model Rules Retained From Audit

| Rule | Implementation requirement |
|------|----------------------------|
| Primary keys | Use canonical `BaseModel`/`BigIntField` ownership for ORM table entities. |
| Enums | Replace closed-domain raw choices with canonical enums and `CharEnumField`. |
| Indexes | Use explicit Tortoise `Index(fields=[...])` declarations; validate expiry/status/time access paths and avoid tuple-style definitions. |
| Identity | `user.py` is internal user/admin identity; provider and provider-account surfaces remain external account relationships. |
| Seeds | Seed providers from canonical YAML only when the table is empty; enrich/upsert non-destructively after provider/model ownership is explicit. |
| Navigation | Startup upserts known routes deterministically and keeps partition/tree behavior in `menu.py`. |
| Schema policy | Phase 40 currently uses direct model/schema edits with no migration files; production migration/versioning is a later explicit decision. |

## Cross-Area Destinations

| Domain | Local owner |
|--------|-------------|
| Settings and projects | `core/settings/settings.md`, `modules/projects/projects.md` |
| Memory and hybrid retrieval | `core/memory/memory.md`, `core/rag_vector/rag_vector.md`, `core/rag_graph/rag_graph.md` |
| Reports and artifacts | `modules/reports/reports.md` |
| Auth/accounts | `core/auth/auth.md`, `core/accounts/accounts.md` |
| Menu/frontend composition | `core/menu/menu.md`, `core/templates/plan.md` |
| Telemetry streams | `core/otel/plan.md` |

## Dependencies
- `src/css/core/db/`

## Executable Phase 40 Addendum (2026-05-26)

### Exact Files And Symbols

| Path | Symbols / edit boundary |
|------|-------------------------|
| `src/css/core/db/models/memory.py` | `MemoryEntryRecord`, `MemorySnapshotRecord`; canonical memory persistence target. |
| `src/css/core/db/models/marketplace.py` | Retained `MarketplaceItem`, `MarketplaceMeta`, `MarketplaceItemTag` and managers; consolidated lane is done. |
| `src/css/core/db/models/tasks.py` and `src/css/core/db/models/quotas.py` | `TaskAssignment`, `TaskResult`, `TeamQuota`; task/quota ownership cutover. |
| `src/css/core/db/models/provider.py`, `src/css/core/db/models/user.py`, `src/css/core/db/models/accounts.py`, `src/css/core/db/models/llm_models.py` | Provider, internal user, account, and model boundaries. |
| `src/css/core/db/models/menu.py` | `MenuItem`, `MenuItemManager`, `sync_default_menu_items()`. |
| `src/css/core/menu/endpoints.py` | `list_menu_items(menu_id: str | None = None)` target for `db40-menu-menuid-endpoints`. |
| `src/css/core/db/models/base.py`, `src/css/core/db/models/mixins.py`, `src/css/core/db/fields/char_fields.py` | Model Meta/mixin/semantic-field standards. |

### Live Todo Map

| Todo group | Status | Ordered contract |
|------------|--------|------------------|
| `db40-lane-marketplace`, marketplace cutover/remove rows | done | Preserve the retained symbols in canonical `marketplace.py`. |
| `db40-memory-*`, `db40-lane-memory` | done | Canonical memory model ownership is reconciled; import cutover and snapshot payload contract are aligned. |
| `db40-taskmodel-import-cutover`, `db40-quotas-task-residual-cleanup`, `db40-provider-model-cutover`, `db40-user-vs-account-boundary`, `db40-lane-task-provider-user` | pending | Settle task/provider/user ownership without duplicate model classes. |
| `db40-menu-menuid-upsert`, `db40-menu-menuid-endpoints`, `db40-menu-tree-constraints`, `db40-menu-marketplace-children-contract` | pending | Partition and serialize navigation deterministically through `menu_id`. |
| `db40-lane-tagging` plus `db40-tag-junction-naming-standard`, `db40-tag-junction-meta-backfill`, `db40-tagging-db-concept`, `db40-llmmodel-tag-runtime-wire`, `db40-taggable-entity-inventory` | in_progress | Freeze tagging as classification/filter/search/policy metadata and keep it out of menu/tree/navigation ownership. |
| `db40-lane-platform-polish`, `db40-direct-schema-policy`, `db40-cache-md-reference-fix`, `db40-field-library-expansion`, `db40-mixins-expansion`, `db40-model-meta-standardization`, `db40-intelligence-home-plan`, `db40-pipeline-home-plan` | in_progress | Lane F reconciles field/mixin/Meta standards and runtime-home documentation across DB + core planning docs. |

### Lane E Tagging Scope, Order, and Write Surface

Tagging lane contract:
- Tagging is classification, filter, search, and policy metadata.
- Tagging is not navigation/menu/tree hierarchy ownership.

Lane E child todo order:
1. `db40-taggable-entity-inventory`
2. `db40-tag-junction-naming-standard`
3. `db40-tag-junction-meta-backfill`
4. `db40-tagging-db-concept`
5. `db40-llmmodel-tag-runtime-wire`

Lane E owned write surface:
- `src/css/modules/tags/*`
- `src/css/core/db/models/llm_models.py`
- `src/css/core/db/models/marketplace.py`
- `src/css/modules/tools/models.py`
- `src/css/core/tools/models.py`

Out-of-scope for Lane E: menu/tree routes and unrelated model cleanup.

### Lane F Child Scope And Ordered Dependencies

| Todo ID | Scope owner and boundary |
|---------|--------------------------|
| `db40-direct-schema-policy` | Keep `src/css/core/db/postgres-db.md` and this file aligned on the direct schema policy for Phase 40. |
| `db40-cache-md-reference-fix` | Normalize cache planning references to `src/css/core/cache/` and `src/css/core/prompt_cache/`. |
| `db40-field-library-expansion` | Expand semantic DB field helpers and expose canonical imports via `src/css/core/db/fields/`. |
| `db40-mixins-expansion` | Apply/standardize mixin contracts on DB models after the field-library expansion baseline. |
| `db40-model-meta-standardization` | Standardize model `Meta` conventions after tagging meta backfill is complete. |
| `db40-intelligence-home-plan` | Keep intelligence-owner planning in `src/css/modules/triage/` and retrieval owners. |
| `db40-pipeline-home-plan` | Keep runtime pipeline-owner planning centered on `src/css/core/pipeline.py`. |

Ordered constraints for Lane F work:
1. `db40-field-library-expansion` before `db40-mixins-expansion`.
2. `db40-tag-junction-meta-backfill` before `db40-model-meta-standardization`.
3. `db40-intelligence-home-plan` before `db40-pipeline-home-plan`.

Shared Phase 40 schema-change flow for DB ownership work:
1. Edit the ORM model directly.
2. Rebuild and reseed through `python manage.py init-db`.
3. Re-run read-side/import checks before closing TODO rows.

### Numbered Validation Contract

1. Complete one lane at a time against the exact files above and query
   `.plan/session.db` dependencies before changing schema ownership.
2. For `db40-menu-menuid-endpoints`, extend
   `src/css/core/menu/endpoints.py::list_menu_items()` with an optional
   `menu_id` filter for `sidebar`, `settings`, and `topnav`, preserving
   recursive `menu_id` values and rejecting invalid inputs.
3. Run model/import tests plus `python manage.py init-db`; exercise
   `/api/menu/items?menu_id=sidebar|settings|topnav` and invalid input; inspect
   canonical imports before deleting or deprecating any legacy model surface.

**Last Updated**: 2026-05-09

# core/db/models — Core ORM Schema Boundary

**Location**: `src/css/core/db/models/`
**Status**: Active model owner | **Current gate**: Phase 45 decision row blocked; planning only
**Tracker authority**: `.plan/session.db`; this document owns executable model
consolidation guidance for the database package.

## Purpose
Tortoise ORM models for all core infrastructure (teams, orchestrators, quotas, etc.).

## Files

| File | Primary model responsibility | Reconciliation focus |
|------|------------------------------|----------------------|
| `base.py`, `mixins.py`, `enums.py` | Shared model base, lifecycle/version/frontmatter mixins, database enums. | Apply semantic fields and enum rules consistently. |
| `accounts.py`, `user.py`, `provider.py` | Account/organization, internal user/admin, external provider identity. | Phase 45 defines the requested identity/profile and account/provider junctions after cardinality confirmation. |
| `llm_models.py` | Model metadata, pricing/capability persistence and query helpers. | Keep the provider slug field as a bridge; Provider↔LLMModel relation remains explicit deferred work. |
| `marketplace.py` | Canonical marketplace model surface. `marketplace_catalog.py` removed in Phase 40. | No further reconciliation needed. |
| `memory.py` | Memory entry/snapshot persistence. | Phase 40 aligns consumers with the canonical surface. |
| `menu.py` | Navigation tree and `menu_id` partitioning. | Complete deterministic seed/filter/tree constraints. |
| `machine.py` | Current infrastructure machine/endpoint record. | Phase 45 target retires this table after data-transition policy is confirmed and retained asset fields move to `Host`. |
| `host.py` | Current host/asset record with required `Machine` FK and scalar IP fields. | Phase 45 target promotes `Host` to the canonical asset and connects normalized addresses and paths. |
| `pathfs.py` | Filesystem path hierarchy with an existing direct `Host` FK. | Retain the relation; remove only the Machine-dependent seeding chain unless an explicit rename is approved. |
| `network.py`, `address.py` | Not present in current source. | Phase 45 planned owners for `Network`, `Address`, `HostAddress`, and `NetworkAddress`. |
| `../managers/` | New package scaffold is incomplete; model files still define manager classes. | Phase 45 moves query managers out of ORM modules with a cycle-safe import pattern. |
| `../../serializers/` | New package scaffold is incomplete; serializers still appear in model/feature files. | Phase 43 moves all serializer implementations out of ORM ownership. |
| `tasks.py`, `quotas.py` | Task results/assignments versus team quota storage. | Remove residual task ownership from quota paths. |
| `permissions.py`, `scope.py` | Existing permission/scope session records. | Reconcile with permissions redesign and unresolved scope/session replacement. |
| `events.py`, `orchestrator.py`, `team.py` | Event persistence and execution/team coordination. | Retain model/meta/index standards during audit remediation. |

### Current Source Snapshot And Follow-On Target

| Lane | Current symbols requiring deliberate consolidation |
|------|----------------------------------------------------|
| Marketplace | `BaseMarketPlace`, `MarketplaceMeta`, `MarketplaceMetaManager`, `MarketplaceItem`, `MarketplaceItemManager`, `MarketplaceItemTag`, and their `*Info` structs in `marketplace.py`. |
| Menu/tree | `MenuItem`, `MenuItemInfo`, `MenuItemManager`, `sync_default_menu_items` in `menu.py`. |
| Infrastructure baseline | `Machine`, `Host`, and `PathFS` currently exist; `Host.machine` and Machine-dependent host seeding remain live in source. |
| Phase 45 topology target | Retire `Machine`; use `Host` plus `PathFS`, `Address`, `HostAddress`, `Network`, and `NetworkAddress` as the traversable inventory graph. |
| Ownership relocation target | Managers live in `core/db/managers/<domain>.py`; serializers live in `core/serializers/<domain>.py`; ORM modules contain records/value types only. |

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

### Active Follow-On DB Work (Phase 17 + Phase 45)
- Phase 40 is complete in `.plan/session.db`; do not reinterpret its historical
  machine/host/path work as approval of the new topology target.
- `orm-provider-llmmodel-relation` — explicit Provider ↔ LLMModel relation contract for startup seeding and query flows.
- `seed-providers-empty-table-yaml` — provider table cardinality gate (seed only when empty, otherwise non-destructive enrich).
- `db45-schema-decision-gates` — blocked decision root for Machine transition,
  topology tenancy, identity/profile cardinality, provider connections, and
  `PathFS` naming.
- `db45-manager-package-relocation` — move manager implementations to
  `core/db/managers/` without changing query behavior.
- `db45-machine-retirement-host-promotion`, `db45-host-pathfs-chain`, and
  `db45-network-address-topology` — implement the asset/relation graph after
  the decision gate.
- `db45-identity-account-profile-schema` and
  `db45-account-provider-junction` — implement confirmed identity/provider
  associations without storing secrets in relation tables.

## Completed Phase 40 Baseline

Phase 40 is complete in live tracker state. It established the present
machine/host/path baseline and does not block recording a new schema target in
Phase 45.

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
| Meta schema | Use one `Meta` contract: `table`, `table_verbose`, `table_verbose_plural`, list-style `ordering`, list-style `indexes` with `Index(fields=[...])`, and `unique_together` only for real uniqueness constraints. |
| Indexes | Use explicit Tortoise `Index(fields=[...])` declarations; validate expiry/status/time access paths and avoid tuple-style definitions. |
| Identity | `user.py` is internal user/admin identity; provider and provider-account surfaces remain external account relationships. |
| Seeds | Seed providers from canonical YAML only when the table is empty; enrich/upsert non-destructively after provider/model ownership is explicit. |
| Navigation | Startup upserts known routes deterministically and keeps partition/tree behavior in `menu.py`. |
| Schema policy | Phase 40 used direct model/schema edits; Phase 45 must not assume rebuild versus migration until its decision gate is answered. |

### Canonical Meta Pattern (Phase 40)

Applied across `llm_models.py`, `scope.py`, `team.py`, `events.py`, and `marketplace.py`:

```python
class Meta:
    table = "concrete_table_name"
    table_verbose = "Concrete Model"
    table_verbose_plural = "Concrete Models"
    ordering = ["field_a", "field_b", "id"]
    indexes = [
        Index(fields=["field_a"]),
        Index(fields=["field_a", "field_b"]),
    ]
    unique_together = (("field_a", "field_b"),)
```

`unique_together` is included only when the row contract truly requires uniqueness.

## Phase 45 Executable Topology And Relation Contract (2026-05-27)

### Source-Backed Findings

| Finding | Implementation consequence |
|---------|----------------------------|
| `Host.machine` is required and `HostInfo` exposes `machine_id`. | `Machine` cannot be deleted until retained asset fields and seed behavior are transferred to `Host`. |
| `PathFS.host` already exists with unique `host_id` plus `path`. | Keep the direct host/path chain; only repair seed and ownership relocation unless a rename is approved. |
| `Host` stores `ipv4_address` and `ipv6_address` as scalars. | Normalize IP identity into `Address` and link through an explicit junction. |
| No `Network` or address junction model exists. | Add new ORM modules and register them in both CLI and ASGI Tortoise model lists. |
| `UserProfile.account` is a non-unique FK with singular `related_name="profile"`. | Confirm the desired identity/profile cardinality before modifying it. |
| `ApiServiceProvider` is catalog-only. | Add a connection junction to accounts; never store credential bytes on the junction. |

### Recommended Normalized Table Layout

This is the recommended baseline pending the decision questions below:

| Table / model | Required ownership and key relations |
|---------------|--------------------------------------|
| `host` / `Host` | Canonical system asset. Absorb retained `Machine` fields: `hostname`, `os_type`, `os_version`, `asset_uuid`, activity/last-seen and capacity fields. Keep `fqdn` and `host_role`. |
| `path_fs` / `PathFS` | Existing tree record. `host_id -> host.id`; preserve unique `(host_id, path)` and parent hierarchy. |
| `network` / `Network` | Named network boundary with canonical CIDR/prefix, family, label/description, and approved tenant owner. |
| `address` / `Address` | One canonical IPv4/IPv6 value plus family and optional display metadata; do not duplicate the same IP per host. |
| `host_address` / `HostAddress` | Junction `host_id -> host.id`, `address_id -> address.id`; carry interface, primary/role, and observation timestamps. |
| `network_address` / `NetworkAddress` | Junction `network_id -> network.id`, `address_id -> address.id`; supports overlapping/observed networks without copying address rows. |
| `user_account_membership` / `UserAccountMembership` | Only if confirmed: explicit M:N junction between internal `User` and tenant/login `Account`; carry role/status/audit fields, not credentials. |
| `account_provider_connection` / `AccountProviderConnection` | Explicit M:N association from `Account` to `ApiServiceProvider`; carry status, auth method, scope and encrypted-setting reference, never plaintext tokens. |

Required traversal contract:

```text
Host -> HostAddress -> Address -> NetworkAddress -> Network
Network -> NetworkAddress -> Address -> HostAddress -> Host
Host -> PathFS -> child PathFS
Account -> AccountProviderConnection -> ApiServiceProvider
```

### Open Decisions Blocking Implementation

The tracker row `db45-schema-decision-gates` remains `blocked` until these
answers are supplied:

1. `Machine` data transition: may development tables be rebuilt, or must
   existing `Machine` rows be migrated into `Host` without loss?
2. Topology tenancy: should `Host` and `Network` belong to `Organization`,
   `ProjectScope`, both through junctions, or remain global inventory?
3. Identity meaning: does “useraccount/profile many to many rel to accounts”
   mean `User <-> Account` is many-to-many while each `Account` has exactly
   one `UserProfile` (recommended), or must profiles themselves be shared?
4. Provider multiplicity: may one `Account` connect multiple credentials to
   the same `ApiServiceProvider`, requiring `connection_name` in uniqueness?
5. Naming: retain current `PathFS`/`path_fs`, or explicitly rename it to
   `FSPath` and its table as part of the schema change?

### Implementation Order

| Todo ID | Status | Concrete outcome |
|---------|--------|------------------|
| `db45-schema-decision-gates` | blocked | Capture the five decisions above before schema mutation. |
| `audit44-db-manager-import-cutover` | pending | Repair `BaseManager` package contract. |
| `db45-manager-package-relocation` | pending | Move all existing manager implementations to mirrored `core/db/managers/*.py` files. |
| `serializer-base-create`, `serializer-relocate-base` | pending | Establish canonical serializer bases and move serializer implementations to `core/serializers/*.py`. |
| `db45-machine-retirement-host-promotion` | pending | Delete the Machine owner only after `Host` carries retained asset data. |
| `db45-host-pathfs-chain`, `db45-network-address-topology` | pending | Preserve paths and add reversible address/network traversal. |
| `db45-identity-account-profile-schema`, `db45-account-provider-junction` | pending | Implement confirmed identity and provider associations. |
| `db45-model-registration-seeding`, `db45-schema-validation` | pending | Register modules, seed retained defaults, and verify complete relation chains. |

### Runtime Registration And Ownership Boundary

- Add `host.py`, `pathfs.py`, `network.py`, and `address.py` to model module
  enumeration in `src/css/manager.py` and `src/css/core/asgi/app.py`; remove
  `machine.py` only after the replacement is implementable.
- `core/db/models/*.py` owns ORM records and domain value types only.
- `core/db/managers/*.py` owns query manager implementations; manager modules
  must use cycle-safe model imports.
- `core/serializers/*.py` owns every serializer implementation; ORM files must
  not import serializer bases.
- Provider connection rows may reference encrypted secret storage, but actual
  provider tokens and API keys remain owned by `auth-secrets-settings`.

## Cross-Area Destinations

| Domain | Local owner |
|--------|-------------|
| Settings and projects | `core/settings/settings.md`, `modules/projects/projects.md` |
| Memory and hybrid retrieval | `core/memory/memory.md`, `core/rag_vector/rag_vector.md`, `core/rag_graph/rag_graph.md` |
| Reports and artifacts | `modules/reports/reports.md` |
| Auth/accounts | `core/authentication/authentication.md`, `core/accounts/accounts.md` |
| Structured serialization | `core/serializers/serializers.md` |
| Menu/frontend composition | `core/menu/menu.md`, `core/templates/plan.md` |
| Telemetry streams | `core/otel/plan.md` |

## Dependencies
- `src/css/core/db/`

## Historical Phase 40 Addendum (2026-05-26, Completed)

### Exact Files And Symbols

| Path | Symbols / edit boundary |
|------|-------------------------|
| `src/css/core/db/models/memory.py` | `MemoryEntryRecord`, `MemorySnapshotRecord`; canonical memory persistence target. |
| `src/css/core/db/models/marketplace.py` | Retained `MarketplaceItem`, `MarketplaceMeta`, `MarketplaceItemTag` and managers; consolidated lane is done. |
| `src/css/core/db/models/tasks.py` and `src/css/core/db/models/quotas.py` | `TaskAssignment`, `TaskResult`, `TeamQuota`; task/quota ownership cutover. |
| `src/css/core/db/models/provider.py`, `src/css/core/db/models/user.py`, `src/css/core/db/models/accounts.py`, `src/css/core/db/models/llm_models.py` | Provider, internal user, account, and model boundaries. |
| `src/css/core/db/models/menu.py` | `MenuItem`, `MenuItemManager`, `sync_default_menu_items()`. |
| `src/css/core/menu/endpoints.py` | `list_menu_items(menu_id: str | None = None)` target for `db40-menu-menuid-endpoints`. |
| `src/css/core/db/models/base.py`, `src/css/core/db/models/mixins.py`, `src/css/core/db/fields/{char,int,float,decimal,json}_fields.py` | Model Meta/mixin/semantic-field standards. |

### Live Todo Map

| Todo group | Status | Ordered contract |
|------------|--------|------------------|
| `db40-lane-marketplace`, marketplace cutover/remove rows | done | Preserve the retained symbols in canonical `marketplace.py`. |
| `db40-memory-*`, `db40-lane-memory` | done | Canonical memory model ownership is reconciled; import cutover and snapshot payload contract are aligned. |
| `db40-taskmodel-import-cutover`, `db40-quotas-task-residual-cleanup`, `db40-provider-model-cutover`, `db40-user-vs-account-boundary`, `db40-lane-task-provider-user` | done | Historical Lane C ownership map is complete; Phase 45 introduces follow-on identity/provider relations. |
| `db40-basetree-candidate-inventory` | done | Inventory confirmed navigation URL/path/breadcrumb tree ownership stays with `MenuItem` (`BaseTreeModel`) and no extra tree adoption is needed in this tranche. |
| `db40-basetree-tag-adoption-plan` | done | Evaluated `Tag.parent_tag` and kept it on `BaseModel`; no default `BaseTreeModel` adoption unless tagging later requires navigation semantics. |
| `db40-field-library-expansion` | done | Expanded semantic DB field helpers (`CurrencyCodeField`, non-negative/ratio numeric fields, JSON object/list wrappers) and wired them into `LLMModel`. |
| `db40-menu-menuid-upsert` | done | Seed/upsert flow now uses (`menu_id`, `parent_id`, `name`) identity and deterministic partition ordering. |
| `db40-menu-menuid-endpoints`, `db40-menu-tree-constraints`, `db40-menu-marketplace-children-contract` | done | Historical menu partition/tree implementation is complete. |
| `db40-lane-tagging` plus `db40-tag-junction-naming-standard`, `db40-tag-junction-meta-backfill`, `db40-tagging-db-concept`, `db40-llmmodel-tag-runtime-wire`, `db40-taggable-entity-inventory` | done | Historical tagging ownership is complete and remains outside Phase 45 topology. |
| `db40-intelligence-home-plan` | done | Verified triage ownership is module-local after facade removal and kept retrieval ownership in `core/rag_vector` + `core/rag_graph`. |
| `db40-lane-platform-polish`, `db40-mixins-expansion`, `db40-model-meta-standardization`, `db40-pipeline-home-plan` | done | Historical platform/model-meta baseline is complete. |

### Lane C Task/Provider/User Ownership Map

Lane C canonical ownership:
- `tasks.py`: `TaskAssignment`, `TaskResult`
- `quotas.py`: `TeamQuota` only
- `user.py`: internal user/admin runtime identity
- `accounts.py`: account/profile/organization tenancy records; Account owns identity
- `provider.py` + `llm_models.py`: provider and model catalog ownership
- deferred boundary: Provider↔LLMModel relation stays in `orm-provider-llmmodel-relation`
- `modules/tasks/models.py`: auto-discovery stub only; no module-local task ORM ownership
- boundary phrase retained: user/admin vs provider-account

Lane C child todo execution constraints:
1. `db40-taskmodel-import-cutover` before `db40-quotas-task-residual-cleanup`.
2. `db40-user-vs-account-boundary` before `db40-provider-model-cutover`.

Lane C owned write surface:
- `src/css/core/db/models/tasks.py`
- `src/css/core/db/models/quotas.py`
- `src/css/core/db/models/provider.py`
- `src/css/core/db/models/user.py`
- `src/css/core/db/models/accounts.py`
- `src/css/core/db/models/llm_models.py`
- `src/css/modules/tasks/endpoints.py`
- `src/css/modules/tasks/models.py`
- `src/css/core/accounts/accounts.md`

Out-of-scope for Lane C: menu/tree/tagging/model-meta cleanup outside the listed files.

### Lane D BaseTreeModel Candidate Inventory

Inventory result (`db40-basetree-candidate-inventory`):
- canonical owner remains `src/css/core/db/models/menu.py::MenuItem`
  (`BaseTreeModel`) for navigation URL/path/breadcrumb behavior.
- `src/css/modules/tags/models.py::Tag.parent_tag` stays tagging
  classification metadata and is not promoted to navigation-tree ownership.
- `src/css/core/marketplace/` remains catalog/install metadata and consumes
  menu tree output rather than introducing a second tree ORM owner.
- Tag-tree adoption is opt-in only: adopt `BaseTreeModel` for tags only when
  explicit URL/path/breadcrumb navigation semantics are introduced.

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
| `db40-field-library-expansion` | Expand semantic DB field helpers and expose canonical imports via `src/css/core/db/fields/` (char/int/float/decimal/json modules). |
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

**Last Updated**: 2026-05-27

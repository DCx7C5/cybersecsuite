# core/serializers — Canonical Serialization Boundary

**Location**: `src/css/core/serializers/`
**Status**: New canonical package scaffold; Phase 43 is reopened and pending.
**Tracker authority**: `.plan/session.db`; this document owns the executable serializer specification.

## Purpose

- Own public serializer base contracts and strict format-specific serializers.
- Own all ORM/domain serializer implementations extracted from model modules.
- Support database/domain bridges, menu/retrieval responses, and SecureMD
  frontmatter/Markdown parsing through one canonical package.
- Remove imports from the deleted `core/db/serializers.py` owner.

## Files

| File | Contents / current status |
|------|---------------------------|
| `dbmodel.py` | Placeholder `DBModelSerializer`; base/model contract is pending. |
| `json.py` | Placeholder `JSONSerializer`; strict JSON contract is pending. |
| `frontmatter.py` | Placeholder `FrontMatterSerializer`; naming/implementation must align with SecureMD. |
| `markdown.py` | Placeholder `MarkdownSerializer`; signed-document integration is pending. |
| `__init__.py` | Empty public package scaffold; exports are pending. |
| `<domain>.py` | Planned mirrored serializers for ORM/feature domains: `accounts`, `user`, `host`, `filesystem_path`, `network`, `address`, `provider`, `menu`, `memory`, `tasks`, `events`, `scope`, `permissions`, `llm_models`, `marketplace`, `team`, `orchestrator`, `quotas`, and `rag_vector`. |
| `serializers.md` | This executable owner document. |

## Ownership Rule

`core/serializers` owns public serializer base contracts and format-specific
strict serialization used by database/domain bridges, menu and retrieval
responses, and SecureMD frontmatter/Markdown parsing. It also owns all
`*Serializer` classes for ORM models. The deleted `core/db/serializers.py`,
`core/db/models/*.py`, `core/menu/serializers.py`, and
`core/rag_vector/serializers.py` are not final serializer owners.

## Current Source Reality

- `dbmodel.py`, `json.py`, `frontmatter.py`, and `markdown.py` contain
  placeholder subclasses only; `__init__.py` exposes no public contract.
- `core/base/base_serializer.py` is a placeholder whose ownership text still
  points at the removed DB serializer module.
- Current DB model, menu, and retrieval consumers import
  `css.core.db.serializers`, which no longer resolves; `host.py` additionally
  references `BaseModelSerializer` without importing it.
- Existing serializer classes currently sit inside many ORM model modules.
  The requested target moves these classes into mirrored
  `css.core.serializers.<domain>` modules rather than repairing them in place.

## Live Todo Map

| Todo ID | Status in `session.db` | Required change |
|---------|------------------------|-----------------|
| `serializer-base-create` | pending | Implement the public base/format contract in this package. |
| `serializer-relocate-base` | pending | Extract serializer classes for stable ORM shapes into mirrored modules; defer `Host`/`Machine`/`PathFS`/provider topology serializers to `serializer-model-infra` so no temporary target contract is created. |
| `serializer-apply-rag-vector`, `serializer-apply-menu` | pending | Move feature-local serializer classes into canonical ownership and cut endpoint imports over. |
| `serializer-model-*`, `serializer-apply-*` | pending | Move and integrate each domain serializer group after its model shape is stable. |
| `serializer-db-hub-complete` | pending | Validate canonical exports and prove no model/feature-local serializer implementations remain. |
| `db45-machine-retirement-host-promotion`, `db45-machine-data-cutover`, `db45-machine-retirement-finalization`, `db45-network-address-topology` | pending | Supply the final `Host`, `FilesystemPath`, `Network`, `Address`, `HostAddress`, and `NetworkAddress` model shapes for infrastructure serializers. |
| `db45-identity-account-profile-schema`, `db45-account-provider-junction` | pending | Supply final identity and provider relation models before their serializers are finalized. |

## Dependencies

- `serializer-relocate-base` depends on `serializer-base-create`; serializer
  consumer rollout follows extraction into the canonical package.
- `securemd44-frontmatter-serializer` depends on the package cutover because
  SecureMD parsing must use this canonical strict serializer owner.
- Infrastructure and identity serializer rows depend on their Phase 45 schema
  decisions and new relation models; they must not make those decisions inside
  serialization code.

## Extraction Pattern

| Current owner | Final serializer owner | Required removal |
|---------------|------------------------|------------------|
| `core/db/models/accounts.py`, `user.py` | `core/serializers/accounts.py`, `core/serializers/user.py` | Remove model-local serializer classes/imports after identity shape is approved. |
| `core/db/models/host.py`, current `pathfs.py` renamed to `filesystem_path.py`, `provider.py`, other topology-mutated model modules | `core/serializers/host.py`, `filesystem_path.py`, `network.py`, `address.py`, `provider.py` | Defer extraction to `serializer-model-infra`; remove model-local serializers and expose `FilesystemPathSerializer`, not `PathFSSerializer` or `MachineSerializer`, in the target schema. |
| `core/menu/serializers.py` | `core/serializers/menu.py` | Move `MenuItemTreeSerializer`; endpoints import the canonical owner. |
| `core/rag_vector/serializers.py` | `core/serializers/rag_vector.py` | Move retrieval response serializers; preserve endpoint response shape. |

Implementation rule: serializer modules may import ORM classes; ORM model
modules must not import serializer bases or serializer implementations. This
one-way dependency avoids cycles and keeps schema ownership separate.

## Validation

- Run `scripts/codebase_dependency_analyzer.py` for this package.
- Require no imports from deleted `css.core.db.serializers`.
- Require no `class *Serializer` definitions in `src/css/core/db/models/`,
  `src/css/core/menu/serializers.py`, or `src/css/core/rag_vector/serializers.py`
  after cutover.
- Run focused Ruff and basedpyright plus import smoke for the public exports
  after implementation tasks are complete.

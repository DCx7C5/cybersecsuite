# CyberSecSuite - Global Planning Index

**Purpose**: global navigation, current tracker snapshot, and execution gates.
Detailed implementation contracts live in the owning Markdown files below
`src/css/`; this file must not grow back into a second implementation plan.

**Updated**: 2026-05-27 (core boundary and host-topology planning intake)

## Current Session (2026-05-27 - Core Boundary And Schema Intake)

**Session Goal**: Reconcile the newly introduced `core/authentication`,
`core/serializers`, `core/cryptography`, and `core/securemd` source boundaries
with executable tracker ownership, then define the requested host/network,
account/provider, serializer, and manager schema work without implementing it.

**Audited Outcome**:

- Live tracker: 1079 todos | 597 done | 473 pending | 9 blocked | 0 active.
- Hierarchy repair: zero `unassigned` todos and zero empty descriptions remain.
- Phase 43 was reopened and retargeted to canonical `core/serializers`
  ownership: all `*Serializer` implementations must be extracted from ORM
  and feature-local modules into mirrored serializer modules.
- Phase 28 now owns the `core/auth` to `core/authentication` cutover and route
  contract reconciliation.
- New Phase 44 orders cryptographic key ownership, SecureMD
  integrity/origin verification, strict serialization, ingestion gating, and
  validation. Signed content is not automatically safe content.
- The adjacent `core/db/managers` package relocation has an explicit precursor
  repair and Phase 45 extraction row because its new `base.py` currently
  imports unresolved `models` while manager classes remain model-local.
- Five completed-to-incomplete dependency inconsistencies remain recorded by
  pending `audit-phase-dependency-completeness`.
- Direct source fixes: dependency-analyzer missing-symbol/deduplication support,
  `core/orchestration` export repair, xAI SDK import/lifecycle correction,
  streaming client-pool deadlock/protocol correction, and prompt-cache metrics
  false-success correction.
- False completions reopened: prompt-cache stream contract and metrics transport;
  broader runtime/type/documentation findings remain in owned pending rows.
- Provider/auth audit: corrected GitHub Models and Cloudflare credential
  contracts, declared typed API-key/OAuth capability metadata, and recorded
  SDK-runtime convergence, catalog/identity, OAuth lifecycle, and duplicated
  provider-fragment rows.
- SDK interconnectivity audit: repaired the active `AgentExecutor` call to
  its declared provider-client interface and reopened unsupported Phase 10
  claims because `core.sdks.SDKRegistry` has no registered providers while
  live callers use `api_services.ProviderRegistry`.
- Workflow policy update: development workflow now requires passing
  `--project pyrightconfig.json` for `basedpyright` commands.
- Phase 40 remains historical completion. New Phase 45 plans the requested
  follow-on schema: retire `Machine`, promote `Host`, retain `Host -> PathFS`,
  add `HostAddress`/`NetworkAddress` traversal, and add account/provider
  junctions after explicit cardinality decisions.

**Core Dependency/Reference Evidence**:

- `scripts/codebase_dependency_analyzer.py` scanned 179 `src/css/core` Python
  files and reports 12 live `core -> modules` edges.
- After repairing the broken `core/orchestration` facade, the sole confirmed
  missing imported core symbol is `TeamLeader` in
  `src/css/core/streaming/runner.py` against
  `src/css/modules/teams/orchestrator.py`.
- Core-owned Markdown reference scanning reports 14 Python files without a
  file-level documentation hit; remediation is owned by
  `audit42-core-owner-doc-boundaries`.
- Boundary and architecture-document reconciliation is recorded by
  `audit42-core-module-boundary-edges` and `audit42-plan-reference-cleanup`.

**Validation Performed**:

- `ruff check src/css tests scripts/codebase_dependency_analyzer.py` passed.
- `basedpyright` passed for the directly repaired analyzer, xAI service,
  orchestration facade, prompt-cache metrics exporter, and client pool.
- Import smoke passed for `xAIApiService`, `UvicornProcessManager`, and
  `ClientPool`.
- Provider auth validation decoded all configured `spec.yaml` files; focused
  `ruff` and `basedpyright` passed for the corrected services and typed auth
  schema/exports, and dependency analysis scanned 58 `api_services` Python
  files with no missing imported symbols.
- SDK interconnectivity validation uses an offline `AgentExecutor` response
  smoke plus dependency scans for `modules/agents`, `core/sdks`, and
  `api_services`; the agents scan reports the existing missing
  `AgentMetrics`/`AgentState`/`AgentMessage` manager imports now recorded in
  `agent-execution-logic`, while the SDK/provider scans report no missing
  imported symbols.
- Phase-level test execution remains deferred by workflow rule; existing
  ASGI and prompt-cache stream type failures are tracked rather than hidden.
- Current intake evidence: the dependency analyzer scanned each new core
  package; focused Ruff identifies unresolved serializer/header symbols, and
  focused basedpyright reports the deleted serializer imports plus the
  database-manager import defect. These are recorded as pending work rather
  than altered in source during planning.
- Model intake evidence: `Host.machine` is required, `PathFS.host` already
  exists, IP addresses are embedded on `Host`, no network/address model exists,
  `UserProfile.account` is not one-to-one, and `ApiServiceProvider` has no
  account junction. `src/css/manager.py` and `src/css/core/asgi/app.py` also
  require explicit registration changes for new model modules.

Audit report: `.plan/architecture/plan-audit-2026-05-25.md`
**Tracker authority**: `.plan/session.db`
**Local plan index**: `src/css/plan.md`
**Governing documents**: `.plan/rules.md`, `.plan/development-workflow.md`,
`.plan/checkpoints.md`, `.plan/memory.md`

## Mandatory Start Sequence

Before implementing a todo:

1. Read `.plan/rules.md` and `.plan/development-workflow.md`.
2. Query the live todo, dependencies, and statuses from `.plan/session.db`.
3. Open the owning `src/css/**/*.md` implementation specification.
4. Inspect the current source, imports, and tests; use dependency analysis when
   ownership or cross-module effects are unclear.
5. Make scoped source/test/tracker changes following the governing rules.

Do not reconstruct implementation behavior from this index alone.

## Tracker Snapshot

Snapshot queried from `.plan/session.db` on 2026-05-27:

| Total | Done | Pending | Blocked | In progress |
|------:|-----:|--------:|--------:|------------:|
| 1079 | 597 | 473 | 9 | 0 |

Overall completion: 55.3%. This planning intake preserves the new core
boundaries, replaces incompatible serializer/manager ownership assumptions,
and adds blocked schema decisions before destructive model work.

## Current Execution Boundary

Phase 41 has completed its preparation boundary. Pending tracker descriptions
and owner documents have been made executable before implementation resumes.

- All Phase 41 todo-description remediation batches now record exact
  target files, symbols, implementation steps, validation, and dependency
  gates.
- Phase 41 has no remaining pending preparation todo; the audited
  cross-consistency conflicts are recorded as resolved in `session.db`.
- Phase 43 implementation must start with `serializer-base-create`, then
  `serializer-relocate-base`, which moves serializer implementations out of
  ORM modules, before consumer or SecureMD serializer work.
- Phase 44 implementation starts with `crypto44-key-boundary`; verified
  document ingestion is downstream of both cryptography and serializers.
- Phase 45 implementation is planning-blocked at `db45-schema-decision-gates`
  for data retention, topology tenancy, identity cardinality, provider
  connection multiplicity, and `PathFS` naming decisions.
- Production migration/versioning policy is a later explicit decision, not an
  assumption to introduce during model cleanup.

## Phase Status

| Phase | Scope | Total | Done | Pending | Blocked | Active |
|------:|-------|------:|-----:|--------:|--------:|-------:|
| 0 | TeamScope Foundation | 12 | 12 | 0 | 0 | 0 |
| 1 | Multi-Orchestrator Core | 16 | 16 | 0 | 0 | 0 |
| 2 | SDK Architecture | 64 | 64 | 0 | 0 | 0 |
| 3 | Module Consistency | 155 | 153 | 0 | 2 | 0 |
| 4 | Core Consistency + Types | 24 | 22 | 0 | 2 | 0 |
| 5 | Integration & Testing | 32 | 32 | 0 | 0 | 0 |
| 6 | Architecture Overhaul | 37 | 37 | 0 | 0 | 0 |
| 7 | Feature Completeness | 19 | 19 | 0 | 0 | 0 |
| 8 | AI Execution Layer | 17 | 17 | 0 | 0 | 0 |
| 9 | ORM/Manager/Registry | 32 | 32 | 0 | 0 | 0 |
| 10 | Unified SDK Architecture | 16 | 14 | 2 | 0 | 0 |
| 11 | Cross-Provider Prompt Caching | 11 | 9 | 1 | 1 | 0 |
| 12 | QoL Output Controls Migration | 11 | 1 | 10 | 0 | 0 |
| 13 | Provider Routing & Resilience | 15 | 0 | 15 | 0 | 0 |
| 14 | Event Hooks & Entry/Exit Instrumentation | 18 | 8 | 10 | 0 | 0 |
| 15 | Permissions + WorkingDir | 32 | 0 | 31 | 1 | 0 |
| 16 | Provider SDK Features | 38 | 10 | 28 | 0 | 0 |
| 17 | Settings & Projects | 43 | 1 | 41 | 1 | 0 |
| 18 | Frontend Foundation | 45 | 8 | 37 | 0 | 0 |
| 19 | Module Restructuring + Sessions | 15 | 3 | 11 | 1 | 0 |
| 20 | Persistent Memory Layer | 44 | 8 | 36 | 0 | 0 |
| 21 | Qwen3-0.6B Triage Intelligence | 15 | 0 | 15 | 0 | 0 |
| 22 | MCP Protocol Layer | 8 | 8 | 0 | 0 | 0 |
| 23 | Prompt Registry | 11 | 1 | 10 | 0 | 0 |
| 24 | Git Tracking & Worktree Isolation | 9 | 0 | 9 | 0 | 0 |
| 25 | Integration Hardening | 14 | 8 | 6 | 0 | 0 |
| 26 | Human Approval Workflows | 15 | 0 | 15 | 0 | 0 |
| 27 | Graph Visualization Engine | 17 | 0 | 17 | 0 | 0 |
| 28 | Auth & Accounts | 10 | 1 | 9 | 0 | 0 |
| 29 | Cybersec Domain Layer | 12 | 0 | 12 | 0 | 0 |
| 30 | Workflow Engine + IPC | 5 | 0 | 5 | 0 | 0 |
| 31 | Production Readiness | 9 | 0 | 9 | 0 | 0 |
| 32 | Reports Module | 11 | 0 | 11 | 0 | 0 |
| 33 | Ollama Native | 6 | 0 | 6 | 0 | 0 |
| 34 | Dependency Map | 20 | 2 | 18 | 0 | 0 |
| 35 | Telemetry Infrastructure | 7 | 0 | 7 | 0 | 0 |
| 36 | Local Proxy & Transport Surfaces | 8 | 2 | 6 | 0 | 0 |
| 37 | SIEM/EDR Integration | 6 | 0 | 6 | 0 | 0 |
| 38 | IDE PyCharm | 5 | 4 | 1 | 0 | 0 |
| 39 | Audit Remediation (A1/A2/A3) | 43 | 7 | 36 | 0 | 0 |
| 39 | Code Quality Remediation | 5 | 5 | 0 | 0 | 0 |
| 40 | DB Model Consolidation & Rich Schemas | 42 | 42 | 0 | 0 | 0 |
| 41 | Plan Quality Remediation | 12 | 12 | 0 | 0 | 0 |
| 42 | ACP + LSP + Marketplace Implementation | 19 | 1 | 18 | 0 | 0 |
| 43 | Serializer Layer | 13 | 0 | 13 | 0 | 0 |
| 44 | Cryptography + SecureMD Integrity | 5 | 0 | 5 | 0 | 0 |
| 45 | Host Topology + Account Provider Schema | 9 | 0 | 8 | 1 | 0 |
| — | Meta — Audit & Validation | 47 | 38 | 9 | 0 | 0 |

## Local Ownership Map

Implementation detail is intentionally routed to these local documents:

| Phase(s) | Implementation owner documents |
|----------|--------------------------------|
| 0-9, 40 | `src/css/core/db/models/postgres-models.md`, `src/css/core/db/postgres-db.md`, relevant core/module owner docs |
| 10, 16 | `src/css/core/sdks/sdks.md`, `src/css/api_services/api_services.md`, `src/css/core/models/models.md` |
| 11 | `src/css/core/prompt_cache/prompt_cache.md` |
| 12 | `src/css/core/types/types.md` |
| 13 | `src/css/core/resilience/resilience.md` |
| 14 | `src/css/core/events/events.md`, `src/css/modules/hooks/hooks.md` |
| 15 | `src/css/core/permissions/permissions.md`, `src/css/modules/sessions/sessions.md` |
| 17 | `src/css/core/settings/settings.md`, `src/css/modules/projects/projects.md` |
| 18 | `src/css/core/templates/plan.md`, `src/css/core/menu/menu.md`, `src/css/core/marketplace/templates/marketplace-frontend.md`, `src/css/modules/chat/chat.md` |
| 19, 24 | `src/css/modules/modules.md`, `src/css/modules/sessions/sessions.md`, `src/css/modules/planner-dev/planner-dev.md` |
| 20 | `src/css/core/memory/memory.md`, `src/css/core/rag_vector/rag_vector.md`, `src/css/core/rag_graph/rag_graph.md` |
| 21 | `src/css/modules/triage/triage.md` |
| 22 | `src/css/modules/mcps/mcps.md`, `src/css/modules/tools/tools.md`, `src/css/core/tools/tools.md` |
| 23 | `src/css/modules/prompts/prompts.md` |
| 25 | affected owner docs in `src/css/core/` and `src/css/modules/`; tracker selects pending gaps |
| 26 | `src/css/modules/approvals/approvals.md` |
| 27 | `src/css/modules/graphs/graphs.md` |
| 28 | `src/css/core/authentication/authentication.md`, `src/css/core/accounts/accounts.md` |
| 29 | `src/css/modules/mitre/mitre.md`, `src/css/modules/threat_intel/threat_intel.md`, `src/css/modules/scans/scans.md`, `src/css/modules/incidents/incidents.md`, `src/css/modules/evidence/evidence.md`, `src/css/modules/compliance/compliance.md` |
| 30 | `src/css/modules/workflows/workflows.md`, `src/css/modules/a2a_google/a2a_google.md`, `src/css/modules/a2a_internal/a2a_internal.md` |
| 31 | `src/css/core/asgi/asgi.md`, `src/css/modules/alerts/alerts.md`, `src/css/modules/webhooks/webhooks.md`, `src/css/modules/scheduler/scheduler.md` |
| 32 | `src/css/modules/reports/reports.md` |
| 33 | `src/css/core/core.md` (native Ollama section) |
| 34, 39 | this index, local owner docs, source audit evidence, and deferred architecture reconciliation |
| 35 | `src/css/core/otel/plan.md` |
| 36 | `src/css/core/asgi/asgi.md`, `src/css/modules/llm_proxy/llm_proxy.md` |
| 37 | `src/css/modules/siem/siem.md` |
| 38 | `src/css/modules/jetbrains/jetbrains.md` |
| 42 | `src/css/modules/acp/acp.md`, `src/css/modules/mcps/mcps.md`, `src/css/core/marketplace/marketplace.md`, `src/css/modules/approvals/approvals.md`, `src/css/modules/jetbrains/jetbrains.md` (legacy bridge) |
| 43 | `src/css/core/serializers/serializers.md`, `src/css/core/types/types.md`, relevant serializer consumer owner docs |
| 44 | `src/css/core/cryptography/cryptography.md`, `src/css/core/securemd/securemd.md`, `.plan/architecture/securemd-architecture.md` |
| 45 | `src/css/core/db/models/postgres-models.md`, `src/css/core/db/postgres-db.md`, `src/css/core/accounts/accounts.md`, `src/css/core/serializers/serializers.md` |

## Sanitization Movement Record

This pass changes documentation ownership, not the implementation status of
unrelated code:

| Detail removed from the former central plan | New or expanded owner |
|---------------------------------------------|-----------------------|
| Prompt-cache execution design | `src/css/core/prompt_cache/prompt_cache.md` |
| QoL output-control contract | `src/css/core/types/types.md` |
| Routing strategies, tiers and resilience sequence | `src/css/core/resilience/resilience.md` |
| Provider SDK capability expansion | `src/css/core/sdks/sdks.md` |
| Frontend foundation execution contract | `src/css/core/templates/plan.md` |
| Settings and projects implementation ownership | `src/css/core/settings/settings.md`, `src/css/modules/projects/projects.md` |
| Persistent retrieval/memory ownership | `src/css/core/memory/memory.md`, `src/css/core/rag_vector/rag_vector.md`, `src/css/core/rag_graph/rag_graph.md` |
| Session and git/worktree behavior | `src/css/modules/sessions/sessions.md` |
| Approval and graph execution contracts | `src/css/modules/approvals/approvals.md`, `src/css/modules/graphs/graphs.md` |
| Authentication contract | `src/css/core/authentication/authentication.md` |
| Structured serializer contract | `src/css/core/serializers/serializers.md` |
| Cryptographic and signed-Markdown integrity boundary | `src/css/core/cryptography/cryptography.md`, `src/css/core/securemd/securemd.md` |
| Report generation/API pipeline | `src/css/modules/reports/reports.md` |
| DB model lanes and initialization boundaries | `src/css/core/db/models/postgres-models.md`, `src/css/core/db/postgres-db.md` |
| Host/network/address and account/provider relation graph | `src/css/core/db/models/postgres-models.md`, `src/css/core/accounts/accounts.md` |
| Telemetry stream and storage boundary | `src/css/core/otel/plan.md` |
| Local transport/proxy and SIEM contracts | `src/css/core/asgi/asgi.md`, `src/css/modules/llm_proxy/llm_proxy.md`, `src/css/modules/siem/siem.md` |
| IDE integration contract | `src/css/modules/jetbrains/jetbrains.md` |

Todo status language in local documents has been normalized: local Markdown
owns executable specifications; `.plan/session.db` owns live progress.

## Reconciliation Gates

The following items intentionally remain unresolved until compared with source
and, where relevant, architecture diagrams:

1. Session output and working-directory ownership: no implemented
   `src/css/core/workspace/` package was found during this pass. Legacy todo
   names are not implementation proof.
2. Retrieval package placement: executable packages currently exist at
   `src/css/core/rag_vector/` and `src/css/core/rag_graph/`. Moving them below
   `src/css/core/memory/` requires a bounded source/import/API migration.
3. Architecture diagrams and historical audit claims: validate them against
   live source before deleting or treating them as implementation evidence.
4. Tracker maintenance: completed-row pruning and broader stale-row cleanup are
   a separate maintenance pass after source validation.
5. Remaining policy reconciliation: validate historical schema-migration
   wording and any architecture claims against live implementation before use.
6. Provider execution convergence: duplicated `api_services/*/service.py`
   transport code, missing registry-spec coverage, GitHub Models/Copilot
   identity collision, and OAuth token lifecycle are recorded in owned rows.
7. Phase 45 schema decisions: confirm Machine data transition, Host/Network
   tenancy, User/Account/Profile cardinality, repeated provider connections,
   and whether `PathFS` should be renamed before implementation.
8. SecureMD enforcement: the source currently provides an incomplete header
   scaffold only. Implement and validate signer/key policy and context
   ingestion consumers before treating signed Markdown as trusted input.

## Documentation Maintenance Rules

- Keep executable details in the closest owning `src/css/**/*.md` document.
- Keep this file within a compact navigation/snapshot role.
- Do not duplicate local API/type/todo specifications here.
- Query `.plan/session.db` rather than copying dynamic completion state into
  local specifications.
- Require each todo description to be implementation-ready for GitHub Copilot
  Auto: exact files/symbols, ordered steps, dependencies, boundaries, and
  runnable validation.
- Use source inspection and focused dependency-analysis evidence before moving
  ownership or declaring a plan obsolete.
- Update architecture documents after source comparison when package ownership
  or security-boundary claims change.

# CyberSecSuite - Global Planning Index

**Purpose**: global navigation, current tracker snapshot, and execution gates.
Detailed implementation contracts live in the owning Markdown files below
`src/css/`; this file must not grow back into a second implementation plan.

**Updated**: 2026-05-26 (session: Phase 42 planning intake + Phase 39 runtime validation + Phase 16 xAI SDK intake)

## Current Session Goals (2026-05-26)

**Phase 41 — Plan Quality Remediation** (complete):
Initial audit result: 415/442 todos insufficient, 0 sufficient. 25 owner docs: 1 rich, 15 partial, 9 thin.
Goal: make every pending todo executable by a cheaper reasoning model without follow-up questions.

Execution order:
1. T41.1 — Enrich 442 todo descriptions in session.db (9 agent batches by phase group)
2. T41.2 — Rewrite 9 thin + improve 15 partial owner .md files
3. T41.3 — Fix 10 cross-consistency gaps (session.db + owner docs)
4. Source code sanitization (follow-on session)

**Progress** — Phase 41 description batches for Phase 40, 13-14, 15-19,
10-12, 16, 18, 20-21, 22-30, and 31-39 are complete, all nine thin plus
fifteen partial owner documents now have executable contracts, and the ten
audited consistency conflicts are resolved. Phase 41 preparation is complete.

**Phase 39 — Runtime Validation & Completion** (active):
`audit39-dependency-refresh`, `audit39-msgspec-boundary-cleanup`, and
`audit39-source-todo-cleanup` are complete. Remaining runtime validation
work is currently driven by `audit39-src-quality-gate` and downstream
dependency-gated remediation rows.

**Phase 42 — ACP + LSP + Marketplace Implementation** (new):
Added implementation todos for Agent Client Protocol (ACP), Language Server
Protocol (LSP), and marketplace delivery/runtime integration for ACP/LSP
artifacts. Execution is tracked under `T42.1` through `T42.4`.

**Phase 16 — xAI SDK Integration Intake** (new):
Added a dependency-ordered `T16.15` xAI chain to implement and use the
official `xai-sdk` client path (`AsyncClient`, stream/sample mapping, model
catalog mapping, server-side tools usage, and telemetry/retry policy bridge),
while preserving explicit fallback behavior.

**Implementation tranche** — Phase 40 still contains pending implementation
work after Phase 41 preparation; `db40-lane-marketplace` is already recorded
done and must not be reclaimed as active work.
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

Snapshot queried from `.plan/session.db` on 2026-05-26:

| Total | Done | Pending | Blocked | In progress |
|------:|-----:|--------:|--------:|------------:|
| 983 | 492 | 485 | 6 | 0 |

Current active todo: none (`in_progress = 0`). Phase 41 preparation remains
complete; Phase 39 runtime validation and Phase 42 planning intake are now
the active planning boundary.

## Current Execution Boundary

Phase 41 has completed its preparation boundary. Pending tracker descriptions
and owner documents have been made executable before implementation resumes.

- All Phase 41 todo-description remediation batches now record exact
  target files, symbols, implementation steps, validation, and dependency
  gates.
- Phase 41 has no remaining pending preparation todo; the audited
  cross-consistency conflicts are recorded as resolved in `session.db`.
- Phase 40 source work may resume only through a dependency-ready claimed row;
  its direct development-schema/model edit policy remains retained.
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
| 40 | DB Model Consolidation & Rich Schemas | 37 | 7 | 30 | 0 | 0 |
| 9 | ORM/Manager/Registry | 32 | 32 | 0 | 0 | 0 |
| 10 | Unified SDK Architecture | 16 | 11 | 5 | 0 | 0 |
| 11 | Cross-Provider Prompt Caching | 10 | 0 | 9 | 1 | 0 |
| 12 | QoL Output Controls Migration | 11 | 1 | 10 | 0 | 0 |
| 13 | Provider Routing & Resilience | 15 | 0 | 15 | 0 | 0 |
| 14 | Event Hooks & Entry/Exit Instrumentation | 18 | 8 | 10 | 0 | 0 |
| 15 | Permissions + WorkingDir | 31 | 0 | 31 | 0 | 0 |
| 16 | Provider SDK Features | 36 | 0 | 36 | 0 | 0 |
| 17 | Settings & Projects | 39 | 0 | 39 | 0 | 0 |
| 18 | Frontend Foundation | 43 | 8 | 35 | 0 | 0 |
| 19 | Module Restructuring + Sessions | 15 | 3 | 11 | 1 | 0 |
| 20 | Persistent Memory Layer | 43 | 8 | 35 | 0 | 0 |
| 21 | Qwen3-0.6B Triage Intelligence | 15 | 0 | 15 | 0 | 0 |
| 22 | MCP Protocol Layer | 8 | 5 | 3 | 0 | 0 |
| 23 | Prompt Registry | 11 | 1 | 10 | 0 | 0 |
| 24 | Git Tracking & Worktree Isolation | 9 | 0 | 9 | 0 | 0 |
| 25 | Integration Hardening | 14 | 8 | 6 | 0 | 0 |
| 26 | Human Approval Workflows | 14 | 0 | 14 | 0 | 0 |
| 27 | Graph Visualization Engine | 17 | 0 | 17 | 0 | 0 |
| 28 | Auth & Accounts | 6 | 1 | 5 | 0 | 0 |
| 29 | Cybersec Domain Layer | 10 | 0 | 10 | 0 | 0 |
| 30 | Workflow Engine + IPC | 5 | 0 | 5 | 0 | 0 |
| 31 | Production Readiness | 7 | 0 | 7 | 0 | 0 |
| 32 | Reports Module | 11 | 0 | 11 | 0 | 0 |
| 33 | Ollama Native | 6 | 0 | 6 | 0 | 0 |
| 34 | Dependency Map | 20 | 2 | 18 | 0 | 0 |
| 35 | Telemetry Infrastructure | 7 | 0 | 7 | 0 | 0 |
| 36 | Local Proxy & Transport Surfaces | 8 | 2 | 6 | 0 | 0 |
| — | unassigned | 26 | 0 | 26 | 0 | 0 |
| 37 | SIEM/EDR Integration | 6 | 0 | 6 | 0 | 0 |
| 38 | IDE PyCharm | 5 | 4 | 1 | 0 | 0 |
| 39 | Audit Remediation (A1/A2/A3) | 25 | 6 | 19 | 0 | 0 |
| 41 | Plan Quality Remediation | 12 | 12 | 0 | 0 | 0 |
| 42 | ACP + LSP + Marketplace Implementation | 19 | 1 | 18 | 0 | 0 |

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
| 28 | `src/css/core/auth/auth.md`, `src/css/core/accounts/accounts.md` |
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
| Authentication contract | `src/css/core/auth/auth.md` |
| Report generation/API pipeline | `src/css/modules/reports/reports.md` |
| DB model lanes and initialization boundaries | `src/css/core/db/models/postgres-models.md`, `src/css/core/db/postgres-db.md` |
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

## Documentation Maintenance Rules

- Keep executable details in the closest owning `src/css/**/*.md` document.
- Keep this file within a compact navigation/snapshot role.
- Do not duplicate local API/type/todo specifications here.
- Query `.plan/session.db` rather than copying dynamic completion state into
  local specifications.
- Use source inspection and focused dependency-analysis evidence before moving
  ownership or declaring a plan obsolete.
- Update architecture documents only after the deferred source comparison.

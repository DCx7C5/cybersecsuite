# src/css - Local Planning Index

**Location**: `src/css/`
**Purpose**: Route implementers to the nearest executable area specification.

## Planning Ownership

- Detailed implementation plans belong in the local document nearest the code
  that owns the behavior: `src/css/core/<area>/*.md` or
  `src/css/modules/<module>/<module>.md`.
- `.plan/plan.md` is the compact global navigation and snapshot document. It
  must not become the only location for module implementation detail.
- `.plan/session.db` is authoritative for todo status. Documentation
  sanitization may improve tracker descriptions so implementation instructions
  match local ownership, but it must not silently claim todo completion.
- `.plan/architecture/*.md` remains design/reference material until its
  diagrams and assertions are reconciled against actual source.

## Package Boundaries

| Area | Responsibility |
|------|----------------|
| `core/` | Shared runtime infrastructure and cross-cutting domain owners such as authentication, accounts, cryptography, SecureMD, serializers, events, marketplace, memory, retrieval, permissions, settings, and SDK dispatch. |
| `modules/` | User-facing/domain workflows such as agents, chat, MCPs, projects, reports, triage, workflows, and cybersec domain modules. |
| `api_services/` | External provider adapter implementations consumed through SDK/routing surfaces. |
| `src/frontend/` | Frontend application shell; feature panels remain colocated under owning CSS `templates/` directories. |

`working_dir` and `core/workspace` planning references are not settled
ownership. No implemented `src/css/core/workspace/` package was found during
this cleanup; resolve that surface against source and architecture before
implementing or relocating directory lifecycle behavior.

## Local Specification Standard

An implementer should be able to execute a local todo after reading its
`session.db` description and nearest owner document. Each owner document must
state:

- the canonical package boundary and current source reality;
- the remaining behavior or explicit implementation gate;
- dependencies/integration boundaries; and
- validation or acceptance checks for new behavior.

Provider child directories under `api_services/` are intentionally governed by
`api_services/api_services.md`; internal helper subdirectories such as
`core/db/fields/`, `core/sdks/adapters/`, and `core/types/providers/` are
governed by their parent core document unless they later acquire independent
work queues.

## Core Plan Map

| Domain | Local specification | Primary work represented |
|--------|---------------------|--------------------------|
| Application/runtime | `core/core.md`, `core/asgi/asgi.md` | Package assembly, ASGI/startup surface. |
| Authentication/accounts | `core/authentication/authentication.md`, `core/accounts/accounts.md` | Auth runtime and account identity boundary; `core/auth/` is retired. |
| Cryptography/SecureMD | `core/cryptography/cryptography.md`, `core/securemd/securemd.md` | Key-purpose ownership and signed Markdown integrity/origin verification. |
| Serializers | `core/serializers/serializers.md` | Canonical structured serialization boundary; Phase 43 extracts serializer implementations from model and feature-local modules. |
| Database/model consolidation | `core/db/postgres-db.md`, `core/db/models/postgres-models.md` | ORM ownership and Phase 45 planned organization-owned Host/FilesystemPath/Address/Network graph plus confirmed account/provider relations. |
| Events/observability | `core/events/events.md`, `core/otel/plan.md` | Event runtime, interceptors, telemetry. |
| Cache/prompt cache | `core/cache/plan.md`, `core/prompt_cache/prompt_cache.md`, `core/redis/plan.md` | Generic and provider-aware caching. |
| Models/capabilities/SDKs | `core/models/models.md`, `core/capabilities/plan.md`, `core/sdks/sdks.md` | Provider/model dispatch and advanced SDK capabilities. |
| Routing/resilience | `core/resilience/resilience.md` | Retry, failure handling, and Phase 13 expansion. |
| Types/QoL | `core/types/types.md` | Shared types and Phase 12 output-control contract. |
| Permissions/roles | `core/permissions/permissions.md`, `core/roles/plan.md` | Access control and role boundaries. |
| Settings/menu/templates | `core/settings/settings.md`, `core/menu/menu.md`, `core/templates/plan.md` | Runtime configuration, navigation, and frontend foundation. |
| Marketplace/tools | `core/marketplace/marketplace.md`, `core/tools/tools.md` | Marketplace core ownership and shared execution surface. |
| Memory/retrieval | `core/memory/memory.md`, `core/rag_vector/rag_vector.md`, `core/rag_graph/rag_graph.md` | Persistent memory and hybrid retrieval. |

## Module Plan Map

| Domain group | Local specification(s) | Primary work represented |
|--------------|------------------------|--------------------------|
| Agents/tasks/teams | `modules/agents/agents.md`, `modules/tasks/tasks.md`, `modules/teams/teams.md` | Agent orchestration and task execution. |
| Chat/prompt/proxy | `modules/chat/chat.md`, `modules/prompts/prompts.md`, `modules/llm_proxy/llm_proxy.md` | Conversation, prompt registry, proxy surfaces. |
| Sessions/projects | `modules/sessions/sessions.md`, `modules/projects/projects.md` | Session and registered project lifecycle; directory ownership requires reconciliation. |
| MCP/tools/skills | `modules/mcps/mcps.md`, `modules/tools/tools.md`, `modules/skills/skills.md` | Tool protocols and integrations. |
| Intelligence/triage | `modules/triage/triage.md` | Intelligence processing and retrieval-routing hints. |
| Approvals/workflows/graphs | `modules/approvals/approvals.md`, `modules/workflows/workflows.md`, `modules/graphs/graphs.md` | Approval gates, workflow engine, operational visualization. |
| Cybersec records | `modules/incidents/incidents.md`, `modules/scans/scans.md`, `modules/evidence/evidence.md`, `modules/compliance/compliance.md`, `modules/reports/reports.md` | Findings, evidence, compliance and report delivery. |
| Intelligence/integration | `modules/mitre/mitre.md`, `modules/threat_intel/threat_intel.md`, `modules/siem/siem.md`, `modules/webhooks/webhooks.md` | Intel and external integration surfaces. |
| IDE/local support | `modules/jetbrains/jetbrains.md`, `modules/local_assist/local_assist.md`, `modules/planner-dev/planner-dev.md` | Local and IDE-facing capabilities. |

## Implementation Entry Procedure

1. Read `.plan/rules.md` and `.plan/development-workflow.md`.
2. Read this package index and the nearest local document for the target code.
3. For implementation work, query `.plan/session.db` for the exact todo status
   and dependency chain before changing behavior.
4. Inspect actual source and dependencies before accepting planned paths,
   types, diagrams, or claimed completion.
5. Keep implementation detail in the local owner document; update the global
   index only when navigation, status snapshot, or cross-area sequencing changes.

## Deferred Reconciliation

- Validate architecture diagrams and file-layout claims against source,
  especially frontend charts/templates and session/output-directory ownership.
- Reconcile stale completed/pending tracker rows in a later explicit
  `session.db` maintenance pass.
- Compare local plans to implementation for missing behavior and plan-only
  packages before assigning development work.
- Evaluate a bounded source refactor from `core/rag_vector` and
  `core/rag_graph` into `core/memory/` subdirectories only after auditing
  imports, API registration, and ORM discovery.

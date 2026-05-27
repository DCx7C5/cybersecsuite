# Planning Memory & Session State

**Last Updated**: 2026-05-27 (runtime execution tracking sync) | **Session**: runtime table workflow/triggers, model-fit claim flow, router script removal

⚠️ **CRITICAL**: `.plan/` is the working directory. NEVER use `~/.copilot/` as working dir.  
⚠️ **CRITICAL**: session.db MUST use PHASE > TASK > TODO hierarchy (see rules.md).  
⚠️ **Remember**: `src/css/` uses local planning Markdown everywhere — core areas use the nearest planning markdown, modules use same-name docs like `agents/agents.md`. Read the nearest one FIRST and update it DURING work.  
⚠️ **Architecture**: `accounts`, `authentication`, `cryptography`, `events`, `marketplace`, `memory`, `rag_vector`, `rag_graph`, `securemd`, and `serializers` are core-owned or planned core-owned. `core/auth/` is retired in favor of `core/authentication/`. Phase 45 uses organization-owned `Host` as the canonical asset, migrates `Machine` data before removal, renames paths to `FilesystemPath`, and adds normalized address/network junctions.
⚠️ **STARTUP**: `CACHE_DIR=/tmp/css-cache LOG_DIR=/tmp/css-logs python manage.py serve --reload` (Docker = infra-only: postgres/redis/openobserve/neo4j). Ollama provider calls currently use `api_services/ollama/`; native process ownership is Phase 33 work. Frontend: `cd src/frontend && bun run dev`.
⚠️ **Memory sync rule**: `memory.md` is still phase-end by default, but it must also be refreshed immediately after major architecture, source-of-truth, or tracker-structure changes.
⚠️ **Todo quality rule**: every new or revised todo must be concrete enough for GitHub Copilot Auto to implement: exact files/symbols, ordered steps, actual dependencies, boundaries, and runnable validation.
⚠️ **Cleanup rule**: when changing code or plans, remove redundant scaffolding, stale exports, temp artifacts, dead docs, and superseded abstractions in the same pass whenever it is safe.

---

## 📊 session.db State (2026-05-27 runtime execution tracking sync)

**Total**: 1085 todos | **Done**: 601 | **Pending**: 475 | **Blocked**: 8 | **In Progress**: 1

**Overall Completion**: 55.4%

**Last Verified**: 2026-05-27 (checked against live session.db totals)

**Selected active phases**:

| Phase | Todos | Done | Pending | Blocked | In Progress | Progress |
|-------|-------|------|---------|---------|-------------|----------|
| Phase 11 — Cross-Provider Prompt Caching | 11 | 9 | 1 | 1 | 0 | 81.8% |
| Phase 10 — Unified SDK Architecture | 16 | 14 | 2 | 0 | 0 | 87.5% |
| Phase 16 — Provider SDK Features | 38 | 10 | 28 | 0 | 0 | 26.3% |
| Phase 17 — Settings & Projects | 43 | 1 | 41 | 1 | 0 | 2.3% |
| Phase 18 — Frontend Foundation | 45 | 8 | 37 | 0 | 0 | 17.8% |
| Phase 20 — Persistent Memory Layer | 44 | 8 | 36 | 0 | 0 | 18.2% |
| Phase 25 — Integration Hardening | 14 | 8 | 6 | 0 | 0 | 57.1% |
| Phase 28 — Auth & Accounts | 10 | 1 | 9 | 0 | 0 | 10.0% |
| Phase 39 — Audit Remediation (A1/A2/A3) | 44 | 7 | 37 | 0 | 0 | 15.9% |
| Phase 40 — DB Model Consolidation & Rich Schemas | 42 | 42 | 0 | 0 | 0 | 100.0% |
| Phase 42 — ACP + LSP + Marketplace Implementation | 19 | 1 | 18 | 0 | 0 | 5.3% |
| Phase 43 — Serializer Layer | 13 | 0 | 13 | 0 | 0 | 0.0% |
| Phase 44 — Cryptography + SecureMD Integrity | 7 | 3 | 4 | 0 | 0 | 42.9% |
| Phase 45 — Host Topology + Account Provider Schema | 11 | 1 | 10 | 0 | 0 | 9.1% |

**Completed phases** (100%): Phase 0, 1, 2, 5, 6, 7, 8, 9, 22, 40, 41, and the separate `Phase 39 — Code Quality Remediation` row set.

**DB note**: `sort_order INTEGER` column — use `ORDER BY sort_order` not `ORDER BY phase` (alphabetical breaks ordering).

---

## 🔑 Recent Phase Key Points

### Runtime Execution Table + Claim Flow (2026-05-27)

- Removed `scripts/todo_model_router.py`; execution tracking is now DB-native.
- Added `.plan/session.db::runtime` with triggers that auto-sync active rows
  from `todos.status='in_progress'`.
- Rule/workflow now require runtime-row cleanup immediately when a todo leaves
  `in_progress` (`done`, `blocked`, or back to `pending`).
- Worker flow now uses SQL claim/update patterns tied to model-fit metadata and
  runtime row inspection/heartbeat.

### Phase 11 Cross-Provider Prompt Caching (2026-05-26) PARTIAL (9/11)

- **Status**: 9/11 todos DONE, 1 pending (`cache-metrics-openobserve`), 1 blocked (Gemini deferred to Phase 12)
- **Modules Created**:
  - `types.py`: CachingCapability enum (5 levels: NONE, EXACT_ONLY, NATIVE_AUTOMATIC, NATIVE_AUTOMATIC_WITH_EXPLICIT_BREAKPOINTS, NATIVE_RESOURCE)
  - `manager.py`: PromptCacheManager orchestration with tier selection logic
  - `exact_match_cache.py`: O(1) Redis lookup for exact message matching
  - `streaming_buffer.py`: Async chunk accumulation and finalization
  - `native_cache_tracking.py`: Provider-native cache detection (Anthropic, OpenAI, DeepSeek)
  - `anthropic_breakpoints.py`: Explicit cache control token injection
  - `cost_savings_tracker.py`: Financial tracking with per-provider aggregation
  - `metrics_exporter.py`: preserves buffered metrics while OpenObserve transport is not yet wired
- **Protocol Extension**: LLMAdapter.cache_capability property added
- **Gate**: do not treat Phase 11 as complete or use it to unblock dependent completion claims until the stream contract and telemetry transport are reconciled

### Phase 39 Code Quality Remediation (2026-05-26) - Historical Row Set Closed, Follow-up Audit Open

- **Status**: the separate 5-row quality-remediation set is done; `Phase 39 — Audit Remediation (A1/A2/A3)` is active at 7/44 done
- **Fixed in core/asgi/app.py**:
  - Type hint: marketplace_db_config: dict[str, Any]
  - Exception handling: Replaced 8 bare Exception catches with BaseCoreException (Rule 70)
  - Variable shadowing: Renamed exception variables (db_init_error, marketplace_db_error, etc.)
  - ToolRegistry attributes: Verified type hints for tools, hybrid_tools, initialize_runtime_state
- **Follow-up evidence**: source audit found remaining broad exceptions, `Any` boundaries, ASGI registry typing errors, and prompt-cache stream-type drift; these are now owned by pending audit rows

### Plan And Core Connectivity Audit (2026-05-26)

- Rehomed all 26 prior `unassigned` todos into named phase/task owners and filled the sole empty description; live queries now report zero for both conditions.
- Reopened false completions for prompt-cache streaming, prompt metrics transport, singleton standardization, and dependency completeness.
- Enhanced `scripts/codebase_dependency_analyzer.py` to deduplicate Markdown evidence correctly and report missing internal imported symbols.
- The analyzer reports 179 core Python files, 12 current `core -> modules` edges, and one remaining confirmed missing-symbol surface: `core/streaming/runner.py` imports absent `TeamLeader` from `modules/teams/orchestrator.py`.
- A core-owner Markdown scan reports 14 files without file-level documentation hits; missing owner boundaries and stale integration-matrix assertions remain tracked rather than silently accepted.

### Authentication, Serializer, Cryptography, And SecureMD Intake (2026-05-27)

- Adopted `src/css/core/authentication/` as the planned sole authentication
  owner after the source rename; Phase 28 now includes
  `authentication-package-cutover` and active docs point at the new path.
- Reopened all previously done Phase 43 serializer rows: the new
  `src/css/core/serializers/` package is placeholder-only, while serializer
  implementations must be removed from model/menu/retrieval modules and
  moved into mirrored canonical serializer modules.
- Added Phase 44 with five dependency-ordered rows for cryptographic key
  ownership, SecureMD header verification, strict frontmatter serialization,
  marketplace-origin prompt ingestion gating, and final security validation.
- SecureMD is recorded as an integrity/signer-origin gate only. Marketplace
  preview is display-only; Phase 23 prompt rendering and reconciled agent
  execution are the planned verified-context boundary.
- Recorded adjacent `audit44-db-manager-import-cutover` as the precursor to
  Phase 45 manager extraction because focused basedpyright reports unresolved
  `from models import BaseModel` in `core/db/managers/base.py` and manager
  implementations still live beside ORM models.
- Added the binding rule that todos and instructions must provide exact
  files/symbols, steps, dependencies, boundaries, and validation so GitHub
  Copilot Auto can implement them without guessing.

### Host Topology And Account Provider Schema Decision Resolution (2026-05-27)

- Resolved `db45-schema-decision-gates`: existing `Machine` data must be
  migrated into `Host`; topology records are owned by `Organization` rather
  than `ProjectScope`; `UserAccountMembership` represents `User <-> Account`
  M:N while `Account -> UserProfile` is one-to-one; provider connections are
  repeatable through normalized names; `PathFS` is renamed to
  `FilesystemPath`.
- Added `db45-machine-data-cutover` and
  `db45-machine-retirement-finalization` so schema implementation cannot drop
  `Machine` until a fan-out/tenant-mapping preflight, data copy, and
  verification pass have completed while the source table is still readable.
- Source-backed starting point: `Host` currently depends on `Machine`,
  `PathFS` already points directly to `Host`, host IPs are scalar fields,
  network/address tables are absent, `UserProfile.account` is not unique, and
  `ApiServiceProvider` has no `Account` relation.
- Approved topology uses explicit organization-isolated junctions:
  `Host -> HostAddress -> Address -> NetworkAddress -> Network`, enabling
  reverse traversal from a network address back to every associated host.
- Rich model classes are approved for persistence-domain invariants, relation
  mutation, tenancy validation, lifecycle methods, and domain conversion;
  manager modules still own collection/bulk migration queries and serializer
  modules still own representations.
- `Machine` retirement is a new follow-on requirement, not a rewrite of the
  completed Phase 40 history; implementation remains out of scope for this
  planning session.

### Phase 22 MCP Protocol Layer (2026-05-25, verified 2026-05-26) ✅ VERIFIED COMPLETE

- **Status**: All 8 todos confirmed DONE from prior session work
- **Verified completions**: MCP lifecycle endpoints, auto-discovery, ASGI app integration
- **Unblocks**: Phase 42 (ACP + LSP + Marketplace Implementation)

### Phase 16 xAI SDK Implementation + Usage Intake (2026-05-26)

- Added five dependency-ordered `T16.15` todos in `.plan/session.db`:
  - `xai-sdk-client-dependency-pin`
  - `xai-sdk-async-client-bridge`
  - `xai-sdk-chat-stream-bridge`
  - `xai-sdk-server-side-tools-usage`
  - `xai-sdk-telemetry-policy`
- Updated existing `xai-config-base-url-yaml` and `xai-get-models-list` rows
  so model discovery is tied to official `xai-sdk` usage
  (`client.models.list_language_models()`) with deterministic fallback.
- Implementation/usage scope now explicitly includes `AsyncClient`, chat
  `stream()`/`sample()`, server-side tools (`web_search`, `x_search`,
  `code_execution`), and telemetry/retry policy wiring.

### Provider SDK, Authentication, And Duplicate-Fragment Audit (2026-05-26)

- Confirmed that the active YAML provider registry still executes through
  generic `HttpProviderAdapter` while numerous provider `service.py` files
  duplicate REST streaming/buffering code; no persisted PyCharm
  duplicate-fragment report exists in `modules/jetbrains`.
- Corrected bounded credential contract drift: GitHub Models now uses
  `GITHUB_TOKEN` with its configured models endpoint, Cloudflare uses
  `CLOUDFLARE_API_TOKEN`, and the Cerebras environment example is no longer
  populated with a stray value.
- Added typed `ProviderOAuthFlow` capability metadata; current execution
  remains API-key based, with Gemini and OpenRouter declaring planned OAuth
  authorization-code support.
- Added `provider-sdk-runtime-consolidation`,
  `provider-catalog-spec-coverage`, `auth-provider-oauth-flows`, and
  `audit42-api-services-duplicate-fragments`; OAuth execution is gated on
  encrypted provider secret storage.
- Confirmed `core.sdks` is not currently joined to the live provider path:
  `SDKRegistry` resolves no registered providers while agents and the local
  proxy consume `api_services.ProviderRegistry`; reopened
  `sdk-unified-client` and `sdk-replace-queryexecutor`.
- Repaired the bounded live-path interface defect in `base.AgentExecutor`:
  it now calls `BaseApiServiceClient.call_llm_buffered()` rather than a
  nonexistent `HttpProviderAdapter.complete()` method.
- The agent dependency scan additionally reports that provisional
  `modules/agents/manager.py` imports absent `AgentMetrics`, `AgentState`, and
  `AgentMessage`; that unresolved manager-surface work is retained under
  `agent-execution-logic`.
- Validation decoded all configured provider specs, passed focused `ruff` and
  `basedpyright` for corrected services/auth schema, and dependency-scanned 58
  provider Python files without missing imported symbols.

### Phase 42 ACP + LSP + Marketplace Implementation Intake (2026-05-26)

- Added a new execution phase with 19 dependency-ordered todos across:
  - `T42.1 ACP Protocol Baseline`
  - `T42.2 ACP Session Runtime`
  - `T42.3 LSP Runtime Bridge`
  - `T42.4 Marketplace Implementation`
- Added `acp42-module-bootstrap` (done) to establish `src/css/modules/acp/`
  as the primary ACP/LSP runtime owner while retaining `modules/jetbrains`
  as a legacy compatibility bridge.
- ACP planning aligns to protocol-v1 lifecycle: initialize/authentication,
  session/new+prompt+cancel+load+list+resume+close, session/update streams,
  and `session/request_permission` integration with approvals policy.
- LSP planning adds stdio JSON-RPC transport/runtime lifecycle, document sync,
  feature wrappers, and diagnostics ingestion as an IDE/runtime bridge.
- Marketplace planning adds ACP/LSP catalog typing, manifest seeding,
  installer runtime hooks, frontend workflows, and end-to-end lifecycle
  validation.
- Local owner docs updated for this phase:
  `modules/mcps/mcps.md`, `modules/jetbrains/jetbrains.md`,
  and `core/marketplace/marketplace.md`.

### Phase 39 Runtime Validation & Completion Addendum (2026-05-26)

- Added six dependency-gated audit rows for package refresh, msgspec/API
  boundary cleanup, ASGI/Tortoise startup repair, source TODO cleanup,
  full `src/css` quality validation, and final architecture/plan sync.
- `audit39-dependency-refresh` is done: unused conflicting `attrs` and
  `fireworks-ai` direct dependencies were removed, while the aiohttp-based
  Fireworks provider remains; `uv` and `bun` locks validate successfully.
- Completed rows now include `audit39-msgspec-boundary-cleanup` and
  `audit39-source-todo-cleanup`; quality-gate and downstream runtime rows
  remain pending.

### Documentation Ownership Sanitization + Phase 41 Remediation (2026-05-26)

- `.plan/plan.md` is now a compact global snapshot and owner index; executable
  implementation contracts live in the nearest `src/css/**/*.md` document.
- Tracker status is authoritative in `.plan/session.db`; local documents are
  implementation specifications rather than duplicated progress ledgers.
- Retired alternative persistence pending work was removed from the tracker
  by explicit direction; active memory retrieval ownership is in
  `core/memory`, `core/rag_vector`, and `core/rag_graph`.
- Module-owned triage and response-routing facades were removed from the
  `core/` root: consumers now use `modules/triage`, `modules/strategies`, and
  the public `modules/agents.AgentExecutor` API directly.
- `.plan/architecture/feature-overview.md` now records live tracker totals,
  partial source surfaces, and the active-source TODO-marker audit.
- `.plan/checkpoints.md` is explicitly historical; it no longer acts as an
  accidental live implementation source when older paths conflict with
  `session.db` or local owner documents.
- Every `.plan/session.db` todo now has a description; active descriptions were
  normalized away from removed owners and short active local documents were
  supplemented with implementation and validation contracts.
- Provider routing/resilience planning now targets
  `core/resilience/routing/`, distinct from module-owned response strategies.
- Session-output ownership remains gated: do not implement a proposed
  `core/workspace` or revive `working_dir` until the owner is explicitly
  decided.
- Phase 41 has now enriched executable specifications for the Phase 40,
  Phase 13-14, Phase 15-19, Phase 10-12, Phase 16, Phase 18, Phase 20-21,
  Phase 22-30, and Phase 31-39 description batches; todo-description
  enrichment is complete.
- The nine owner documents rated thin by the audit now contain literal target
  file maps, live todo tables, numbered execution order, and validation gates.
- The fifteen owner documents rated partial by the audit now contain the
  missing concrete symbols, step order, live statuses, and validation gates.
- All ten audited cross-consistency pairs are resolved in owner docs and
  recorded in tracker descriptions; legacy session-output rows were also
  rewritten as ownership-decision gates rather than assumed `core/workspace`
  implementation work.
- The Phase 41 preparation gate is complete. Phase 39 runtime validation is
  currently driven by `audit39-src-quality-gate` and its dependency-gated
  follow-on rows; use live dependencies and owner documents before broader
  implementation work.

### Newly Unblocked Phases (2026-05-26)

**Phase 20 — LLM Cost Optimization** (still gated by incomplete Phase 11):
- The cost tracker exists, but streaming contract repair and OpenObserve transport remain pending
- Depends on PromptCacheManager integration into the unified LLM client and corrected Phase 11 completion evidence
- Next owner: `src/css/core/cost/` or extend `core/prompt_cache`

**Phase 42 — ACP + LSP + Marketplace Implementation** (unblocked by Phase 22):
- Ready to activate with MCP server lifecycle endpoints verified
- Depends on MCP registration, lifecycle events, async client patterns
- Next owner: `modules/acp`, `modules/mcps`, `core/marketplace`

### Phase 18 Frontend Foundation — 8 todos completed (2026-05-09)

- Frontend shell scaffolded in `src/frontend/` with React 19 + Vite + strict TypeScript + Tailwind v4 + shadcn/ui.
- Core layout implemented: AppShell, Sidebar, TopBar, and PanelContainer with lazy route rendering.
- Module registry wired to dashboard/settings/marketplace/chat panel routes.
- Colocated template stubs added in:
  - `src/css/core/settings/templates/`
  - `src/css/core/marketplace/templates/`
  - `src/css/modules/chat/templates/`
- Marketplace frontend hooks + panel implemented via `src/frontend/src/panels/marketplace/*` and re-exported through `core/marketplace/templates/*`.
- Vite dev proxy now includes `/marketplace` in addition to `/api` and `/ws`.
- `frontend-live-graphs` planning has been revised from Recharts to **Apache ECharts + Web Worker processing** (Comlink-first API, batched WS ingestion, downsampled render datasets).
- Added `T18.0 Parallel Lanes` for multi-worker frontend execution:
  - theme/layout
  - settings/config integration
  - navigation shell
  - marketplace UX
  - MCP GUI
  - XYFlow integration
- Added frontend directives as explicit todos:
  - early theming pass
  - shadcn-admin layout/component reuse
  - marketplace sidebar-child navigation + side-tab removal
  - installed/catalog dual-surface marketplace design
  - MCP server start/stop/restart GUI controls
  - `@xyflow/react` integration and first topology view
- Added frontend QoL/runtime directives as explicit todos:
  - `frontend-core-templates-home-cutover` (frontend ownership move to `core/templates/*`)
  - `frontend-dashboard-tiles-workspace` + `frontend-dashboard-tiles-persistence` (add/remove/drag/drop/snap/reorder)
  - `frontend-chat-activity-stream` + `frontend-chat-thinking-task-visuals` (thinking spinners, agent activity, running tasks)

### Phase 17 Settings Consolidation — 3 todos added (2026-05-09)

- Added `T17.14 Config Consolidation` to migrate dual config surfaces into core/settings ownership:
  - `settings-config-dual-source-audit`
  - `settings-config-merge-into-core-settings`
  - `settings-config-import-cutover`
- Added startup-seeding DB directives:
  - `orm-provider-llmmodel-relation`
  - `seed-providers-empty-table-yaml`

### Phase 10 SDK Relay Expansion — 3 todos added (2026-05-09)

- Added `T10.7 Provider Priority + Browser Plugin Backend`:
  - `sdk-deepseek-adapter`
  - `sdk-browser-relay-provider-priority`
  - `sdk-browser-relay-web-llm-relay`
- Browser relay priority chain is now explicitly tracked: `github -> codex -> openai -> deepseek -> nvidia -> web-LLM relay`.
- Phase 32 reports backlog task labels were normalized from `task='unassigned'` into explicit `T32.*` buckets for parallel planning.

### Phase 39 Audit Remediation — 43 todos tracked (updated 2026-05-27)

- Added a dedicated remediation phase from three audit streams (Architecture/Runtime, Plan/Tracker Integrity, Code Quality/Rules).
- Task buckets:
  - `T39.1 Agent 1 — Architecture & Runtime Gaps` (10 todos; 1 done, 9 pending)
  - `T39.2 Agent 2 — Plan & Tracker Integrity` (9 todos; 3 done, 6 pending)
  - `T39.3 Agent 3 — Code Quality & Rules Compliance` (18 todos; 18 pending)
  - `T39.4 Runtime Validation & Completion` (6 todos; 3 done, 3 pending)
- Critical tracked gaps now explicitly queued:
  - EventStore durability + Redis fan-out
  - OTEL runtime bridge and trace propagation
  - Permission enforcement wiring
  - plan/session.db phase-name/status reconciliation
  - removal of remaining `from __future__ import annotations` and legacy typing imports
  - `__all__` policy enforcement and broad exception cleanup
- `audit38-unassigned-rehome` is now completed: all prior pending `unassigned` rows were rehomed to explicit phase/task ownership.
- Added `audit39-module-import-order-canonical` to codify `core/settings/config.py` `MODULES` line-order as canonical import-order reference.
- Added `audit42-api-services-duplicate-fragments` after source comparison
  found repeated provider REST implementations outside any stored PyCharm
  inspection artifact.
- Added `audit44-db-manager-import-cutover` after the new manager package
  failed focused import/type resolution.
- Added `T39.4 Runtime Validation & Completion` with six bounded audit rows;
  dependency refresh is done and msgspec-boundary cleanup is active.

### Phase 40 DB Model Consolidation — 42 todos complete (2026-05-09; live count updated 2026-05-27)

- Added a dedicated plan intake phase for model-location and schema requests:
  - memory model move reconciliation and canonical import cutover
  - marketplace dual-model consolidation (`marketplace.py` vs `marketplace_catalog.py`)
  - task model cutover from `quotas.py` to `tasks.py`
  - user/admin vs account/provider ownership boundary + provider rename cutover
  - MenuItem sidebar contract around `menu_id` and menu-partitioned retrieval
  - BaseTreeModel adoption inventory and tag hierarchy migration plan
  - taggable-entity inventory + singular `*Tag` naming/meta standardization
  - field/base/mixin enrichment proposals and stale `modules/cache` markdown cleanup
- Added `T40.0 Parallel Lanes` with 6 explicit lane bootstrap todos to support parallel execution with disjoint write scopes:
  - Lane A memory
  - Lane B marketplace
  - Lane C task/provider/user
  - Lane D menu/tree
  - Lane E tagging
  - Lane F platform polish
- Added `db40-direct-schema-policy`: current tranche is direct table/model mutation only (no migration scripts; Aerich deferred).
- Added `db40-menu-marketplace-children-contract` so the marketplace sidebar children set (agents/skills/mcps/workflows/templates/prompts/teams) is explicitly seeded and stable.
- User directives now reflected in todo descriptions:
  - choose higher-quality canonical model when duplicates exist
  - enforce `provider 1..N accounts` and `user 1..N accounts` ownership model
  - prioritize BaseTreeModel on menu/url/path/breadcrumb navigation use-cases
  - keep tag architecture focused on classification, not navigation

### Phase 10 SDK Architecture — Historical Delivery, Two Claims Reopened (2026-05-26)

- **T10.2 NativeSDK**: `AnthropicNativeAdapter` (prompt caching, computer_use, extended thinking) + `OpenAINativeAdapter` (structured output, assistants API) in `core/sdks/adapters/`
- **T10.3 HTTP Provider**: `HttpProviderAdapter` in `core/sdks/adapters/http_provider.py` — YAML-driven, supports OpenAI-compatible + Anthropic `/messages` format via `ProviderSpec.api_type`
- **T10.4 Ollama**: `OllamaAdapter` in `core/sdks/adapters/ollama.py` — wraps `ollama.AsyncClient`, model lifecycle (pull/list/delete)
- **T10.6 Unified Client**: `CSSLLMClient` and `SDKRegistry` source surfaces
  exist, but `sdk-unified-client` is reopened because no provider adapters
  are registered in the live SDK registry.
- **T10.6 Tools Bridge**: `modules/tools/adapter_bridge.py` — `register_adapter_tools()` converts adapter `builtin_tools()` → ToolRegistry
- **ModelNameMapper**: `core/sdks/model_mapper.py` — 20+ canonical model mappings across 10+ providers
- **Remaining**: `sdk-browser-relay-adapter` + `sdk-browser-relay-polling` (deferred)
- `sdk-replace-queryexecutor` is reopened: the Claude hardcode was removed,
  but current QueryExecutor routing reaches `api_services.ProviderRegistry`,
  not `core.sdks.CSSLLMClient`.

### DB Primitive Rollout Planning (2026-05-08)

- Phase 9 now explicitly tracks rollout of `TimestampMixin`, `BaseFrontmatterMixin`, and `VersionMixin` instead of leaving the new primitives as unplanned implementation details.
- A new guardrail todo, `db-frontmatter-field-semantics`, captures the main semantic trap: `NameField` currently behaves like an identifier field, not a general display-name field, so frontmatter/base-model rollout must wait for that split.
- Architectural decision: keep `BaseFrontmatterMixin`, remove `BaseFBSModel`. The mixin is composable; the extra base class is unused and adds no real semantic value.
- The DB source-of-truth docs now treat semantic field helpers and base-model adoption as a planned migration path, not just a coding preference.

### MCP + SIEM Planning Sync (2026-05-08)

- Phase 9 prerequisite ~~`orm-registry-metaclass-fix`~~ is now resolved: removed `ABC` from `BaseRegistry` / `BaseToolRegistry` bases (redundant — `AsyncSafeSingletonMeta(ABCMeta)` already enables `@abstractmethod`). Also deleted dead `modules/tools/base.py` duplicate and removed `_instances = None` shadowing from `BaseRegistry`.
- Phase 22 docs and tracker items now use **server-scoped MCP runtime IDs**: `mcp:{server_id}:{tool_name}`. Marketplace/catalog state stays in `core/marketplace`; runtime connect/discover/call stays in `modules/mcps`; shared registry exposure stays in `modules/tools`.
- `mcp-module-plan`, `mcp-tools-plan-update`, and `mcp-rules-update` are now marked done in `session.db` because the corresponding planning docs/rules were brought in sync with the live codebase.
- Phase 37 SIEM work is now wired explicitly to OpenObserve. `siem-models` depends on `db-oo-client-implementation` and `db-oo-stream-definitions`, and the SIEM docs now state that OpenObserve is the primary telemetry surface, with PostgreSQL and GraphRAG layered on top.

### GraphRAG Planning Baseline (2026-05-08)

- `core/rag_vector/` now means vector retrieval + hybrid orchestration.
- `core/rag_graph/` is now a dedicated planned sibling subsystem for graph ingest, graph traversal, and Neo4j-backed GraphRAG retrieval.
- MITRE ATT&CK and threat-intel remain canonically owned by `modules/mitre/` and `modules/threat_intel/`, but now explicitly project graph-native entities/relationships into `core/rag_graph/`.
- Phase 21 now also plans a narrow intelligence→graph hook: only stable extracted entities, ATT&CK hints, and confidence-scored links go to graph ingest; ephemeral routing state does not.
- the retrieval-ingestion tracker item is now `domain-rag-ingestion`, making it explicit that this is ingestion on top of the shared retrieval core.

### Rename + Connectivity Audit (2026-05-09)

- Local planning docs are being normalized to the active package names: `a2a_google`, `a2a_internal`, `rag_vector`, and `rag_graph`.
- The former `modules/rag_vector/` migration surface has been removed; active retrieval runtime code lives in `core/rag_vector/`.
- Cache posture is now explicit: not every business module should depend on `core/cache/` directly. Direct cache consumers are mainly `core/settings`, `core/permissions`, `core/marketplace`, `core/memory`, `core/rag_vector`, `core/rag_graph`, `modules/llm_proxy`, and `modules/triage`.
- Canonical source-of-truth modules such as `mitre`, `threat_intel`, `incidents`, `evidence`, `reports`, and `siem` should persist to their own primary stores first and only consume cached retrieval/prompt layers indirectly.
- The repository dependency analyzer now lives in `scripts/codebase_dependency_analyzer.py`; module-scope scans currently report **11 live cross-module imports** across the audited module paths, and the core scan reports **12 core-to-module edges**, so boundary cleanup remains real, not theoretical.

### Prompt Cache Planning Correction (2026-05-08)

- Anthropic prompt caching is now tracked as **automatic top-level `cache_control` by default**, with explicit block breakpoints kept as an advanced override for mixed-cadence prompt layouts.
- OpenAI remains native automatic caching, but the plan now also captures `prompt_cache_key` / retention hints instead of treating it as passive usage parsing only.
- Phase 11 live todos were rewritten to point at `core/prompt_cache/` and to spell out the provider-specific request shaping and usage parsing steps.

### ASGI + Local Proxy Prep (2026-05-08)

- `core/asgi/asgi.md` now treats the backend as a **single local ASGI runtime** with explicit future transport families: `/api/*`, `/ws/*`, `/sse/*`, `/v1/*`, discovery, and `/health`.
- `modules/llm_proxy` is now planned as an **in-process local-compatible proxy facade**, not a Docker or sidecar service.
- New **Phase 36 — Local Proxy & Transport Surfaces** now tracks ASGI transport prep plus the proxy facade work. Phase 36 starts with `2 done / 6 pending`.
- `frontend-sse-client` was intentionally pushed behind the first usable settings/marketplace/chat panels; the current MVP path is REST + WebSocket first, SSE/proxy later.
- Frontend dev-proxy expectations were aligned to include `/sse/*` in addition to `/api/*`, `/ws/*`, and `/v1/*`.
- Compose review found one real infra prerequisite: the custom Postgres image is based on `postgres:18-alpine` but does **not** yet install the `pgvector` extension package. Phase 20 `mem-pgvector-setup` now explicitly tracks the image work as well as the migration work.

### ✅ Phase N0 — Python 3.14 Typing Normalization (Completed 2026-05-07)

- Removed forbidden typing patterns in active code scope.
- `src/css + tests` now have:
  - `from __future__ import annotations` = 0
  - legacy typing imports (`List/Dict/Optional/...`) = 0
  - `typing.List/Dict/Optional/...` = 0
- Added guardrail command: `make lint-typing-rules` (scoped to `src/css` + `tests`).

### ✅/⛔ Phase N1 — dataclass → msgspec.Struct (2026-05-07)

- Migrated `@dataclass` usage in active scope:
  - `src/css/core/**` → done
  - `src/css/modules/**` → done
- Guardrail extended to block dataclass reintroduction in active scope.
- `src/css + tests` current state:
  - dataclass decorators = 0
  - dataclass imports (`dataclass`/`field`) = 0
- **User directive applied**: `src/legacy/**` is out of scope until explicitly requested.
  - `phase-n1-migrate-legacy` set to `blocked` accordingly.

### ✅ Phase 4 Entity Migrations (Completed 2026-05-05)

Session completed 7 Phase 4 entity migration todos:
- `phase4-verify-imports`: Core module imports verified (css.core.types, css.core.db, css.core.events, css.modules.roles all functional)
- `types-option-c-accounts`: Account entity moved to `src/css/core/accounts/types.py`
- `types-option-c-agents`: Agent entity moved to `src/css/modules/agents/types.py`
- `types-option-c-permissions`: Role entity added to `src/css/core/permissions/types.py` with built-in singletons (ORCHESTRATOR, TEAM_MODE, WORKER)
- `types-option-c-skills`: Skill entity moved to `src/css/modules/skills/types.py`
- `types-option-c-tools`: Tool entity moved to `src/css/modules/tools/types.py` + 5 helper classes (ToolParameter, ToolReturnType, ToolSchema, HybridToolSchema, ManagedTool)
- `types-option-c-reimport`: Updated `src/css/core/types/__init__.py` to import entities from new module locations

**QA Verification**: ✅ PASS
- All 5 new entity files in correct locations with proper Python syntax
- All module __init__.py files export entities via __all__
- Import chain verified: css.core.types → css.modules.*.types (no circular imports)
- Base classes (BaseAgent, BaseRole, BaseSkill, BaseTool) remain in core/types/entities/ as expected
- Old entity files still preserved for Phase 4 cleanup (types-option-c-cleanup todo)
- All changes passed ruff linting

**Files Modified**:
- src/css/core/types/__init__.py (updated imports)
- src/css/core/accounts/__init__.py (new)
- src/css/modules/agents/__init__.py (updated)
- src/css/core/permissions/__init__.py (updated)
- src/css/modules/skills/__init__.py (new)
- src/css/modules/tools/__init__.py (updated)

**Session Progress**:
- Started: 235/768 todos (Phase 3: 125/147, Phase 4: 0/23)
- Completed: 242/768 todos (+7 entity migration todos, now Phase 4: 7/24)

### ✅ DB Critical Startup Chain (Completed 2026-05-04)

`app.py` lifespan now initializes Tortoise on startup and closes connections on shutdown.  
Completed TODOs: `db-dedupe-enums`, `db-fix-tooltype-enum-empty`, `db-delete-team-stub`, `db-delete-orchestrator-dup`, `db-fix-pk-permissions`, `db-fix-marketplace-item-pk`, `db-fix-fk-labels-scope`, `db-fix-scope-level-charenum`, `db-fix-charfield-enums`, `db-fix-index-tuple-syntax`, `db-asgi-tortoise-init`.

### Phase 32 — Reports Module (2026-05-04, NEWLY ADDED)
- **Supersedes** 3 duplicate report todos from Phase 7/19/29 (marked blocked)
- **ORM**: `Report`, `ReportArtifact`, `ReportTemplate` — 3 models
- **Services**: `ReportBuilder` (data collection) → `ReportRenderer` (Jinja2→MD→HTML) → `ReportExporter` (weasyprint PDF + JSON)
- **5 builtin templates** seeded on `init-db`: ExecutiveSummary, TechnicalFindings, IncidentTimeline, ComplianceMapping (NIST/SOC2/ISO27001), VulnerabilitySummary
- **Async generation**: POST /api/reports/ → 202 + BackgroundTask PENDING→GENERATING→READY/FAILED
- **Hook events**: `report.generation.started/complete/failed` + WS push
- **Frontend**: ReportsPanel, GenerateReportModal, ReportViewer, TemplateEditor (Monaco)
- **Deps**: gates on `domain-incidents`, `domain-scans`, `domain-compliance`, `prod-task-queue`

### Phase 25 — Integration Hardening (2026-05-04, NEWLY ADDED)
- **10 inter-module connection gaps** found in full audit (Gaps A–J)
- **Gap A** (CRITICAL): `css.core.session` missing — already tracked as `session-context-create` in Phase 15
- **Gap B** (HIGH): ORM models missing — ProjectRecord, McpServerConfigRecord, PromptDefinitionRecord
- **Gap C** (HIGH): `core/types/projects.py` missing — projects/plan.md references it
- **Gap D** (BLOCKED): `context.py` uses `@dataclass + BaseModel` anti-pattern on 4 classes
- **Gap E** (BLOCKED): `ScopeLevel` defined independently in 3 places (core/db, scopes, permissions)
- **Gap H/I**: 8 modules still have placeholder integration tables; `chat` and `triage` still need formalized matrices, while `llm_proxy` and `workflows` are already covered
- **Gap J**: `@cache` not referenced in any consuming module's integration table
- **Two todos BLOCKED** (`gap-scopelevel-deduplicate`, `gap-context-antipattern`) pending user decision

### Phase 24 — Git Tracking & Worktree Isolation
- **Git isolation is gated** — `git-session-init` may initialize a repository only after the canonical session-output owner and artifact directory are approved
- **Auto-commit per turn** — `GitTracker.commit_turn()` fires as @post_hook priority=100 (non-blocking, fire-and-forget)
- **One agent = one worktree = one branch** — `WorktreeManager.create()` on SessionManager.add_agent()
- **Branch convention**: `agent/{session_id[:8]}/{agent_id}`
- **Merge at session end**: MergeStrategy SQUASH (default) / REBASE / OURS / MANUAL
- **3-layer audit**: L1 git (files) + L2 Phase 6 P3 events (domain) + L3 Phase 19 turns (reasoning)
- **Migration**: legacy `scope.py` has `worktree_path`; its replacement waits for the session-output ownership decision
- **Gates**: depends on Phase 15 ownership resolution (`working-dir-manager`) and Phase 19 session lifecycle work

### Phase 23 — Prompt Registry
- Prompts = first-class versioned entities. **Not MCP.** Platform's own template library.
- `MarketplaceItemType.prompt` already existed — wired in `prompt-marketplace-wire`
- Template syntax: `{{variable}}` + `{{> partial_id}}` includes (one level, no Jinja2)
- All types: msgspec.Struct (frozen). PromptCategory: SYSTEM/USER/FEW_SHOT/CHAIN/PERSONA/INSTRUCTION
- Versioning: prompt_id + version unique key. `registry.get("id")` returns latest.

### Phase 22 — MCP Protocol Layer
- `@mcps` ≠ `@tools`. tools/ = LLM provider builtin tools. mcps/ = MCP server connections.
- **PYTHON_DIRECT**: `Client(FastMCP_instance)` — in-process, zero HTTP. `module_path="pkg:factory"` format.
- fastmcp v3.1.0 already in pyproject.toml. `fastmcp.Client` unified across all transports.
- `McpToolBridge` pushes MCP tools into ToolRegistry as `ToolType.MCP`, `provider="mcp:{server_id}"`.

### Phase 33 — Ollama Native (planned)
- Current provider-call source remains `src/css/api_services/ollama/`.
- Phase 33 may implement `src/css/core/ollama/` for native process lifecycle (`installer.py`, `process.py`) after its pending todos are executed.
- Provider-call and host-process ownership must remain distinct; no current `core/ollama` runtime is claimed.
- **No preloader** — models are dev recommendations, pulled manually. `installer.py` prints the hint:
    `ollama pull qwen3:0.6b` / `phi4-mini:3.8b-q4_K_M` / `qwen3:4b-q4_K_M`
- `llama-cpp-python` is an optional future dependency, not wired into current Ollama provider calls.
- Dependency chain: `ollama-install-checker` → `ollama-process-manager` → `ollama-lifespan-wire` → `ollama-docker-remove`

### Phase 21 — Triage Intelligence Scope
- Canonical runtime ownership is `src/css/modules/triage/`; no automatic rename to `modules/intelligence` is approved.
- Scope broadened: quality gates, conversation health, cost budget, memory tagging, tone adaptation — all local AI assistance (not just routing/classification)
- Local inference currently consumes `src/css/api_services/ollama/`; native process ownership is separately planned in Phase 33.

### Phase 20 — Persistent Memory Layer
- `MemoryEntry` (msgspec.Struct, frozen): provider-agnostic — survives model/provider swap.
- Hot tier: Redis sliding window + token budget. Cold tier: PostgreSQL + tsvector FTS.
- `ContextAssembler`: MemoryEntry list → provider-specific message format.
- Integration: SessionManager.create/resume/end + AgentExecutor pre/post turn.

---

## 🚀 Phase 6 — 5 Approved Architecture Proposals

All 5 approved. Tasks under `Phase 6 — Architecture Overhaul` in session.db.

| Proposal                                 | Core idea                                                                                                  | Key tasks              |
|------------------------------------------|------------------------------------------------------------------------------------------------------------|------------------------|
| P1 — Protocol-first + msgspec            | Drop ABC/dataclass mixing. Protocol for contracts, msgspec.Struct for values. 10-40× faster serialization. | `p6-msgspec-*` (5)     |
| P2 — 24 YAML specs + 1 adapter           | Replace 24 provider classes (~4800 LOC) with YAML + 1 HttpProviderAdapter (~150 LOC)                       | `p6-yaml-*` (5)        |
| P3 — CQRS + Event Store                  | Every mutation = immutable DomainEvent in PostgreSQL. Forensic replay built-in.                            | `p6-events-*` (5)      |
| P4 — importlib.metadata entry_points     | Replace pkgutil with Python plugin system. Loader → 20 lines.                                              | `p6-entrypoints-*` (4) |
| P5 — Composable async generator pipeline | `pipe(source, classify, route, execute, observe)` — each stage one `async def __aiter__`                   | `p6-pipeline-*` (6)    |

---

## 🩺 Anti-Patterns (avoid repeating)

1. `agents/base.py`, `skills/base.py` → ✅ DELETED (0 LOC, no refs)
2. `__all__` in wrong files — must be in `__init__.py` only
3. **`@dataclass + ABC` on same class** = forbidden. **`@dataclass + BaseModel(Pydantic)` on same class** = forbidden. Pure `@dataclass` alone (no ABC) = acceptable for value types / frontmatter structs, but migrate to `msgspec.Struct` on touch (Phase 6 P1). `context.py` fix tracked as `gap-context-antipattern`.
4. `aiohttp` not `httpx`, `uv` not `pip`, `bun` not `npm`
5. Do not import from `~~scopes~~` — DEPRECATED, pending deletion (Phase 15)
6. **`project_dir` is not `session_dir`** — `SessionContext.session_dir` is the isolated output concept whose allocator/root remains to be approved. `project.source_dir` is the target/codebase reference. They are not nested by assumption.

---

## ⚠️ Structural Debt (open)

- **`core/caching/` renamed → `core/prompt_cache/`**: Clearer name. Two-tier only (Redis + provider-native prompt caching). Anthropic uses automatic top-level `cache_control` by default with explicit breakpoints only when needed; OpenAI/DeepSeek native tracking is also part of Phase 11. Streaming-buffer contract and metrics transport are pending; Gemini `NATIVE_RESOURCE` stays blocked/deferred.
- **`core/retry/` renamed → `core/resilience/`**: Already has `detection.py`, `orchestrator.py`, `config.py` — broader than retry alone.
- **`working_dir` module deleted; replacement unresolved**: no implemented `core/workspace/` package was found during documentation sanitization. Retain the session-output/permission requirement, but validate source and architecture before creating a replacement owner.
- **`modules/cache/` → `core/cache/` completed**: L4 SQLite removed. 3-layer cache stack is L1 memory, L2 redis.asyncio, L3 PostgreSQL; `core/cache/` is canonical.
- **`modules/triage` remains canonical**: Phase 21 broadens local intelligence behavior without renaming the current runtime package by assumption.
- Tool Registry partially implemented (provider normalization + execution path still pending) — Phase 3
- **`mcps` ↔ `tools` bridge is now planned precisely but still not implemented**: `modules/mcps/registry.py` exists, the runtime/tool/marketplace boundaries are documented, and the runtime ID contract is `mcp:{server_id}:{tool_name}`. What is still missing is the actual `McpToolBridge` implementation plus MCP delegation in the tool execution path.
- ~~**Registry singleton standardization had an unresolved metaclass issue**: `BaseRegistry` / `BaseToolRegistry` combined `AsyncSafeSingletonMeta` with `ABC`, causing import-time conflicts. Fixed by removing `ABC` from both bases (redundant — `AsyncSafeSingletonMeta(ABCMeta)` already provides abstract method support).~~ ✅
- Permissions not implemented — Phase 15
- Events module missing (0/5 files) — Phase 6 P3
- 5-file pattern: only 3/48 components compliant — Phase 3/4
- 13 pre-existing test collection errors (bare `db`/`api_services`/`ai_proxy` imports) — Phase 6 P4

---

## 📚 Key Planning Documents

- `.plan/plan.md` — phases overview + Phase 6 proposals
- `.plan/session.db` — **1085 todos**, PHASE > TASK > TODO hierarchy (`unassigned` count is zero; 1 in_progress: dep-map-modules-prompts)
- `.plan/rules.md` — absolute dev rules (live inventory, ready-query, stack rules)
- `.plan/checkpoints.md` — session history (018 checkpoints)
- `src/css/modules/modules.md` + `src/css/modules/*/<module>.md` — live module index + per-module source-of-truth
- `src/css/api_services/api_services.md` — provider source-of-truth index

### TYPE_CHECKING Elimination (2026-05-27)

- **Goal**: Replace all `TYPE_CHECKING`-guarded imports with unconditional
  imports, Protocols, or alternative patterns — eliminating the circular-import
  workaround where not genuinely required.
- **Scope**: 12 files identified with `if TYPE_CHECKING:` blocks.
- **8 eliminated**:
  - `core/logger.py` — used `logging.Logger` directly (stdlib, no circular risk)
  - `core/types/base_endpoint.py` — pydantic types moved to inline
    `_GetCoreSchemaHandler` Protocol; later upgraded to production-ready
    version with full docstrings (matching pydantic's originals), all
    interface methods (including `_get_types_namespace`), and removed
    redundant `-> dict[str, object]` return annotation on
    `__get_pydantic_core_schema__` (type checker infers
    `PlainValidatorFunctionSchema` from body instead).
  - `core/memory/session_store.py` — ORM model imports unconditional (no circular)
  - `core/memory/service.py` — ORM model imports unconditional (no circular)
  - `core/models/registry.py` — `LLMModel` import unconditional (no circular)
  - `modules/agents/base.py` — `DynamicCapabilityRegistry` unconditional (core dep)
  - `core/events/emitter.py` — `EventBus` unconditional (no circular verified)
  - `core/streaming/runner.py` — replaced with inline `_AgentExecutorProtocol`
    and `_TeamLeaderProtocol` (preserves core→modules architectural boundary)
- **4 retained** (legitimate patterns):
  - `core/types/base_enums.py` — dynamic `ProviderType` enum from filesystem discovery
  - `modules/tags/manager.py` — genuine circular with `models.py` (`TagManager` imported by `Tag`)
  - `modules/agents/__init__.py` — canonical lazy-import package pattern
  - `modules/tools/__init__.py` — canonical lazy-import package pattern
- **Side discovery**: 3 stale `from css.core.pipeline import Stage` imports in
  `modules/triage/pipeline.py`, `modules/strategies/pipeline.py`,
  `modules/chat/pipeline_endpoint.py` — reference the deleted `core/pipeline.py`
  which survives only as untracked leftover. Cleanup queued for next pass.
- **Validation**: `ruff check src/css/` passes (4 pre-existing unrelated errors);
  runtime import smoke test passes for all modified modules.

### SecureMD Config Toggles + Crypto Scaffold (2026-05-27)

- Confirmed `securemd-config-toggles` was already implemented: SECUREMD_ENABLED and SECUREMD_ENFORCE_HEADER env vars exist in config.py and .env.example.
- Confirmed `crypto44-key-boundary` was already implemented: Ed25519 generate/sign/verify/load primitives exist in core/cryptography/__init__.py.
- Confirmed `securemd44-header-integrity` was already implemented: BaseFrontmatterHeader and FrontMatterHeader with sign/verify/verify_and_get_body exist.
- Marked all three Phase 44 in_progress todos as done — they were implemented in the prior session but never tracked as complete.
- Added `securemd-fix-duplicate-secret-key` (pending): remove duplicate SECRET_KEY at config.py lines 5-9.
- `serializer-base-create` updated: FrontMatterSerializer must be compatible with BaseFrontmatterHeader and SECUREMD_ENFORCE_HEADER toggle.
- Plan snapshot: 1085 total, 601 done, 475 pending, 8 blocked, 1 in_progress.
- Phase 44 now has 7 todos (was 5). Phase 39 has 44 (was 43).

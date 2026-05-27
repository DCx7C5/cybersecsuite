# Plan Quality Audit — 2026-05-25

**Historical snapshot note (2026-05-27)**: This report records pre-rename
evidence. Current authentication ownership is `src/css/core/authentication/`;
live status and implementation instructions are authoritative in
`.plan/session.db`, `.plan/plan.md`, and the nearest owner Markdown.

## Executive Summary
- Total pending todos: 442
- Sufficient: 0 (0.0%)
- Partial: 27 (6.1%)
- Insufficient: 415 (93.9%)
- Owner .md files audited: 25
- Rich: 1 | Partial: 15 | Thin: 9
- Focus checks: all 6 todos under 100 chars were ❌ insufficient; 89 todos are under 200 chars with no file path heuristic hit.
- Manual spot-check sample (30 medium-length todos across phases): none met all 5 required description criteria. Sample IDs: sdk-browser-relay-polling, sdk-browser-relay-adapter, cache-automatic-native-tracking, cache-caching-capability-enum, qol-unified-client-middleware, qol-a2a-integration, routing-unified-client-wire, routing-rest-endpoints, events-instrument-tool, events-instrument-decorator, …

## A — session.db Todos Needing Enrichment

### Insufficient (❌) — needs full rewrite
| id | phase | current_desc_len | gap |
|---|---|---|---|
| `fe18-lane-mcp-gui` | Phase 18 — Frontend Foundation | 85 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `fe18-lane-navigation-shell` | Phase 18 — Frontend Foundation | 85 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `fe18-lane-theme-layout` | Phase 18 — Frontend Foundation | 85 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-marketplace-duplicate-remove` | Phase 40 — DB Model Consolidation & Rich Schemas | 87 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `fe18-lane-marketplace-ux` | Phase 18 — Frontend Foundation | 94 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-marketplace-canonical-cutover` | Phase 40 — DB Model Consolidation & Rich Schemas | 98 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-taskmodel-import-cutover` | Phase 40 — DB Model Consolidation & Rich Schemas | 101 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `fe18-lane-settings-config` | Phase 18 — Frontend Foundation | 102 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-settings-nav-runtime` | Phase 18 — Frontend Foundation | 107 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit38-remove-legacy-typing-imports` | Phase 39 — Audit Remediation (A1/A2/A3) | 107 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-memory-legacy-remove` | Phase 40 — DB Model Consolidation & Rich Schemas | 107 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `graph-xyflow-adoption-plan` | Phase 27 — Graph Visualization Engine | 108 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `sdk-deepseek-adapter` | Phase 10 — Unified SDK Architecture | 112 | very short; no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-menu-tree-constraints` | Phase 40 — DB Model Consolidation & Rich Schemas | 112 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `settings-config-import-cutover` | Phase 17 — Settings & Projects | 116 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-marketplace-remove-kind-tabs` | Phase 18 — Frontend Foundation | 116 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `mcp-server-lifecycle-runtime-wire` | Phase 22 — MCP Protocol Layer | 119 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit38-all-export-policy` | Phase 39 — Audit Remediation (A1/A2/A3) | 119 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `mcp-server-lifecycle-api` | Phase 22 — MCP Protocol Layer | 121 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit38-remove-future-annotations` | Phase 39 — Audit Remediation (A1/A2/A3) | 121 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-mcp-servers-panel` | Phase 18 — Frontend Foundation | 122 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-mcp-servers-hooks` | Phase 18 — Frontend Foundation | 124 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-quotas-task-residual-cleanup` | Phase 40 — DB Model Consolidation & Rich Schemas | 124 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `db40-llmmodel-tag-runtime-wire` | Phase 40 — DB Model Consolidation & Rich Schemas | 126 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `settings-config-merge-into-core-settings` | Phase 17 — Settings & Projects | 127 | very short; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `gap-orm-prompts-models` | Phase 23 — Prompt Registry | 127 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-dashboard-tiles-persistence` | Phase 18 — Frontend Foundation | 129 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `settings-db-migration` | Phase 17 — Settings & Projects | 130 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `audit38-stale-blocked-cleanup` | Phase 39 — Audit Remediation (A1/A2/A3) | 130 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `gap-orm-mcps-models` | Phase 22 — MCP Protocol Layer | 132 | very short; no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit38-any-reduction-pass` | Phase 39 — Audit Remediation (A1/A2/A3) | 132 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-marketplace-ux-refine` | Phase 18 — Frontend Foundation | 134 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-menu-menuid-endpoints` | Phase 40 — DB Model Consolidation & Rich Schemas | 135 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit38-bare-exception-replacement` | Phase 39 — Audit Remediation (A1/A2/A3) | 137 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit38-charenumfield-migration` | Phase 39 — Audit Remediation (A1/A2/A3) | 137 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-xyflow-integration` | Phase 18 — Frontend Foundation | 138 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-xyflow-marketplace-mcp-view` | Phase 18 — Frontend Foundation | 139 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `ollama-lifespan-wire` | Phase 33 — Ollama Native | 143 | very short; no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-memory-canonical-cutover` | Phase 40 — DB Model Consolidation & Rich Schemas | 144 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-lane-platform-polish` | Phase 40 — DB Model Consolidation & Rich Schemas | 148 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-provider-model-cutover` | Phase 40 — DB Model Consolidation & Rich Schemas | 149 | very short; no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-tag-junction-meta-backfill` | Phase 40 — DB Model Consolidation & Rich Schemas | 151 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `sdk-browser-relay-provider-priority` | Phase 10 — Unified SDK Architecture | 152 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-tag-junction-naming-standard` | Phase 40 — DB Model Consolidation & Rich Schemas | 153 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `approval-permissions-wire` | Phase 26 — Human Approval Workflows | 154 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-direct-schema-policy` | Phase 40 — DB Model Consolidation & Rich Schemas | 154 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `settings-config-dual-source-audit` | Phase 17 — Settings & Projects | 155 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit38-phase-name-normalization` | Phase 39 — Audit Remediation (A1/A2/A3) | 156 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-taggable-entity-inventory` | Phase 40 — DB Model Consolidation & Rich Schemas | 156 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-memory-feature-merge` | Phase 40 — DB Model Consolidation & Rich Schemas | 158 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-theme-early-pass` | Phase 18 — Frontend Foundation | 159 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit38-stale-scope-docrefs` | Phase 39 — Audit Remediation (A1/A2/A3) | 159 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `events-instrument-command-bus` | Phase 14 — Event Hooks & Entry/Exit Instrumentation | 160 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-marketplace-sidebar-children-nav` | Phase 18 — Frontend Foundation | 164 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-marketplace-feature-merge` | Phase 40 — DB Model Consolidation & Rich Schemas | 165 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `projects-db-migration` | Phase 17 — Settings & Projects | 166 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-chat-activity-stream` | Phase 18 — Frontend Foundation | 167 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-cache-md-reference-fix` | Phase 40 — DB Model Consolidation & Rich Schemas | 167 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `sdk-browser-relay-web-llm-relay` | Phase 10 — Unified SDK Architecture | 168 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit38-phase22-reconcile` | Phase 39 — Audit Remediation (A1/A2/A3) | 168 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-lane-tagging` | Phase 40 — DB Model Consolidation & Rich Schemas | 168 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-lane-marketplace` | Phase 40 — DB Model Consolidation & Rich Schemas | 169 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-modules-mcps` | Phase 34 — Dependency Map | 170 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-lane-memory` | Phase 40 — DB Model Consolidation & Rich Schemas | 170 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit39-module-import-order-canonical` | Phase 39 — Audit Remediation (A1/A2/A3) | 171 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit38-entrypoints-p4-gap` | Phase 39 — Audit Remediation (A1/A2/A3) | 172 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit38-otel-runtime-wire` | Phase 39 — Audit Remediation (A1/A2/A3) | 172 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-menu-menuid-upsert` | Phase 40 — DB Model Consolidation & Rich Schemas | 172 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `seed-providers-empty-table-yaml` | Phase 17 — Settings & Projects | 173 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-mixins-expansion` | Phase 40 — DB Model Consolidation & Rich Schemas | 174 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `orm-provider-llmmodel-relation` | Phase 17 — Settings & Projects | 175 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-tagging-db-concept` | Phase 40 — DB Model Consolidation & Rich Schemas | 176 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-dashboard-tiles-workspace` | Phase 18 — Frontend Foundation | 178 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-marketplace-installed-catalog-layout` | Phase 18 — Frontend Foundation | 180 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-sidebar-menu-runtime` | Phase 18 — Frontend Foundation | 180 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-menu-marketplace-children-contract` | Phase 40 — DB Model Consolidation & Rich Schemas | 181 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-memory-usage-audit` | Phase 40 — DB Model Consolidation & Rich Schemas | 182 | no exact file paths; no class/function names; no numbered steps |
| `db40-field-library-expansion` | Phase 40 — DB Model Consolidation & Rich Schemas | 184 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-chat-thinking-task-visuals` | Phase 18 — Frontend Foundation | 185 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-topbar-rich-navigation` | Phase 18 — Frontend Foundation | 185 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `idepycharm-agent-wiring` | Phase 38 — IDE PyCharm | 186 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-basetree-candidate-inventory` | Phase 40 — DB Model Consolidation & Rich Schemas | 187 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `auth-middleware` | Phase 28 — Auth & Accounts | 188 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-marketplace-dualmodel-usage-audit` | Phase 40 — DB Model Consolidation & Rich Schemas | 190 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `approval-events` | Phase 26 — Human Approval Workflows | 192 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `accounts-module` | Phase 28 — Auth & Accounts | 192 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `events-otel-auto-deps` | Phase 14 — Event Hooks & Entry/Exit Instrumentation | 193 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `rerank-adapter` | Phase 16 — Provider SDK Features | 196 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `graph-react-flow` | Phase 27 — Graph Visualization Engine | 196 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `telemetry-filesystem-md` | Phase 35 — Telemetry Infrastructure | 196 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `telemetry-timescaledb` | Phase 35 — Telemetry Infrastructure | 196 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit38-permissions-enforcement-wire` | Phase 39 — Audit Remediation (A1/A2/A3) | 197 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `workflow-endpoints` | Phase 30 — Workflow Engine + IPC | 199 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `ollama-model-preloader` | Phase 33 — Ollama Native | 200 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `graph-module-files` | Phase 27 — Graph Visualization Engine | 201 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `sessions-endpoints` | Phase 19 — Module Restructuring + Sessions | 203 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `ollama-llama-cpp-dep` | Phase 33 — Ollama Native | 205 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-decorator-require-tool` | Phase 15 — Permissions + WorkingDir | 206 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `xai-get-models-list` | Phase 16 — Provider SDK Features | 206 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `thinking-config-struct` | Phase 16 — Provider SDK Features | 207 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-lane-task-provider-user` | Phase 40 — DB Model Consolidation & Rich Schemas | 208 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `mem-session-wire` | Phase 20 — Persistent Memory Layer | 210 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `prompt-rules-update` | Phase 23 — Prompt Registry | 210 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `audit38-eventstore-pg-redis-wire` | Phase 39 — Audit Remediation (A1/A2/A3) | 210 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `native-tools-hooks` | Phase 16 — Provider SDK Features | 211 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `xai-config-base-url-yaml` | Phase 16 — Provider SDK Features | 211 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `approval-channel` | Phase 26 — Human Approval Workflows | 211 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `events-otel-trace-context` | Phase 14 — Event Hooks & Entry/Exit Instrumentation | 212 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `mem-redis-token-budget` | Phase 20 — Persistent Memory Layer | 212 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `triage-module-plan-update` | Phase 21 — Qwen3-0.6B Triage Intelligence | 212 | no class/function names; no numbered steps; no validation criteria |
| `approval-audit-stream` | Phase 26 — Human Approval Workflows | 212 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `events-instrument-llm-client` | Phase 14 — Event Hooks & Entry/Exit Instrumentation | 214 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-basetree-tag-adoption-plan` | Phase 40 — DB Model Consolidation & Rich Schemas | 214 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-model-meta-standardization` | Phase 40 — DB Model Consolidation & Rich Schemas | 215 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `telemetry-dashboard` | Phase 35 — Telemetry Infrastructure | 216 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-user-vs-account-boundary` | Phase 40 — DB Model Consolidation & Rich Schemas | 216 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `gemini-cache-manager` | Phase 16 — Provider SDK Features | 218 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `reports-json-export` | Phase 32 — Reports Module | 218 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `domain-threat-intel` | Phase 29 — Cybersec Domain Layer | 220 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `native-tools-computer-use` | Phase 16 — Provider SDK Features | 223 | no exact file paths; no numbered steps; no validation criteria |
| `graph-endpoints` | Phase 27 — Graph Visualization Engine | 223 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `graph-openobserve-wire` | Phase 27 — Graph Visualization Engine | 223 | no exact file paths; no numbered steps; no validation criteria |
| `graph-session-flow` | Phase 27 — Graph Visualization Engine | 223 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `batch-api-openai` | Phase 16 — Provider SDK Features | 224 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `graph-approval-flow` | Phase 27 — Graph Visualization Engine | 225 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `graph-snapshot-orm` | Phase 27 — Graph Visualization Engine | 225 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-rename-scope-to-session` | Phase 15 — Permissions + WorkingDir | 226 | no exact file paths; no class/function names; no numbered steps; no dependencies/preconditions |
| `graph-approval-overlay` | Phase 27 — Graph Visualization Engine | 226 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `auth-project-isolation` | Phase 28 — Auth & Accounts | 226 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `approval-module-files` | Phase 26 — Human Approval Workflows | 228 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `sessions-lifecycle` | Phase 19 — Module Restructuring + Sessions | 230 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-shadcn-admin-harvest` | Phase 18 — Frontend Foundation | 231 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `native-tools-permissions` | Phase 16 — Provider SDK Features | 232 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `gap-orm-projects-models` | Phase 17 — Settings & Projects | 232 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `sessions-persistence` | Phase 19 — Module Restructuring + Sessions | 233 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-path-op-flag` | Phase 15 — Permissions + WorkingDir | 234 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `prompt-exceptions` | Phase 23 — Prompt Registry | 234 | no exact file paths; no class/function names; no numbered steps; no dependencies/preconditions |
| `graph-events-wire` | Phase 27 — Graph Visualization Engine | 234 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `prod-rate-limiting` | Phase 31 — Production Readiness | 235 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `reports-enums` | Phase 32 — Reports Module | 235 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `graph-workflow-builder` | Phase 27 — Graph Visualization Engine | 236 | no exact file paths; no numbered steps; no validation criteria |
| `dep-map-core-types` | Phase 34 — Dependency Map | 237 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `domain-mitre` | Phase 29 — Cybersec Domain Layer | 238 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `mem-pg-model` | Phase 20 — Persistent Memory Layer | 239 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `domain-reports` | Phase 29 — Cybersec Domain Layer | 239 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `triage-confidence-scorer` | Phase 21 — Qwen3-0.6B Triage Intelligence | 240 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `prompt-enums` | Phase 23 — Prompt Registry | 240 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `approval-endpoints` | Phase 26 — Human Approval Workflows | 241 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `token-count-in-routing` | Phase 16 — Provider SDK Features | 244 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `projects-manager-sessions` | Phase 17 — Settings & Projects | 244 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-core-resilience` | Phase 34 — Dependency Map | 245 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `working-dir-search-layout` | Phase 15 — Permissions + WorkingDir | 246 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `prod-openapi-polish` | Phase 31 — Production Readiness | 246 | no exact file paths; no class/function names; no numbered steps; no dependencies/preconditions |
| `background-job-struct` | Phase 16 — Provider SDK Features | 247 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `batch-api-anthropic` | Phase 16 — Provider SDK Features | 247 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `session-context-create` | Phase 15 — Permissions + WorkingDir | 249 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `events-otel-child-spans` | Phase 14 — Event Hooks & Entry/Exit Instrumentation | 250 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `ollama-router-check` | Phase 16 — Provider SDK Features | 250 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `telemetry-collector` | Phase 35 — Telemetry Infrastructure | 251 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `openrouter-cost-tracking` | Phase 16 — Provider SDK Features | 252 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `triage-micro-router` | Phase 21 — Qwen3-0.6B Triage Intelligence | 254 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `rerank-cohere` | Phase 16 — Provider SDK Features | 255 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `graph-types` | Phase 27 — Graph Visualization Engine | 256 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db-oo-stream-definitions` | Phase 35 — Telemetry Infrastructure | 258 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `orm-capability-record` | Phase 17 — Settings & Projects | 259 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `approval-gate` | Phase 26 — Human Approval Workflows | 259 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `projects-event-emission` | Phase 17 — Settings & Projects | 261 | no exact file paths; no numbered steps; no validation criteria |
| `triage-intent-drift` | Phase 21 — Qwen3-0.6B Triage Intelligence | 261 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `prod-multitenancy-rls` | Phase 31 — Production Readiness | 261 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `approval-timeout-handler` | Phase 26 — Human Approval Workflows | 262 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `approval-agentexecutor-wire` | Phase 26 — Human Approval Workflows | 264 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `mem-memory-tagger-hook` | Phase 20 — Persistent Memory Layer | 265 | no exact file paths; no numbered steps; no validation criteria |
| `triage-paraphrase-suggester` | Phase 21 — Qwen3-0.6B Triage Intelligence | 265 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `context-mgmt-struct` | Phase 16 — Provider SDK Features | 267 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `sessions-module-create` | Phase 19 — Module Restructuring + Sessions | 268 | no exact file paths; no numbered steps; no validation criteria |
| `triage-memory-tagger` | Phase 21 — Qwen3-0.6B Triage Intelligence | 268 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `approval-ws-push` | Phase 26 — Human Approval Workflows | 268 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `domain-scans` | Phase 29 — Cybersec Domain Layer | 269 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `memory-provider-parity-tests` | Phase 20 — Persistent Memory Layer | 270 | no class/function names; no numbered steps; no dependencies/preconditions |
| `triage-micro-voter` | Phase 21 — Qwen3-0.6B Triage Intelligence | 270 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `triage-tone-adapter` | Phase 21 — Qwen3-0.6B Triage Intelligence | 270 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `triage-fallback-whisperer` | Phase 21 — Qwen3-0.6B Triage Intelligence | 272 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `graph-ws-stream` | Phase 27 — Graph Visualization Engine | 272 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `ollama-docker-remove` | Phase 33 — Ollama Native | 273 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `gemini-cache-adapter` | Phase 16 — Provider SDK Features | 274 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `prod-task-queue` | Phase 31 — Production Readiness | 274 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `fe18-lane-xyflow` | Phase 18 — Frontend Foundation | 276 | no class/function names; no numbered steps; no dependencies/preconditions |
| `frontend-core-templates-home-cutover` | Phase 18 — Frontend Foundation | 276 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `triage-paradox-spotter` | Phase 21 — Qwen3-0.6B Triage Intelligence | 277 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `batch-api-protocol` | Phase 16 — Provider SDK Features | 278 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `domain-incidents` | Phase 29 — Cybersec Domain Layer | 278 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `working-dir-planner-layout` | Phase 15 — Permissions + WorkingDir | 281 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `claude-sdk-session-bridge` | Phase 16 — Provider SDK Features | 282 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `triage-echo-detector` | Phase 21 — Qwen3-0.6B Triage Intelligence | 282 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `domain-evidence` | Phase 29 — Cybersec Domain Layer | 282 | no exact file paths; no class/function names; no numbered steps; no dependencies/preconditions |
| `domain-compliance` | Phase 29 — Cybersec Domain Layer | 283 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `prod-dockerfile` | Phase 31 — Production Readiness | 283 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `mistral-ocr-adapter` | Phase 16 — Provider SDK Features | 284 | no exact file paths; no numbered steps; no dependencies/preconditions |
| `prod-alerts` | Phase 31 — Production Readiness | 284 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `events-middleware-fastapi` | Phase 14 — Event Hooks & Entry/Exit Instrumentation | 285 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `ipc-message-bus` | Phase 30 — Workflow Engine + IPC | 285 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-checker-exceptions` | Phase 15 — Permissions + WorkingDir | 286 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `settings-event-emission` | Phase 17 — Settings & Projects | 286 | no exact file paths; no numbered steps; no validation criteria |
| `workflow-runner` | Phase 30 — Workflow Engine + IPC | 286 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `gap-core-types-projects` | Phase 17 — Settings & Projects | 287 | no class/function names; no numbered steps; no dependencies/preconditions |
| `workflow-definition` | Phase 30 — Workflow Engine + IPC | 287 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `qol-cache-key-toggle-hash` | Phase 12 — QoL Output Controls Migration | 288 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `thinking-config-adapter` | Phase 16 — Provider SDK Features | 288 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `mem-agent-wire` | Phase 20 — Persistent Memory Layer | 289 | no exact file paths; no numbered steps; no validation criteria |
| `auth-secrets-settings` | Phase 28 — Auth & Accounts | 289 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-core-redis` | Phase 34 — Dependency Map | 289 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `orm-api-service-provider` | Phase 17 — Settings & Projects | 290 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `triage-intelligence-wire` | Phase 21 — Qwen3-0.6B Triage Intelligence | 290 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-modules-prompts` | Phase 34 — Dependency Map | 290 | no class/function names; no numbered steps; no dependencies/preconditions |
| `qol-dangerous-combos-validator` | Phase 12 — QoL Output Controls Migration | 291 | no exact file paths; no class/function names; no numbered steps; no dependencies/preconditions |
| `context-mgmt-adapter` | Phase 16 — Provider SDK Features | 291 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `graph-telemetry-service` | Phase 27 — Graph Visualization Engine | 291 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `mistral-fim-adapter` | Phase 16 — Provider SDK Features | 293 | no exact file paths; no numbered steps; no dependencies/preconditions |
| `siem-analyzer` | Phase 37 — SIEM/EDR Integration | 293 | no numbered steps; no validation criteria; no dependencies/preconditions |
| `graph-sse-endpoint` | Phase 27 — Graph Visualization Engine | 294 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `background-job-openai` | Phase 16 — Provider SDK Features | 295 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `approval-seed-policies` | Phase 26 — Human Approval Workflows | 295 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-zustand-store` | Phase 18 — Frontend Foundation | 296 | no numbered steps; no validation criteria; no dependencies/preconditions |
| `working-dir-agent-subdir` | Phase 15 — Permissions + WorkingDir | 300 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `token-count-method` | Phase 16 — Provider SDK Features | 300 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `mem-provider-survival` | Phase 20 — Persistent Memory Layer | 300 | no class/function names; no numbered steps; no dependencies/preconditions |
| `siem-module` | Phase 37 — SIEM/EDR Integration | 300 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `git-tracker` | Phase 24 — Git Tracking & Worktree Isolation | 301 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `triage-token-budget-analyst` | Phase 21 — Qwen3-0.6B Triage Intelligence | 302 | no exact file paths; no class/function names; no numbered steps; no dependencies/preconditions |
| `telemetry-schema` | Phase 35 — Telemetry Infrastructure | 302 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `core-templates-cleanup` | Phase 19 — Module Restructuring + Sessions | 304 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-modules-capabilities` | Phase 34 — Dependency Map | 304 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-pipeline-home-plan` | Phase 40 — DB Model Consolidation & Rich Schemas | 304 | no class/function names; no numbered steps; no validation criteria |
| `qol-builtin-presets` | Phase 12 — QoL Output Controls Migration | 305 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db40-intelligence-home-plan` | Phase 40 — DB Model Consolidation & Rich Schemas | 305 | no class/function names; no numbered steps; no dependencies/preconditions |
| `frontend-sse-client` | Phase 18 — Frontend Foundation | 306 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `db-oo-client-implementation` | Phase 35 — Telemetry Infrastructure | 306 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-modules-rich` | Phase 34 — Dependency Map | 307 | no exact file paths; no class/function names; no numbered steps; no dependencies/preconditions |
| `streaming-decouple-from-scopes` | Phase 15 — Permissions + WorkingDir | 308 | no exact file paths; no class/function names; no numbered steps |
| `memory-persistence-guardrails` | Phase 20 — Persistent Memory Layer | 309 | no class/function names; no numbered steps; no dependencies/preconditions |
| `triage-pre-filter` | Phase 21 — Qwen3-0.6B Triage Intelligence | 309 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `git-tracking-docs` | Phase 24 — Git Tracking & Worktree Isolation | 309 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `gap-triage-integration` | Phase 25 — Integration Hardening | 309 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `native-tools-registry` | Phase 16 — Provider SDK Features | 310 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-plan-master` | Phase 34 — Dependency Map | 310 | no class/function names; no numbered steps; no dependencies/preconditions |
| `working-dir-cleanup` | Phase 15 — Permissions + WorkingDir | 311 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `mem-module-files` | Phase 20 — Persistent Memory Layer | 311 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `proxy-streaming-normalization` | Phase 36 — Local Proxy & Transport Surfaces | 311 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-tool-grant-struct` | Phase 15 — Permissions + WorkingDir | 312 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `triage-rename-module` | Phase 19 — Module Restructuring + Sessions | 312 | no class/function names; no numbered steps; no validation criteria |
| `approval-policy-orm` | Phase 26 — Human Approval Workflows | 312 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `rag-vector-backend` | Phase 20 — Persistent Memory Layer | 313 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit38-phase-table-sync` | Phase 39 — Audit Remediation (A1/A2/A3) | 313 | no class/function names; no numbered steps; no validation criteria |
| `scopes-module-remove` | Phase 15 — Permissions + WorkingDir | 316 | no exact file paths; no class/function names; no numbered steps |
| `groq-audio-adapter` | Phase 16 — Provider SDK Features | 316 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `settings-manager-seed` | Phase 17 — Settings & Projects | 316 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `prod-ws-lifecycle` | Phase 31 — Production Readiness | 316 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-modules-marketplace` | Phase 34 — Dependency Map | 316 | no class/function names; no numbered steps; no dependencies/preconditions |
| `asgi-transport-policy` | Phase 36 — Local Proxy & Transport Surfaces | 316 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `siem-response` | Phase 37 — SIEM/EDR Integration | 316 | no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-core-workspace` | Phase 34 — Dependency Map | 317 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `qol-preset-registry` | Phase 12 — QoL Output Controls Migration | 318 | no exact file paths; no numbered steps; no dependencies/preconditions |
| `settings-manager-templates` | Phase 17 — Settings & Projects | 318 | no numbered steps; no validation criteria; no dependencies/preconditions |
| `qol-rest-endpoints` | Phase 12 — QoL Output Controls Migration | 319 | no exact file paths; no numbered steps; no dependencies/preconditions |
| `git-session-init` | Phase 24 — Git Tracking & Worktree Isolation | 319 | no exact file paths; no numbered steps; no validation criteria |
| `gap-chat-integration` | Phase 25 — Integration Hardening | 320 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `siem-ingest` | Phase 37 — SIEM/EDR Integration | 320 | no numbered steps; no validation criteria; no dependencies/preconditions |
| `git-scope-migration` | Phase 24 — Git Tracking & Worktree Isolation | 321 | no exact file paths; no numbered steps; no validation criteria |
| `cache-redis-streaming-buffer` | Phase 11 — Cross-Provider Prompt Caching | 322 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `claude-sdk-hook-bridge` | Phase 16 — Provider SDK Features | 322 | no exact file paths; no class/function names; no numbered steps; no dependencies/preconditions |
| `projects-workingdir-integration` | Phase 17 — Settings & Projects | 322 | no exact file paths; no numbered steps; no validation criteria |
| `rag-context-wire` | Phase 20 — Persistent Memory Layer | 322 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-grant-redis-cache` | Phase 15 — Permissions + WorkingDir | 323 | no exact file paths; no numbered steps; no dependencies/preconditions |
| `git-merge-manager` | Phase 24 — Git Tracking & Worktree Isolation | 324 | no exact file paths; no numbered steps; no validation criteria |
| `reports-renderer` | Phase 32 — Reports Module | 324 | no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-core-otel` | Phase 34 — Dependency Map | 324 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-core-cache` | Phase 34 — Dependency Map | 325 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-core-ollama` | Phase 34 — Dependency Map | 325 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-scopes-cleanup` | Phase 15 — Permissions + WorkingDir | 326 | no class/function names; no numbered steps; no dependencies/preconditions |
| `settings-manager-cache` | Phase 17 — Settings & Projects | 326 | no exact file paths; no numbered steps; no dependencies/preconditions |
| `gap-scopelevel-deduplicate` | Phase 15 — Permissions + WorkingDir | 327 | no class/function names; no numbered steps; no dependencies/preconditions |
| `memory-metrics-and-policy-telemetry` | Phase 20 — Persistent Memory Layer | 327 | no class/function names; no numbered steps; no dependencies/preconditions |
| `qol-unified-client-middleware` | Phase 12 — QoL Output Controls Migration | 328 | no exact file paths; no numbered steps; no validation criteria |
| `perm-decorator-require-path` | Phase 15 — Permissions + WorkingDir | 329 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `rename-planer-to-planner` | Phase 19 — Module Restructuring + Sessions | 329 | no class/function names; no numbered steps; no dependencies/preconditions |
| `ollama-install-checker` | Phase 33 — Ollama Native | 332 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-core-db` | Phase 34 — Dependency Map | 332 | no class/function names; no numbered steps; no validation criteria |
| `memory-domain-events` | Phase 20 — Persistent Memory Layer | 333 | no class/function names; no numbered steps; no dependencies/preconditions |
| `mem-pg-adapter` | Phase 20 — Persistent Memory Layer | 334 | no class/function names; no numbered steps; no dependencies/preconditions |
| `graph-protocol` | Phase 27 — Graph Visualization Engine | 334 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `rag-core-ownership` | Phase 20 — Persistent Memory Layer | 336 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `approval-protocol` | Phase 26 — Human Approval Workflows | 336 | no exact file paths; no numbered steps; no dependencies/preconditions |
| `mem-redis-adapter` | Phase 20 — Persistent Memory Layer | 337 | no class/function names; no numbered steps; no dependencies/preconditions |
| `gap-events-missing-ns` | Phase 25 — Integration Hardening | 337 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-ws-manager` | Phase 18 — Frontend Foundation | 338 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `rag-fusion-layer` | Phase 20 — Persistent Memory Layer | 338 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-path-grant-struct` | Phase 15 — Permissions + WorkingDir | 339 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-core-orchestration` | Phase 34 — Dependency Map | 339 | no class/function names; no numbered steps; no dependencies/preconditions |
| `proxy-local-trust-boundary` | Phase 36 — Local Proxy & Transport Surfaces | 339 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `graph-rag-mitre-projection` | Phase 29 — Cybersec Domain Layer | 341 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `cache-cost-savings-tracker` | Phase 11 — Cross-Provider Prompt Caching | 342 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `projects-record-struct` | Phase 17 — Settings & Projects | 344 | no class/function names; no numbered steps; no dependencies/preconditions |
| `frontend-chat-hooks` | Phase 18 — Frontend Foundation | 344 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `graph-rag-threat-intel-projection` | Phase 29 — Cybersec Domain Layer | 344 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `memory-failure-mode-contract` | Phase 20 — Persistent Memory Layer | 345 | no class/function names; no numbered steps; no dependencies/preconditions |
| `openrouter-provider-list` | Phase 16 — Provider SDK Features | 346 | no class/function names; no numbered steps; no dependencies/preconditions |
| `working-dir-manager` | Phase 15 — Permissions + WorkingDir | 347 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `audit38-workspace-module-baseline` | Phase 39 — Audit Remediation (A1/A2/A3) | 347 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-modules-intelligence` | Phase 34 — Dependency Map | 348 | no class/function names; no numbered steps; no validation criteria |
| `graph-rag-backend` | Phase 20 — Persistent Memory Layer | 351 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `rag-query-modes` | Phase 20 — Persistent Memory Layer | 351 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `reports-pdf-export` | Phase 32 — Reports Module | 351 | no class/function names; no numbered steps; no validation criteria |
| `memory-rollout-and-backfill` | Phase 20 — Persistent Memory Layer | 352 | no exact file paths; no class/function names; no numbered steps; no dependencies/preconditions |
| `git-rules-update` | Phase 24 — Git Tracking & Worktree Isolation | 352 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `mem-context-assembler` | Phase 20 — Persistent Memory Layer | 353 | no class/function names; no numbered steps; no dependencies/preconditions |
| `frontend-settings-panel` | Phase 18 — Frontend Foundation | 354 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `qol-openobserve-metrics` | Phase 12 — QoL Output Controls Migration | 355 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `proxy-routing-bridge` | Phase 36 — Local Proxy & Transport Surfaces | 356 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `mem-protocol-struct` | Phase 20 — Persistent Memory Layer | 357 | no class/function names; no numbered steps; no dependencies/preconditions |
| `graph-rag-core-ownership` | Phase 20 — Persistent Memory Layer | 358 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `orm-rich-meta` | Phase 17 — Settings & Projects | 361 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `reports-events` | Phase 32 — Reports Module | 361 | no class/function names; no numbered steps; no dependencies/preconditions |
| `audit38-feature-inventory-sync` | Phase 39 — Audit Remediation (A1/A2/A3) | 361 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `seed-tools-builtin` | Phase 17 — Settings & Projects | 364 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `memory-provider-memory-adapters` | Phase 20 — Persistent Memory Layer | 365 | no class/function names; no numbered steps; no dependencies/preconditions |
| `bug-fix-sessionstore-race` | Phase 20 — Persistent Memory Layer | 366 | no exact file paths; no class/function names; no numbered steps |
| `siem-types` | Phase 37 — SIEM/EDR Integration | 367 | no numbered steps; no validation criteria; no dependencies/preconditions |
| `rag-cache-layer` | Phase 20 — Persistent Memory Layer | 369 | no exact file paths; no class/function names; no numbered steps |
| `sdk-browser-relay-polling` | Phase 10 — Unified SDK Architecture | 370 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `qol-tortoise-model` | Phase 12 — QoL Output Controls Migration | 371 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `projects-rest-routes` | Phase 17 — Settings & Projects | 371 | no class/function names; no numbered steps; no dependencies/preconditions |
| `gap-agents-plan-stale` | Phase 25 — Integration Hardening | 372 | no class/function names; no numbered steps; no dependencies/preconditions |
| `naming-clarity-docs` | Phase 15 — Permissions + WorkingDir | 375 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `settings-db-model` | Phase 17 — Settings & Projects | 376 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `gap-context-antipattern` | Phase 15 — Permissions + WorkingDir | 378 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `naming-scope-utils-paths` | Phase 15 — Permissions + WorkingDir | 378 | no exact file paths; no class/function names; no numbered steps |
| `frontend-chat-panel` | Phase 18 — Frontend Foundation | 378 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `ollama-process-manager` | Phase 33 — Ollama Native | 378 | no exact file paths; no numbered steps; no validation criteria |
| `seed-tags-defaults` | Phase 17 — Settings & Projects | 379 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-dev-tooling` | Phase 18 — Frontend Foundation | 380 | no exact file paths; no class/function names; no numbered steps; no dependencies/preconditions |
| `bug-fix-sessionstore-dataloss` | Phase 20 — Persistent Memory Layer | 380 | no exact file paths; no numbered steps; no dependencies/preconditions |
| `orm-llm-model-record` | Phase 17 — Settings & Projects | 382 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `seed-permissions-defaults` | Phase 17 — Settings & Projects | 382 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `gap-integration-placeholders` | Phase 25 — Integration Hardening | 382 | no exact file paths; no class/function names; no numbered steps; no dependencies/preconditions |
| `proxy-openai-surface` | Phase 36 — Local Proxy & Transport Surfaces | 382 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `asgi-mounted-surfaces` | Phase 36 — Local Proxy & Transport Surfaces | 384 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-grant-models` | Phase 15 — Permissions + WorkingDir | 385 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `thinking-model-metadata` | Phase 16 — Provider SDK Features | 385 | no exact file paths; no class/function names; no numbered steps; no dependencies/preconditions |
| `graph-recharts` | Phase 27 — Graph Visualization Engine | 387 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `projects-manager-fs-sync` | Phase 17 — Settings & Projects | 388 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `settings-definition-struct` | Phase 17 — Settings & Projects | 388 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `mem-compression` | Phase 20 — Persistent Memory Layer | 388 | no class/function names; no numbered steps; no dependencies/preconditions |
| `seed-capabilities-startup` | Phase 17 — Settings & Projects | 389 | no exact file paths; no numbered steps; no validation criteria |
| `triage-graph-rag-entity-projection` | Phase 21 — Qwen3-0.6B Triage Intelligence | 390 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `cache-response-stats-struct` | Phase 11 — Cross-Provider Prompt Caching | 391 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `domain-rag-ingestion` | Phase 29 — Cybersec Domain Layer | 396 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-grant-manager` | Phase 15 — Permissions + WorkingDir | 397 | no exact file paths; no numbered steps; no dependencies/preconditions |
| `merge-strategies-into-triage` | Phase 19 — Module Restructuring + Sessions | 398 | no class/function names; no numbered steps; no dependencies/preconditions |
| `siem-models` | Phase 37 — SIEM/EDR Integration | 403 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `qol-injector-service` | Phase 12 — QoL Output Controls Migration | 407 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `qol-a2a-integration` | Phase 12 — QoL Output Controls Migration | 413 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-checker-can-tool` | Phase 15 — Permissions + WorkingDir | 413 | no exact file paths; no class/function names; no numbered steps; no validation criteria |
| `projects-db-model` | Phase 17 — Settings & Projects | 414 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-settings-hooks` | Phase 18 — Frontend Foundation | 416 | no class/function names; no numbered steps; no dependencies/preconditions |
| `cache-redis-exact-match` | Phase 11 — Cross-Provider Prompt Caching | 421 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `sdk-browser-relay-adapter` | Phase 10 — Unified SDK Architecture | 423 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `settings-templates` | Phase 17 — Settings & Projects | 425 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `prompt-marketplace-wire` | Phase 23 — Prompt Registry | 429 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `cache-automatic-native-tracking` | Phase 11 — Cross-Provider Prompt Caching | 430 | no exact file paths; no numbered steps; no validation criteria |
| `cache-metrics-openobserve` | Phase 11 — Cross-Provider Prompt Caching | 433 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `dep-map-modules-thin` | Phase 34 — Dependency Map | 433 | no exact file paths; no class/function names; no numbered steps; no dependencies/preconditions |
| `seed-models-startup` | Phase 17 — Settings & Projects | 435 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-checker-can-elevated` | Phase 15 — Permissions + WorkingDir | 438 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `reports-builtin-templates` | Phase 32 — Reports Module | 438 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-hook-tool-enforcement` | Phase 15 — Permissions + WorkingDir | 439 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `git-worktree-sessionmgr` | Phase 24 — Git Tracking & Worktree Isolation | 439 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `seed-providers-fixtures` | Phase 17 — Settings & Projects | 443 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-landing-dashboard` | Phase 18 — Frontend Foundation | 446 | no class/function names; no numbered steps; no validation criteria |
| `approval-orm` | Phase 26 — Human Approval Workflows | 451 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `gap-cache-wiring` | Phase 25 — Integration Hardening | 453 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-checker-can-path` | Phase 15 — Permissions + WorkingDir | 465 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `reports-endpoints` | Phase 32 — Reports Module | 465 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `reports-background-task` | Phase 32 — Reports Module | 471 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `settings-rest-routes` | Phase 17 — Settings & Projects | 477 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `reports-frontend` | Phase 32 — Reports Module | 479 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `cache-caching-capability-enum` | Phase 11 — Cross-Provider Prompt Caching | 481 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `cache-anthropic-breakpoint-injector` | Phase 11 — Cross-Provider Prompt Caching | 511 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `reports-orm` | Phase 32 — Reports Module | 517 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `cache-prompt-cache-manager` | Phase 11 — Cross-Provider Prompt Caching | 531 | no exact file paths; no numbered steps; no validation criteria; no dependencies/preconditions |
| `perm-rest-endpoints` | Phase 15 — Permissions + WorkingDir | 533 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `prompt-renderer` | Phase 23 — Prompt Registry | 535 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `mem-pgvector-setup` | Phase 20 — Persistent Memory Layer | 542 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `routing-combo-target-model` | Phase 13 — Provider Routing & Resilience | 574 | no numbered steps; no validation criteria; no dependencies/preconditions |
| `prompt-types-struct` | Phase 23 — Prompt Registry | 580 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `prompt-registry` | Phase 23 — Prompt Registry | 581 | no exact file paths; no numbered steps; no dependencies/preconditions |
| `routing-budget-guard` | Phase 13 — Provider Routing & Resilience | 590 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `routing-strategy-enum` | Phase 13 — Provider Routing & Resilience | 608 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `prompt-models` | Phase 23 — Prompt Registry | 616 | no exact file paths; no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `settings-defaults-all` | Phase 17 — Settings & Projects | 628 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `routing-circuit-breaker` | Phase 13 — Provider Routing & Resilience | 633 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `prompt-endpoints` | Phase 23 — Prompt Registry | 649 | no exact file paths; no class/function names; no numbered steps; no dependencies/preconditions |
| `routing-unified-client-wire` | Phase 13 — Provider Routing & Resilience | 651 | no numbered steps; no validation criteria; no dependencies/preconditions |
| `routing-strategy-resolver` | Phase 13 — Provider Routing & Resilience | 662 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `routing-rest-endpoints` | Phase 13 — Provider Routing & Resilience | 669 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `routing-usage-tracker` | Phase 13 — Provider Routing & Resilience | 698 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `routing-tier-selector` | Phase 13 — Provider Routing & Resilience | 708 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `routing-triage-complexity` | Phase 13 — Provider Routing & Resilience | 711 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `rename-css-a2a-to-ipc` | Phase 19 — Module Restructuring + Sessions | 722 | no class/function names; no numbered steps; no validation criteria |
| `routing-token-counter` | Phase 13 — Provider Routing & Resilience | 732 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `routing-rate-limiter` | Phase 13 — Provider Routing & Resilience | 738 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `routing-qwen-triage-router` | Phase 13 — Provider Routing & Resilience | 783 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `routing-combo-router` | Phase 13 — Provider Routing & Resilience | 789 | no class/function names; no numbered steps; no validation criteria |
| `notifications-module-create` | Phase 19 — Module Restructuring + Sessions | 902 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |
| `frontend-port-hooks` | Phase 18 — Frontend Foundation | 1054 | no class/function names; no numbered steps; no validation criteria |
| `frontend-live-graphs` | Phase 18 — Frontend Foundation | 1093 | no class/function names; no numbered steps; no validation criteria; no dependencies/preconditions |

### Partial (⚠️) — needs specific additions
| id | phase | missing_criteria | recommendation |
|---|---|---|---|
| `routing-combo-registry` | Phase 13 — Provider Routing & Resilience | steps, dependencies | add numbered implementation steps; name prerequisite todos/owners explicitly |
| `events-event-bus-module` | Phase 14 — Event Hooks & Entry/Exit Instrumentation | steps, dependencies | add numbered implementation steps; name prerequisite todos/owners explicitly |
| `events-instrument-agent` | Phase 14 — Event Hooks & Entry/Exit Instrumentation | symbols, steps | add numbered implementation steps; name exact classes/functions/methods |
| `events-instrument-decorator` | Phase 14 — Event Hooks & Entry/Exit Instrumentation | steps | add numbered implementation steps |
| `events-instrument-tool` | Phase 14 — Event Hooks & Entry/Exit Instrumentation | symbols, steps | add numbered implementation steps; name exact classes/functions/methods |
| `naming-session-context-rename` | Phase 15 — Permissions + WorkingDir | file_paths, steps | add numbered implementation steps; add exact `src/...` file paths |
| `perm-grant-profiles` | Phase 15 — Permissions + WorkingDir | symbols, steps | add numbered implementation steps; name exact classes/functions/methods |
| `perm-hook-path-enforcement` | Phase 15 — Permissions + WorkingDir | symbols, steps | add numbered implementation steps; name exact classes/functions/methods |
| `ollama-model-manager` | Phase 16 — Provider SDK Features | file_paths, steps | add numbered implementation steps; add exact `src/...` file paths |
| `projects-manager-crud` | Phase 17 — Settings & Projects | steps, dependencies | add numbered implementation steps; name prerequisite todos/owners explicitly |
| `settings-manager-core` | Phase 17 — Settings & Projects | steps, dependencies | add numbered implementation steps; name prerequisite todos/owners explicitly |
| `settings-registry-class` | Phase 17 — Settings & Projects | steps, dependencies | add numbered implementation steps; name prerequisite todos/owners explicitly |
| `settings-registry-singleton` | Phase 17 — Settings & Projects | symbols, steps | add numbered implementation steps; name exact classes/functions/methods |
| `sessions-mode-layout` | Phase 19 — Module Restructuring + Sessions | file_paths, steps | add numbered implementation steps; add exact `src/...` file paths |
| `mem-manager` | Phase 20 — Persistent Memory Layer | steps, dependencies | add numbered implementation steps; name prerequisite todos/owners explicitly |
| `mem-protocol-interface` | Phase 20 — Persistent Memory Layer | steps, dependencies | add numbered implementation steps; name prerequisite todos/owners explicitly |
| `memory-context-assembler-integration` | Phase 20 — Persistent Memory Layer | symbols, steps | add numbered implementation steps; name exact classes/functions/methods |
| `memory-module-api-surface` | Phase 20 — Persistent Memory Layer | steps, dependencies | add numbered implementation steps; name prerequisite todos/owners explicitly |
| `memory-startup-wiring` | Phase 20 — Persistent Memory Layer | symbols, steps | add numbered implementation steps; name exact classes/functions/methods |
| `memory-test-harness-and-fixtures` | Phase 20 — Persistent Memory Layer | steps, dependencies | add numbered implementation steps; name prerequisite todos/owners explicitly |
| `git-tracker-hook` | Phase 24 — Git Tracking & Worktree Isolation | file_paths, steps | add numbered implementation steps; add exact `src/...` file paths |
| `git-worktree-manager` | Phase 24 — Git Tracking & Worktree Isolation | file_paths, steps | add numbered implementation steps; add exact `src/...` file paths |
| `auth-jwt-module` | Phase 28 — Auth & Accounts | file_paths, steps | add numbered implementation steps; add exact `src/...` file paths |
| `planner-agent` | Phase 30 — Workflow Engine + IPC | steps, dependencies | add numbered implementation steps; name prerequisite todos/owners explicitly |
| `reports-builder` | Phase 32 — Reports Module | steps, dependencies | add numbered implementation steps; name prerequisite todos/owners explicitly |
| `audit-plan-quality` | Phase 34 — Dependency Map | steps, dependencies | add numbered implementation steps; name prerequisite todos/owners explicitly |
| `dep-map-core-asgi` | Phase 34 — Dependency Map | symbols, steps | add numbered implementation steps; name exact classes/functions/methods |

### Spot-check notes
- Medium-length sample reviewed across phases: `sdk-browser-relay-polling`, `sdk-browser-relay-adapter`, `cache-automatic-native-tracking`, `cache-caching-capability-enum`, `qol-unified-client-middleware`, `qol-a2a-integration`, `routing-unified-client-wire`, `routing-rest-endpoints`, `events-instrument-tool`, `events-instrument-decorator`, `working-dir-manager`, `perm-grant-redis-cache`, `groq-audio-adapter`, `background-job-struct`, `settings-registry-class`, `settings-templates`, `frontend-settings-panel`, `frontend-sse-client`, `sessions-persistence`, `sessions-lifecycle`, `rag-cache-layer`, `mem-pgvector-setup`, `triage-micro-voter`, `triage-pre-filter`, `prompt-marketplace-wire`, `prompt-enums`, `git-session-init`, `git-merge-manager`, `gap-events-missing-ns`, `gap-cache-wiring`
- Common failure pattern in the sample: descriptions often named the subsystem and expected outcome, but omitted numbered steps, validation, and explicit dependency/precondition language.

## B — Owner .md Files

| File | Rating | Missing |
|---|---|---|
| `src/css/core/db/models/postgres-models.md` | ⚠️ Partial | Missing exact `src/...py` paths for many pending edits; lacks numbered implementation steps and method signatures for pending Phase 40 lanes. |
| `src/css/core/db/postgres-db.md` | ⚠️ Partial | Has exact path examples and DB rules, but mixes historical audit prose with current work; method signatures and per-todo implementation steps are still missing. |
| `src/css/core/marketplace/marketplace.md` | ❌ Thin | No exact Python path inventory for runtime files, no numbered implementation contract, and only a small subset of relevant todo IDs are referenced. |
| `src/css/core/memory/memory.md` | ⚠️ Partial | Strong file/class inventory and validation notes, but step-by-step contracts are prose-only and only a subset of pending Phase 20 todo IDs are tracked. |
| `src/css/core/accounts/accounts.md` | ❌ Thin | Three-file overview only; no todo IDs, no method signatures, and no numbered execution contract. |
| `src/css/core/auth/auth.md` | ⚠️ Partial | Numbered requirements exist, but there are no owned todo IDs and the package-ownership guidance conflicts with the pending auth todo path. |
| `src/css/core/events/events.md` | ✅ Rich | Package layout, symbols, API examples, checklist-owned todo IDs, acceptance gates, and current-state notes are detailed enough to implement without follow-up questions. |
| `src/css/core/types/types.md` | ❌ Thin | Large but stale: old Pydantic/entity audit content dominates, and the pending QoL todo map is not backed by current file-level implementation contracts. |
| `src/css/core/sdks/sdks.md` | ⚠️ Partial | Good file/class inventory, provider-priority contract, and todo status list; still lacks exact `src/...` paths for every pending file and explicit validation steps. |
| `src/css/core/resilience/resilience.md` | ❌ Thin | Architecture summary only; no owned todo ID table, no exact routing package file map, and no validation contract per pending routing todo. |
| `src/css/core/settings/settings.md` | ⚠️ Partial | Exact file layout, APIs, DB schema, and todo IDs are strong, but implementation sequencing is not step-by-step and the document includes partially stale ownership/completion notes. |
| `src/css/core/prompt_cache/prompt_cache.md` | ⚠️ Partial | Clear flow and todo map, but no exact file inventory, no method signatures, and blocked/deferred state is not reflected in the todo table. |
| `src/css/core/rag_vector/rag_vector.md` | ⚠️ Partial | Current files, routes, and todo IDs are named, yet implementation order and validation remain high-level prose. |
| `src/css/core/rag_graph/rag_graph.md` | ❌ Thin | Conceptual package note only; no exact Python file list, no class/method signatures, and no owner status table. |
| `src/css/core/asgi/asgi.md` | ⚠️ Partial | Topology and transport boundaries are clear, but only a few concrete files are named and the todo mapping lacks per-file/method contracts. |
| `src/css/core/otel/plan.md` | ⚠️ Partial | File list, stream contract, and todo IDs exist, but the document includes stale stack guidance (`requirements.txt`, Jaeger, SQLAlchemy) and lacks final file-level detail. |
| `src/css/modules/agents/agents.md` | ❌ Thin | Mostly checklist/audit prose; no owner todo IDs, stale `project_dir` naming, and no concrete file/method contract for pending work. |
| `src/css/modules/triage/triage.md` | ⚠️ Partial | Detailed narrative and examples, but only a small subset of pending todo IDs are tracked and several type/model examples are stale. |
| `src/css/modules/sessions/sessions.md` | ❌ Thin | High-level lifecycle notes only; no file map, no class signatures, and no todo IDs for pending session/git work. |
| `src/css/modules/hooks/hooks.md` | ⚠️ Partial | Specific runtime notes and completed todo mapping exist, but there is no pending owner todo coverage and no per-file execution sequence. |
| `src/css/modules/mcps/mcps.md` | ⚠️ Partial | Useful file status table and todo map, but filenames are relative, signatures are sparse, and there is no numbered implementation order. |
| `src/css/modules/projects/projects.md` | ⚠️ Partial | File layout, DB schema, API signatures, and todo IDs are useful, but `~/.css` filesystem paths and session-output ownership language are stale. |
| `src/css/modules/workflows/workflows.md` | ❌ Thin | Conceptual only; no exact files, symbols, or todo cross-references for Phase 30 work. |
| `src/css/modules/chat/chat.md` | ⚠️ Partial | Some concrete files and frontend todo references are present, but the checklist is generic and part of it is stale versus existing template files. |
| `src/css/api_services/api_services.md` | ❌ Thin | Extensive provider catalog, but little exact file ownership for pending todos and almost no stepwise implementation contract. |

### Details per file (for ⚠️ and ❌ only)
- `src/css/core/db/models/postgres-models.md` — ⚠️ Partial: Missing exact `src/...py` paths for many pending edits; lacks numbered implementation steps and method signatures for pending Phase 40 lanes.
- `src/css/core/db/postgres-db.md` — ⚠️ Partial: Has exact path examples and DB rules, but mixes historical audit prose with current work; method signatures and per-todo implementation steps are still missing.
- `src/css/core/marketplace/marketplace.md` — ❌ Thin: No exact Python path inventory for runtime files, no numbered implementation contract, and only a small subset of relevant todo IDs are referenced.
- `src/css/core/memory/memory.md` — ⚠️ Partial: Strong file/class inventory and validation notes, but step-by-step contracts are prose-only and only a subset of pending Phase 20 todo IDs are tracked.
- `src/css/core/accounts/accounts.md` — ❌ Thin: Three-file overview only; no todo IDs, no method signatures, and no numbered execution contract.
- `src/css/core/auth/auth.md` — ⚠️ Partial: Numbered requirements exist, but there are no owned todo IDs and the package-ownership guidance conflicts with the pending auth todo path.
- `src/css/core/types/types.md` — ❌ Thin: Large but stale: old Pydantic/entity audit content dominates, and the pending QoL todo map is not backed by current file-level implementation contracts.
- `src/css/core/sdks/sdks.md` — ⚠️ Partial: Good file/class inventory, provider-priority contract, and todo status list; still lacks exact `src/...` paths for every pending file and explicit validation steps.
- `src/css/core/resilience/resilience.md` — ❌ Thin: Architecture summary only; no owned todo ID table, no exact routing package file map, and no validation contract per pending routing todo.
- `src/css/core/settings/settings.md` — ⚠️ Partial: Exact file layout, APIs, DB schema, and todo IDs are strong, but implementation sequencing is not step-by-step and the document includes partially stale ownership/completion notes.
- `src/css/core/prompt_cache/prompt_cache.md` — ⚠️ Partial: Clear flow and todo map, but no exact file inventory, no method signatures, and blocked/deferred state is not reflected in the todo table.
- `src/css/core/rag_vector/rag_vector.md` — ⚠️ Partial: Current files, routes, and todo IDs are named, yet implementation order and validation remain high-level prose.
- `src/css/core/rag_graph/rag_graph.md` — ❌ Thin: Conceptual package note only; no exact Python file list, no class/method signatures, and no owner status table.
- `src/css/core/asgi/asgi.md` — ⚠️ Partial: Topology and transport boundaries are clear, but only a few concrete files are named and the todo mapping lacks per-file/method contracts.
- `src/css/core/otel/plan.md` — ⚠️ Partial: File list, stream contract, and todo IDs exist, but the document includes stale stack guidance (`requirements.txt`, Jaeger, SQLAlchemy) and lacks final file-level detail.
- `src/css/modules/agents/agents.md` — ❌ Thin: Mostly checklist/audit prose; no owner todo IDs, stale `project_dir` naming, and no concrete file/method contract for pending work.
- `src/css/modules/triage/triage.md` — ⚠️ Partial: Detailed narrative and examples, but only a small subset of pending todo IDs are tracked and several type/model examples are stale.
- `src/css/modules/sessions/sessions.md` — ❌ Thin: High-level lifecycle notes only; no file map, no class signatures, and no todo IDs for pending session/git work.
- `src/css/modules/hooks/hooks.md` — ⚠️ Partial: Specific runtime notes and completed todo mapping exist, but there is no pending owner todo coverage and no per-file execution sequence.
- `src/css/modules/mcps/mcps.md` — ⚠️ Partial: Useful file status table and todo map, but filenames are relative, signatures are sparse, and there is no numbered implementation order.
- `src/css/modules/projects/projects.md` — ⚠️ Partial: File layout, DB schema, API signatures, and todo IDs are useful, but `~/.css` filesystem paths and session-output ownership language are stale.
- `src/css/modules/workflows/workflows.md` — ❌ Thin: Conceptual only; no exact files, symbols, or todo cross-references for Phase 30 work.
- `src/css/modules/chat/chat.md` — ⚠️ Partial: Some concrete files and frontend todo references are present, but the checklist is generic and part of it is stale versus existing template files.
- `src/css/api_services/api_services.md` — ❌ Thin: Extensive provider catalog, but little exact file ownership for pending todos and almost no stepwise implementation contract.

## C — Cross-consistency gaps

| Todo ID | Owner doc | Gap |
|---|---|---|
| `auth-jwt-module` | `src/css/core/auth/auth.md` | Todo says to create `modules/auth/`; owner doc says `src/css/core/auth/` is the current canonical runtime and explicitly says not to create a second auth package until ownership is reconciled. |
| `frontend-chat-panel` | `src/css/modules/chat/chat.md` | Todo says to create `src/css/modules/chat/templates/index.tsx`; owner doc already says that file exists as scaffold, so the todo wording is stale. |
| `cache-gemini-context-cache` | `src/css/core/prompt_cache/prompt_cache.md` | Todo is deferred/blocked, but the owner doc still lists it in the active Phase 11 todo table with no blocked/deferred marker. |
| `telemetry-collector` | `src/css/core/otel/plan.md` | Todo points to `core/telemetry/collector.py`; owner doc frames the area as `src/css/core/otel/` with a different file set, so path ownership is inconsistent. |
| `settings-config-import-cutover` | `src/css/core/settings/settings.md` | Owner doc says a 2026-05-25 import cleanup already repaired `css.config` consumers, but the todo remains pending without saying what import work is still left. |
| `db40-menu-menuid-endpoints` | `src/css/core/db/models/postgres-models.md` | Todo asks for menu_id-aware retrieval endpoints; owner doc names menu symbols but never identifies the endpoint file or function to edit. |
| `db40-lane-marketplace` | `src/css/core/marketplace/marketplace.md` | Todo names the dual-file reconciliation scope, but owner doc stops at boundary prose and does not say which classes from `marketplace.py` must survive the merge. |
| `rag-context-wire` | `src/css/core/rag_vector/rag_vector.md + src/css/core/rag_graph/rag_graph.md` | Todo requires wiring retrieval into `ContextAssembler`, but neither owner doc names the concrete assembler file or method signature. |
| `sdk-browser-relay-provider-priority` | `src/css/core/sdks/sdks.md` | Priority order matches, but the owner doc never identifies the concrete adapter/router file that should implement the fallback chain. |
| `triage-memory-tagger` | `src/css/modules/triage/triage.md` | Todo names `modules/triage/memory_tagger.py` and `MemoryTagger.tag(...)`; owner doc mentions tagging after writes but does not name that file or class. |

## Recommended Actions (priority order)
1. Rewrite the 6 sub-100-char todos first, then batch-rewrite the 89 todos under 200 chars with no file path; these are the fastest high-impact fixes.
2. Apply one required todo-description template in `session.db`: exact `src/...` paths, named symbols, numbered steps, validation block, and explicit dependencies/preconditions.
3. Normalize owner docs to the same template: file map, symbol/method signatures, numbered contract, owned todo ID table, and a live status-sync note pulled from `session.db`.
4. Resolve the path/ownership contradictions called out in section C first (`auth`, `chat`, `otel/telemetry`, `settings` import cleanup), then update both tracker text and owner docs together.
5. Prioritize the thinnest owner docs for enrichment: `core/types`, `core/marketplace`, `core/accounts`, `core/resilience`, `core/rag_graph`, `modules/agents`, `modules/sessions`, `modules/workflows`, and `api_services`.

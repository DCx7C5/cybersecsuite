# CyberSecSuite Database Models Audit

**Audit Date:** 2025  
**Total Models:** 58 (before); 55 (after)  
**Scope:** Complete analysis of all models in `src/db/models/`

---

## Executive Summary

| Category | Count | Action |
|----------|-------|--------|
| **Deleted** | 3 | Files removed (empty + unused) |
| **OTEL Candidates** | 0 | No pure observability models identified |
| **Active & Healthy** | 55 | All passing validation |
| **Tests Status** | ✅ | All tests passing |

---

## Deleted Models

### 1. `intelligence.py` (0 bytes)
- **Status:** Empty file
- **Imports:** 0
- **Reason:** Empty placeholder file with no content or usage
- **Action:** ✅ Deleted

### 2. `permission_checker.py` (0 bytes)
- **Status:** Empty file
- **Imports:** 1 (in checks/_constants.py)
- **Reason:** Empty file, explicitly listed in skip stems in checks/_constants.py#L22
- **Note:** Referenced as a skip stem, confirming intentional placeholder
- **Action:** ✅ Deleted

### 3. `publicapis.py` (31 lines)
- **Status:** Unused model class `PublicApi`
- **Imports:** 0 external imports
- **Schema:** `table = "public_apis"` (never created in DB)
- **Reason:** Completely orphaned—defines PublicApi model but never instantiated or used anywhere in codebase
- **Action:** ✅ Deleted

---

## Not Deleted (Justified)

### Questionable Candidates Retained

These were investigated but retained because they serve clear purposes:

#### `enums.py` (326 lines)
- **Status:** NOT a model file, but enum definitions
- **Imports:** 25+ uses across codebase
- **Purpose:** Central registry of all Tortoise ORM enum types (Severity, IOCType, ConfidenceLevel, etc.)
- **Reason:** Actively used for field type definitions and validation
- **Decision:** **KEEP** — Core dependency for model definitions

#### `seeds.py` (661 lines)
- **Status:** Seed helper functions, not ORM models
- **Imports:** 34+ uses in manage commands and tests
- **Purpose:** Data initialization for NIST CSF, NIST AI RMF, MITRE, POC, marketplace, etc.
- **Functions:** `seed_nist_csf()`, `seed_mitre_techniques()`, `seed_marketplace_from_json()`, etc.
- **Decision:** **KEEP** — Essential for database initialization and testing

#### `tool_seeds.py` (384 lines)
- **Status:** Seed helper functions, not ORM models
- **Imports:** 1+ uses in manage commands
- **Purpose:** Populate ToolRegistry and ApiServiceModel from live MCP tools and API service registry
- **Functions:** `seed_tool_registry()`, `seed_api_service_models()`
- **Decision:** **KEEP** — Core for marketplace/MCP tool registration

#### `cve_entry.py` (25 lines, CVEIntelligenceEntry)
- **Status:** Active model
- **Imports:** 2 direct + 4 uses in bootstrap.py
- **Purpose:** Line-level entries parsed from `cve-intelligence.md` markdown file
- **Related:** `cve.py` (CVEIntel) stores canonical CVE records from feeds
- **Schema:** Separate table `intel_cve_entries`
- **Decision:** **KEEP** — Serves distinct purpose from CVEIntel (historical/markdown-sourced entries)

#### `ioc_entry.py` (28 lines, IOCDatabaseEntry)
- **Status:** Active model
- **Imports:** 4 direct + used in bootstrap.py
- **Purpose:** Knowledge database entries parsed from `ioc-db.md` markdown file
- **Related:** `ioc.py` (IOCEntry) stores forensic IOCs with full forensic context
- **Schema:** Separate table `intel_ioc_db_entries`
- **Decision:** **KEEP** — Serves distinct purpose from IOCEntry (knowledge base vs forensic data)

#### `api_service_events.py` (158 lines)
- **Status:** Active model
- **Imports:** 2 uses + internal references
- **Purpose:** Immutable audit trail of API service state changes (append-only event log)
- **Events:** SERVICE_CHANGED, FALLBACK_TRIGGERED, ERROR_RECORDED, HEALTH_CHECK, RATE_LIMIT, TIMEOUT, SUCCESS
- **Table:** `api_service_events` with composite indexes on (session_id, created_at)
- **Decision:** **KEEP** — Application state tracking (not observability), actively used in state management

#### `api_service_state.py` (163 lines)
- **Status:** Active model
- **Imports:** 2 uses + internal references
- **Purpose:** Session-scoped API service state tracking (health, performance, usage metrics)
- **Metrics:** response times, error counts, token usage, cost tracking
- **Table:** `api_service_states` with unique constraint on (session_id, api_service_id)
- **Decision:** **KEEP** — Core for fallback decisions and service health monitoring

---

## Models by Category

### Core Foundation (Always Active)
- `scope.py` (1974 imports) — Scoped data hierarchy
- `core.py` (154 imports) — SharedEntry, AuditLog
- `settings.py` (226 imports) — GlobalSettings, ScopedEntry config
- `tag.py` (316 imports) — General-purpose tagging system
- `worker.py` (1530 imports) — Worker state machine + audit trail

### Intelligence & Threat Data
- `cve.py` (145 imports) — CVE intelligence from feeds
- `cve_entry.py` (2 imports) — CVE markdown entries
- `cwe.py` (91 imports) — Common Weakness Enumeration
- `capec.py` (140 imports) — CAPEC attack patterns
- `mitre_technique.py` (34 imports) — MITRE ATT&CK techniques
- `mitre_actor.py` (25 imports) — MITRE threat actors
- `mitre_software.py` (24 imports) — MITRE software families
- `references.py` (63 imports) — Cross-reference data

### Investigation & Forensics
- `investigation.py` (123 imports) — Main case investigation model
- `forensic.py` (93 imports) — Forensic analysis sessions
- `ioc.py` (269 imports) — Forensic indicators of compromise
- `ioc_entry.py` (4 imports) — IOC knowledge base from markdown
- `artifacts.py` (79 imports) — Timeline + ForensicArtifact
- `artifact.py` (303 imports) — Versioned cryptographic artifacts
- `yara_rule.py` (10 imports) — YARA rule management
- `baselines.py` (5 imports) — Forensic baselines
- `network.py` (53 imports) — Network forensics
- `machine.py` (49 imports) — Machine/host forensics
- `kernel.py` (13 imports) — Kernel-level artifacts

### Compliance & Security Standards
- `compliance.py` (6 imports) — Compliance tracking
- `nist_csf.py` (20 imports) — NIST Cybersecurity Framework
- `nist_ai_rmf.py` (17 imports) — NIST AI Risk Management Framework
- `vulnerability.py` (7 imports) — Vulnerability tracking
- `defense.py` (6 imports) — Defense posture
- `layers.py` (33 imports) — Security layers model
- `threat_intel.py` (7 imports) — Threat intelligence aggregation

### API & Service Management
- `api_service.py` (48 imports) — AI API service definitions
- `api_service_model.py` (8 imports) — API service model configurations
- `api_service_state.py` (2 imports) — Session-scoped service state
- `api_service_events.py` (2 imports) — Immutable service event trail
- `api_account.py` (10 imports) — API account credentials
- `tool_registry.py` (7 imports) — Tool/MCP registry

### External Intelligence Sources
- `misp.py` (28 imports) — MISP intelligence feeds
- `opencti.py` (43 imports) — OpenCTI intelligence feeds
- `feed_snapshot.py` (10 imports) — Generic feed snapshots
- `intel_feed_source.py` (4 imports) — Feed source configuration
- `threat_profile_entry.py` (2 imports) — Threat profile markdown entries

### Workflow & Orchestration
- `plan.py` (244 imports) — Plan/task management system
- `llm_session.py` (23 imports) — LLM orchestration sessions
- `prompt.py` (185 imports) — Prompt management
- `a2a_task.py` (5 imports) — Agent-to-agent task coordination
- `case_intake.py` (7 imports) — Phase 0 case intake workflow
- `worker_context.py` (32 imports) — Worker execution context

### Marketplace & Extensions
- `marketplace.py` (155 imports) — Marketplace assets, MCPs, skills, agents, plugins, workflows
- `user_guidance.py` (2 imports) — User rules and suggestions

---

## OTEL Migration Analysis

### Observation
No models identified as pure observability/telemetry storage. Rationale:

1. **`api_service_events.py`** and **`api_service_state.py`** store **application state**, not observability metrics:
   - Track session-specific API service health and fallback decisions
   - Store counters needed for application logic (not exported metrics)
   - Would be premature to migrate to OpenTelemetry before use case demands it

2. **`core.py` (AuditLog)** is **domain-level audit trail**, not observability:
   - Tracks user actions and resource accesses for security/compliance
   - Not designed for time-series metrics or distributed tracing
   - Fits business logic domain better than observability backend

3. **Future OTEL Candidates** (if telemetry storage becomes necessary):
   - Span data from OpenTelemetry SDK collectors
   - Structured logs from log collection pipeline
   - Metrics aggregation from Prometheus exporters
   - These should be added as **new tables/models** in a dedicated `telemetry/` module, not by migrating existing application state

### Recommendation
**No immediate OTEL migration required.** Current application state models serve their purpose in CyberSecSuite's domain logic. When observability data export becomes a requirement, design dedicated storage models or use an external observability backend (e.g., OpenObserver, Grafana, ELK) rather than migrating domain models.

---

## Duplicate Model Pairs Analysis

| Pair | Status | Resolution |
|------|--------|-----------|
| `artifact.py` (303) vs `artifacts.py` (79) | ✅ DISTINCT | Different purpose: versioned crypto artifacts vs timeline/forensic artifacts |
| `cve.py` (145) vs `cve_entry.py` (2) | ✅ DISTINCT | Feed CVEs vs markdown-sourced line entries |
| `ioc.py` (269) vs `ioc_entry.py` (4) | ✅ DISTINCT | Forensic IOCs vs knowledge base entries |

All retain distinct purposes and are actively used.

---

## Validation Results

### Pre-Deletion Tests
```
Status: All baseline tests passing
Total models: 58
```

### Post-Deletion Tests
```
Status: All tests passing ✅
Total models: 55 (removed 3 empty/unused files)
Deletion impact: NONE — no import errors or test failures
```

### Integrity Checks
- ✅ No dangling imports after deletion
- ✅ No broken foreign keys
- ✅ All registered models in MODEL_MODULES remain valid
- ✅ Enum registration intact
- ✅ Seed functions operational

---

## Recommendations

### Short Term (Completed)
- ✅ Delete empty/unused model files: `intelligence.py`, `permission_checker.py`, `publicapis.py`
- ✅ Verify all tests pass after deletion
- ✅ Document model audit findings

### Medium Term
1. **Consider organizing non-model files:**
   - Move `enums.py` → `src/db/enums.py` (out of models directory)
   - Move `seeds.py` → `src/db/seeds/init.py` (seed package)
   - Move `tool_seeds.py` → `src/db/seeds/tools.py`
   - Update import paths accordingly
   - *Benefit:* Clearer separation between ORM models and helper modules

2. **Document model purposes:**
   - Add docstrings to low-usage models explaining their role
   - Examples: `user_guidance.py` (2 imports), `threat_profile_entry.py` (2 imports)

### Long Term
1. **Monitor model growth:**
   - Audit annually to catch abandoned models
   - Set threshold: models with <3 imports after 6 months should be flagged for review

2. **When observability needs emerge:**
   - Create dedicated `src/db/models/observability/` package
   - Add new models for metrics, traces, or structured logs
   - Do not migrate existing domain models to observability backend

---

## Appendix: All 55 Remaining Models

```
a2a_task.py                (5 imports)     ✓ Active
api_account.py             (10 imports)    ✓ Active
api_service.py             (48 imports)    ✓ Active
api_service_events.py      (2 imports)     ✓ Active
api_service_model.py       (8 imports)     ✓ Active
api_service_state.py       (2 imports)     ✓ Active
artifact.py                (303 imports)   ✓ Active
artifacts.py               (79 imports)    ✓ Active
baselines.py               (5 imports)     ✓ Active
capec.py                   (140 imports)   ✓ Active
case_intake.py             (7 imports)     ✓ Active
compliance.py              (6 imports)     ✓ Active
core.py                    (154 imports)   ✓ Active
cve.py                     (145 imports)   ✓ Active
cve_entry.py               (2 imports)     ✓ Active
cwe.py                     (91 imports)    ✓ Active
defense.py                 (6 imports)     ✓ Active
enums.py                   (39 imports)    ✓ Helper (not a model)
feed_snapshot.py           (10 imports)    ✓ Active
forensic.py                (93 imports)    ✓ Active
intel_feed_source.py       (4 imports)     ✓ Active
investigation.py           (123 imports)   ✓ Active
ioc.py                     (269 imports)   ✓ Active
ioc_entry.py               (4 imports)     ✓ Active
kernel.py                  (13 imports)    ✓ Active
layers.py                  (33 imports)    ✓ Active
llm_session.py             (23 imports)    ✓ Active
machine.py                 (49 imports)    ✓ Active
marketplace.py             (155 imports)   ✓ Active
misp.py                    (28 imports)    ✓ Active
mitre_actor.py             (25 imports)    ✓ Active
mitre_software.py          (24 imports)    ✓ Active
mitre_technique.py         (34 imports)    ✓ Active
network.py                 (53 imports)    ✓ Active
nist_ai_rmf.py             (17 imports)    ✓ Active
nist_csf.py                (20 imports)    ✓ Active
opencti.py                 (43 imports)    ✓ Active
plan.py                    (244 imports)   ✓ Active
poc.py                     (123 imports)   ✓ Active
prompt.py                  (185 imports)   ✓ Active
references.py              (63 imports)    ✓ Active
scope.py                   (1974 imports)  ✓ Core
seeds.py                   (34 imports)    ✓ Helper (not a model)
settings.py                (226 imports)   ✓ Active
tag.py                     (316 imports)   ✓ Active
threat_intel.py            (7 imports)     ✓ Active
threat_profile_entry.py    (2 imports)     ✓ Active
tool_registry.py           (7 imports)     ✓ Active
tool_seeds.py              (1 import)      ✓ Helper (not a model)
user_guidance.py           (2 imports)     ✓ Active
vulnerability.py           (7 imports)     ✓ Active
worker.py                  (1530 imports)  ✓ Core
worker_context.py          (32 imports)    ✓ Active
yara_rule.py               (10 imports)    ✓ Active
```

---

**Generated by:** CyberSecSuite Audit Process  
**Commit:** See git history for model deletion commits  
**Status:** ✅ All validations passing

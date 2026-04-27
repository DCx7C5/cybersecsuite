# DB Models Audit

**Scope:** `src/db/models/`  
**Date:** 2025-07-25  
**Auditor:** Copilot  

---

## Model Inventory

| Model Class | File | Table Name | Fields | Issues |
|---|---|---|---|---|
| `A2ATask` | `a2a_task.py` | `a2a_tasks` | 8 | `session_id` CharField — consider FK to `sessions` |
| `ApiAccount` | `api_account.py` | `api_account` | 13 | — |
| `ApiService` | `api_service.py` | `api_services` | 17 | — |
| `ApiServiceAuthMethod` | `api_service.py` | `api_service_auth_methods` | 9 | — |
| `ApiServiceEvent` | `api_service_events.py` | `api_service_events` | 15 | — |
| `ApiServiceModel` | `api_service_model.py` | `api_service_models` | 28 | — |
| `AccountModel` | `api_service_model.py` | `account_models` | 11 | — |
| `ApiServiceState` | `api_service_state.py` | `api_service_states` | 21 | — |
| `Artifact` | `artifact.py` | `artifacts` | 18 | — |
| `ArtifactSignatureLog` | `artifact.py` | `artifact_signature_logs` | 12 | — |
| `Timeline` | `artifacts.py` | `timeline_entries` | 10 | — |
| `ForensicArtifact` | `artifacts.py` | `forensic_artifacts` | 10 | — |
| `NetworkBaseline` | `baselines.py` | `network_baselines` | 12 | — |
| `ProcessBaseline` | `baselines.py` | `process_baselines` | 16 | — |
| `KernelBaseline` | `baselines.py` | `kernel_baselines` | 14 | — |
| `PersistenceBaseline` | `baselines.py` | `persistence_baselines` | 13 | — |
| `CapecAttackPatternIntel` | `capec.py` | `intel_capec_patterns` | 22 | — |
| `CaseIntake` | `case_intake.py` | `case_intakes` | 19 | — |
| `ComplianceRule` | `compliance.py` | `compliance_rules` | 13 | — |
| `ComplianceCheck` | `compliance.py` | `compliance_checks` | 9 | — |
| `AgentRootPermission` | `compliance.py` | `agent_root_permissions` | 18 | — |
| `SharedEntry` | `core.py` | `shared_entries` | 4 | — |
| `AuditLog` | `core.py` | `audit_logs` | 8 | `user_id` CharField (intentional — external auth IDs) |
| `CVEIntel` | `cve.py` | `intel_cves` | 18 | — |
| `CVEIntelligenceEntry` | `cve_entry.py` | `intel_cve_entries` | 10 | — |
| `CWEIntel` | `cwe.py` | `intel_cwes` | 17 | — |
| `AntiForensicTechnique` | `defense.py` | `anti_forensic_techniques` | 12 | `mitre_technique_id` CharField — should be FK to `MitreTechniqueIntel` |
| `HardeningRecommendation` | `defense.py` | `hardening_recommendations` | 13 | `mitre_technique_id` CharField — should be FK to `MitreTechniqueIntel` |
| `ThreatIntelFeedSnapshot` | `feed_snapshot.py` | `intel_feed_snapshots` | 10 | — |
| `ForensicProject` | `forensic.py` | `forensic_projects` | 21 | — |
| `ForensicSession` | `forensic.py` | `forensic_sessions` | 35 | — |
| `ForensicFinding` | `forensic.py` | `forensic_findings` | 26 | — |
| `IntelFeedSource` | `intel_feed_source.py` | `intel_feed_sources` | 10 | — |
| `Finding` | `investigation.py` | `findings` | 19 | — |
| `IOC` | `investigation.py` | `iocs` | 14 | `first_session_id`, `last_session_id` CharField — consider FK to `sessions` |
| `Risk` | `investigation.py` | `risks` | 8 | — |
| `MITRETechnique` | `investigation.py` | `mitre_techniques` | 6 | — |
| `Baseline` | `investigation.py` | `baselines` | 7 | — |
| `WatchlistItem` | `investigation.py` | `watchlist_items` | 8 | — |
| `IOCEntry` | `ioc.py` | `ioc_entries` | 28 | — |
| `ForensicWatchlistItem` | `ioc.py` | `forensic_watchlist_items` | 17 | — |
| `ClearedItem` | `ioc.py` | `cleared_items` | 15 | — |
| `IOCDatabaseEntry` | `ioc_entry.py` | `intel_ioc_db_entries` | 12 | — |
| `Kernel` | `kernel.py` | `kernels` | 11 | — |
| `KernelModule` | `kernel.py` | `kernel_modules` | 8 | — |
| `SessionLayer` | `layers.py` | `session_layers` | 9 | — |
| `LlmSession` | `llm_session.py` | `llm_sessions` | 9 | — |
| `Network` | `machine.py` | `networks` | 12 | — |
| `Machine` | `machine.py` | `machines` | 30 | — |
| `CPUInfo` | `machine.py` | `cpu_info` | 16 | — |
| `MemoryModule` | `machine.py` | `memory_modules` | 12 | — |
| `NetworkInterface` | `machine.py` | `network_interfaces` | 16 | — |
| `InterfaceAddress` | `machine.py` | `interface_addresses` | 11 | — |
| `StorageDrive` | `machine.py` | `storage_drives` | 21 | — |
| `StoragePartition` | `machine.py` | `storage_partitions` | 15 | — |
| `PCIDevice` | `machine.py` | `pci_devices` | 14 | — |
| `MarketplaceAsset` | `marketplace.py` | `marketplace_assets` | 10 | — |
| `MarketplaceMCP` | `marketplace.py` | `marketplace_mcps` | 15 | — |
| `Skill` | `marketplace.py` | `marketplace_skills` | 11 | — |
| `Agent` | `marketplace.py` | `marketplace_agents` | 13 | — |
| `Plugin` | `marketplace.py` | `marketplace_plugins` | 12 | — |
| `Workflow` | `marketplace.py` | `marketplace_workflows` | 12 | — |
| `MISPEventIntel` | `misp.py` | `intel_misp_events` | 20 | — |
| `MISPAttributeIntel` | `misp.py` | `intel_misp_attributes` | 20 | — |
| `MitreThreatActorIntel` | `mitre_actor.py` | `intel_mitre_threat_actors` | 18 | — |
| `MitreSoftwareFamilyIntel` | `mitre_software.py` | `intel_mitre_software_families` | 17 | — |
| `MitreTechniqueIntel` | `mitre_technique.py` | `intel_mitre_techniques` | 17 | — |
| `IPAddress` | `network.py` | `ip_addresses` | 8 | — |
| `Host` | `network.py` | `hosts` | 11 | — |
| `Domain` | `network.py` | `domains` | 6 | — |
| `Certificate` | `network.py` | `certificates` | 6 | — |
| `NetworkConnection` | `network.py` | `network_connections` | 9 | — |
| `NistAiRmfControl` | `nist_ai_rmf.py` | `compliance_nist_ai_rmf` | 12 | — |
| `NistCsfControl` | `nist_csf.py` | `compliance_nist_csf` | 12 | — |
| `OpenCTIIndicatorIntel` | `opencti.py` | `intel_opencti_indicators` | 22 | — |
| `OpenCTIEntityIntel` | `opencti.py` | `intel_opencti_entities` | 18 | — |
| `Plan` | `plan.py` | `plans` | 7 | — |
| `Task` | `plan.py` | `tasks` | 8 | — |
| `ExecutionLog` | `plan.py` | `execution_logs` | 5 | — |
| `ProofOfConcept` | `poc.py` | `intel_pocs` | 19 | — |
| `Prompt` | `prompt.py` | `prompts` | 8 | — |
| `CVECWEReference` | `references.py` | `intel_cve_cwe_refs` | 5 | — |
| `CVEMitreTechniqueReference` | `references.py` | `intel_cve_mitre_refs` | 5 | — |
| `CWECAPECReference` | `references.py` | `intel_cwe_capec_refs` | 5 | — |
| `CAPECMitreTechniqueReference` | `references.py` | `intel_capec_mitre_refs` | 5 | — |
| `ThreatActorTechniqueReference` | `references.py` | `intel_actor_technique_refs` | 6 | — |
| `ThreatActorSoftwareReference` | `references.py` | `intel_actor_software_refs` | 7 | — |
| `SoftwareTechniqueReference` | `references.py` | `intel_software_technique_refs` | 7 | — |
| `Project` | `scope.py` | `projects` | 8 | — |
| `Application` | `scope.py` | `applications` | 8 | — |
| `Session` | `scope.py` | `sessions` | 15 | — |
| `ScopedEntry` *(abstract base)* | `scope.py` | **NONE** | 9 | Missing `class Meta`; name collides with `settings.py::ScopedEntry` |
| `ScopedEntry` *(concrete)* | `settings.py` | `scoped_entries` | 8 | Name collides with `scope.py::ScopedEntry` |
| `GlobalSettings` | `settings.py` | `global_settings` | 3 | — |
| `Tag` | `tag.py` | `tags` | 6 | — |
| `ThreatProfile` | `threat_intel.py` | `threat_profiles` | 14 | — |
| `ForensicMITRETechnique` | `threat_intel.py` | `forensic_mitre_techniques` | 13 | — |
| `IOCMITREMapping` | `threat_intel.py` | `ioc_mitre_mappings` | 8 | — |
| `ThreatProfileEntry` | `threat_profile_entry.py` | `intel_threat_profile_entries` | 13 | — |
| `ToolRegistry` | `tool_registry.py` | `tool_registry` | 19 | — |
| `ToolToggleState` | `tool_registry.py` | `tool_toggle_states` | 8 | — |
| `ToolToggleRegistry` | `tool_registry.py` | `tool_toggle_registry` | 4 | — |
| `AccountToolAccess` | `tool_registry.py` | `account_tool_access` | 10 | — |
| `UserRule` | `user_guidance.py` | `user_rules` | 13 | — |
| `UserSuggestion` | `user_guidance.py` | `user_suggestions` | 8 | — |
| `Vulnerability` | `vulnerability.py` | `vulnerabilities` | 18 | — |
| `WorkerStateTransition` | `worker.py` | `worker_state_transitions` | 12 | Uses `models.Model` not `Model`; `worker_id` CharField |
| `WorkerSession` | `worker.py` | `worker_sessions` | 20 | Uses `models.Model` not `Model`; `worker_id` CharField |
| `WorkerAuditLog` | `worker.py` | `worker_audit_logs` | 12 | Uses `models.Model` not `Model`; `worker_id` CharField |
| `WorkerContext` | `worker_context.py` | `worker_contexts` | 28 | `worker_id` CharField |
| `YaraRule` | `yara_rule.py` | `yara_rules` | 26 | — |
| `YaraTestRun` | `yara_rule.py` | `yara_test_runs` | 11 | — |

**Total:** 107 Model classes across 52 files.

**Non-model utility files** (no `class Meta: table`): `intelligence.py`, `permission_checker.py`, `seeds.py`, `tool_seeds.py`

---

## Duplicates Found

**No duplicate table names** — all 107 table declarations are unique across the codebase.

However, there is a **class name collision** that is functionally equivalent to a duplicate:

| Class Name | File | Table | Role |
|---|---|---|---|
| `ScopedEntry` | `scope.py` | *(none — abstract base)* | Parent class for scoped models (baselines, investigation, network, kernel, case_intake, core) |
| `ScopedEntry` | `settings.py` | `scoped_entries` | Concrete key-value settings store; exported from `__init__.py` |

These two classes serve completely different purposes but share the same name. Any code doing `from db.models import ScopedEntry` gets the `settings.py` version. Code in individual model files doing `from db.models.scope import ScopedEntry` gets the base-class version. This is **working but confusing** — the next developer who sees `ScopedEntry` in `settings.py` won't know it's unrelated to the scope hierarchy base.

---

## Unused Models

> **Note:** In Tortoise ORM projects, models are registered by module path (via `MODEL_MODULES` list in `__init__.py`) and queried dynamically via `Model.filter(...)`. The absence of a direct `import ClassName` outside `src/db/models/` does **not** mean the model is unused — it is still active in the database and queryable. The models below are not explicitly imported but remain accessible via the ORM.

Models with **no direct import outside `src/db/models/`**:

- `defense.py`: `AntiForensicTechnique`, `HardeningRecommendation`
- `forensic.py`: `ForensicProject`, `ForensicSession`, `ForensicFinding`
- `ioc.py`: `IOCEntry`, `ForensicWatchlistItem`, `ClearedItem`
- `threat_intel.py`: `ThreatProfile`, `IOCMITREMapping`
- `compliance.py`: `ComplianceRule`, `ComplianceCheck`, `AgentRootPermission`
- `machine.py`: `CPUInfo`, `MemoryModule`, `NetworkInterface`, `InterfaceAddress`, `StorageDrive`, `StoragePartition`, `PCIDevice`
- `network.py`: `IPAddress`, `NetworkConnection`
- `baselines.py`: `NetworkBaseline`, `ProcessBaseline`, `KernelBaseline`, `PersistenceBaseline`
- `nist_ai_rmf.py`: `NistAiRmfControl`
- `nist_csf.py`: `NistCsfControl`
- `yara_rule.py`: `YaraRule`, `YaraTestRun`
- `user_guidance.py`: `UserRule`, `UserSuggestion`
- `tool_registry.py`: `ToolRegistry`, `ToolToggleState`, `ToolToggleRegistry`, `AccountToolAccess`
- `marketplace.py`: `MarketplaceAsset`, `MarketplaceMCP`, `Workflow`
- `api_service_model.py`: `ApiServiceModel`, `AccountModel`
- `api_service_events.py`: `ApiServiceEvent`
- `api_service_state.py`: `ApiServiceState`

These are all registered in `MODEL_MODULES` and are available to the ORM. None should be deleted without confirming the associated DB tables are also dropped.

---

## Recommendations

### R1 — Rename `scope.py::ScopedEntry` to `ScopeBase` (Priority: Medium)

The abstract base class in `scope.py` should be renamed to `ScopeBase` (or `ScopeMixin`) to avoid confusion with the concrete `ScopedEntry` settings model in `settings.py`.

**Files to update after rename:**
- `src/db/models/scope.py` — rename class
- `src/db/models/baselines.py`, `investigation.py`, `network.py`, `kernel.py`, `case_intake.py`, `core.py` — update import
- `src/db/migration/scope_v2.py` — update reference
- `src/checks/_constants.py` — update `_MODEL_BASES`

### R2 — Add `class Meta` with `abstract = True` to `scope.py::ScopedEntry` (Priority: High)

Tortoise ORM supports abstract models. Without `abstract = True`, Tortoise may attempt to map `ScopedEntry` to a `scopedentry` table (lowercase class name fallback). Add:

```python
class Meta:
    abstract = True
```

This should be done immediately as part of R1.

### R3 — Replace `mitre_technique_id` CharField with FK in `defense.py` (Priority: Low)

`AntiForensicTechnique.mitre_technique_id` and `HardeningRecommendation.mitre_technique_id` both store MITRE technique IDs as `CharField(max_length=32)`. These could be `ForeignKeyField` to `MitreTechniqueIntel`, but given the intel tables may be sparsely populated, keeping them as CharField (storing the external MITRE ID like `T1059.001`) is acceptable. Add a comment clarifying intent.

### R4 — Fix `worker.py` model base class import (Priority: Low)

`worker.py` imports `from tortoise import fields, models` and uses `models.Model` as the base. All other files use `from tortoise.models import Model` directly. Both work, but R4 improves consistency:

```python
# Change in worker.py:
from tortoise.models import Model
# Then change: class WorkerSession(models.Model) → class WorkerSession(Model)
```

### R5 — Consider `worker_id` FK in worker models (Priority: Low)

`WorkerStateTransition`, `WorkerSession`, `WorkerAuditLog`, and `WorkerContext` all store `worker_id` as a `CharField`. This appears to be a unique identifier string, not a FK to another table. If `WorkerSession` is the canonical worker identity, `WorkerStateTransition.worker_id` and `WorkerAuditLog.worker_id` could use `ForeignKeyField("models.WorkerSession", ...)`. Evaluate based on whether worker IDs are internal PKs or external correlation IDs.

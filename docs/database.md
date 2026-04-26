# Database Architecture — CyberSecSuite

## Overview

CyberSecSuite uses **PostgreSQL** (via Tortoise ORM + asyncpg) as the authoritative data store
for relational and operational data. **OpenObserve** (OO) is the observability sink for all
append-only time-series data (audit logs, API usage, LLM calls, intel update logs).

---

## Model Inventory (~47 ORM models)

| Module                         | Table                                    | Base          | Purpose                          |
|--------------------------------|------------------------------------------|---------------|----------------------------------|
| `scope.py`                     | `projects`, `applications`, `sessions`   | `Model`       | Forensic root anchors            |
| `scope.py`                     | *(abstract)* `ScopedEntry`               | `Model`       | Base for all scoped data         |
| `forensic.py`                  | `forensic_projects`, `forensic_sessions` | `Model`       | Investigation phase bridge       |
| `llm_session.py`               | `llm_sessions`                           | raw asyncpg   | LLM session tracker per worktree |
| `finding.py`                   | `findings`                               | `ScopedEntry` | Vulnerability/security findings  |
| `ioc.py`                       | `iocs`                                   | `ScopedEntry` | Indicators of Compromise         |
| `risk.py`                      | `risks`                                  | `ScopedEntry` | Risk register entries            |
| `case_intake.py`               | `case_intakes`                           | `ScopedEntry` | Case intake records              |
| `artifact.py` / `artifacts.py` | `artifacts`                              | `ScopedEntry` | Evidence artifacts               |
| `compliance.py`                | `compliance_checks`                      | `ScopedEntry` | Compliance verification          |
| `defense.py`                   | `defense_recommendations`                | `ScopedEntry` | Defensive controls               |
| `vulnerability.py`             | `vulnerabilities`                        | `ScopedEntry` | Vulnerability catalogue          |
| `yara_rule.py`                 | `yara_rules`                             | `ScopedEntry` | YARA detection rules             |
| `user_guidance.py`             | `user_guidances`                         | `ScopedEntry` | User-facing guidance             |
| `baselines.py`                 | `baselines`                              | `ScopedEntry` | Security baselines               |
| `threat_intel.py`              | `forensic_iocs`, `threat_profiles`       | `ScopedEntry` | Threat intelligence              |
| `mitre.py`                     | `mitre_techniques`                       | `ScopedEntry` | MITRE ATT&CK techniques          |
| `mitre.py`                     | `mitre_subtechniques`, `mitre_groups`    | `Model`       | MITRE sub-techniques + groups    |
| `cve.py` / `cve_entry.py`      | `cve_entries`                            | `Model`       | CVE catalogue                    |
| `cwe.py`                       | `cwe_entries`                            | `Model`       | CWE weakness catalogue           |
| `capec.py`                     | `capec_entries`                          | `Model`       | CAPEC attack patterns            |
| `nist_csf.py`                  | `nist_csf_*`                             | `Model`       | NIST CSF 2.0 controls            |
| `api_account.py`               | `api_accounts`                           | `Model`       | AI provider accounts             |
| `provider.py`                  | `providers`                              | `Model`       | AI provider registry             |
| `provider_model.py`            | `provider_models`                        | `Model`       | Models per provider              |
| `prompt.py`                    | `prompts`                                | `Model`       | Prompt library                   |
| `poc.py`                       | `pocs`                                   | `Model`       | Proof-of-concept scripts         |
| `a2a_task.py`                  | `a2a_tasks`                              | `Model`       | A2A protocol task queue          |
| `tool_registry.py`             | `tool_registries`                        | `Model`       | MCP tool registry entries        |
| `tag.py`                       | `tags`                                   | `Model`       | Tagging                          |
| `references.py`                | `references`                             | `Model`       | External reference links         |
| `intel_feed_source.py`         | `intel_feed_sources`                     | `Model`       | Threat intel feeds               |
| `feed_snapshot.py`             | `feed_snapshots`                         | `Model`       | Feed ingestion snapshots         |
| `opencti.py`                   | `opencti_entries`                        | `Model`       | OpenCTI indicator bridge         |
| `marketplace.py`               | `marketplace_assets`                     | `Model`       | Unified marketplace asset catalog (Phase 0.5) |
| `marketplace.py`               | `marketplace_mcps`                       | `Model`       | MCP package registry w/ install tracking |
| `marketplace.py`               | `marketplace_skills`                     | `Model`       | Skill discovery index            |
| `marketplace.py`               | `marketplace_agents`                     | `Model`       | AI agent registry                |
| `marketplace.py`               | `marketplace_plugins`                    | `Model`       | Browser plugin registry          |
| `marketplace.py`               | `marketplace_workflows`                  | `Model`       | Workflow template registry       |
| `settings.py`                  | `system_settings`                        | `Model`       | KV system settings               |

---

## OpenObserve Streams (observability data)

All append-only / time-series data lives in OpenObserve, not PostgreSQL.
Streams use daily rollover: `cybersecsuite-<base>-YYYY.MM.DD`.

| Stream base        | Data                           | Writer                                   |
|--------------------|--------------------------------|------------------------------------------|
| `telemetry`        | In-process OTEL metrics        | `openobserve/writer.py`                  |
| `audit`            | Audit trail events             | `manage migrate-audit` (migrated)        |
| `api-usage`        | Per-request token/cost/latency | `manage migrate-api-usage` (migrated)    |
| `llm-calls`        | LLM call details per worktree  | `llm/client.py` via `_oo_index`          |
| `intel-update-log` | Intel feed update log entries  | `db/intel/bootstrap.py` via `bulk_index` |

Per-call LLM detail (tokens, cost, latency, model) is queryable only from OO.
`llm_sessions` in Postgres tracks session-level metadata; `closed_at` is set on
session close but aggregate totals (`total_calls`, `total_cost_usd`, etc.) are
**not** maintained since the `llm_calls` table was dropped.

---

## Session Tables (3 distinct tables — all required)

| Table | Class | Purpose |
|---|---|---|
| `sessions` | `Session` (scope.py) | Forensic root anchor — links project → session |
| `forensic_sessions` | `ForensicSession` (forensic.py) | Investigation phase bridge — links `Session` → `ForensicProject` |
| `llm_sessions` | `LlmSession` (llm_session.py) | LLM cost/token tracker per git worktree (raw asyncpg, not Tortoise) |

These three tables serve completely different purposes. They must not be merged or deduplicated.

---

## ScopedEntry Base Class — 5-Level Scope (T045 / scope_v2)

`ScopedEntry` (in `scope.py`) is the abstract base for all forensic data tables.

### Columns

| Column          | Type                | Purpose                                                  |
|-----------------|---------------------|----------------------------------------------------------|
| `project_id`    | FK → `projects`     | Project scope                                            |
| `session_id`    | FK → `sessions`     | Session scope                                            |
| `runtime_id`    | `VARCHAR(64)`       | Container/pod runtime identity                           |
| `worktree_path` | `VARCHAR(1024)`     | Absolute path to `.css/<runtime-id>/worktree-<SID>/`     |
| `scope_level`   | `VARCHAR(16)`       | One of: `global`, `app`, `project`, `runtime`, `session` |
| `created_at`    | Datetime            | Record creation                                          |
| `updated_at`    | Datetime            | Last update                                              |
| `is_active`     | Boolean             | Soft-delete flag                                         |
| `deleted_at`    | Datetime (nullable) | Soft-delete timestamp                                    |

### Applying the migration

The `scope_v2` migration adds `runtime_id`, `worktree_path`, and `scope_level` to all
ScopedEntry-derived tables using `ALTER TABLE … ADD COLUMN IF NOT EXISTS` (idempotent):

```bash
uv run python -m db.migration.scope_v2
```

Tables covered by the migration: `findings`, `iocs`, `risks`, `mitre_techniques`,
`case_intakes`, `shared_entries`, `artifacts`, `audit_logs`, `compliance_checks`,
`defense_recommendations`, `vulnerabilities`, `yara_rules`, `user_guidances`,
`baselines`, `forensic_iocs`, `threat_profiles`.

---

## OpenSearch (optional secondary index)

PostgreSQL is always the source of truth. OpenSearch provides full-text search
on three high-volume tables:

| Index                 | Postgres table | Mapping file                    |
|-----------------------|----------------|---------------------------------|
| `cybersec-findings`   | `findings`     | `src/db/opensearch/mappings.py` |
| `cybersec-iocs`       | `iocs`         | `src/db/opensearch/mappings.py` |
| `cybersec-audit-logs` | `audit_logs`   | `src/db/opensearch/mappings.py` |

### Setup

```python
from db.opensearch import ensure_indices
ensure_indices(host="localhost", port=9200)
```

### Mirroring records

```python
from db.opensearch import sync_finding, sync_ioc, sync_audit_log

sync_finding(finding.to_dict())
sync_ioc(ioc.to_dict())
sync_audit_log(log.to_dict())
```

`opensearch-py` is an optional dependency. The helpers raise `ImportError` if it
is not installed: `uv add opensearch-py`

---

## Enum Reference

All enums live in `src/db/models/enums.py` (single block, no duplicates as of T048).

Key enums:

| Enum              | Values                                                                         |
|-------------------|--------------------------------------------------------------------------------|
| `Severity`        | `critical`, `high`, `medium`, `low`, `info`                                    |
| `RedBlueMode`     | `blue`, `red`, `purple`                                                        |
| `SessionPhase`    | `reconnaissance`, `scanning`, `exploitation`, `post_exploitation`, `reporting` |
| `ModelTier`       | `free`, `paid`, `enterprise`                                                   |
| `ToggleScopeType` | `global`, `project`, `session`                                                 |
| `PocStatus`       | `unverified`, `verified`, `weaponized`, `patched`, `disputed`                  |

---

## Environment Variables

```env
CYBERSEC_DB_HOST=localhost
CYBERSEC_DB_PORT=5432
CYBERSEC_DB_USER=cybersec
CYBERSEC_DB_PASSWORD=<secret>
CYBERSEC_DB_NAME=cybersec_forensics
```

---

## Bootstrap

```bash
# Start PostgreSQL
docker-compose up -d db

# Initialise schema (Tortoise generates tables)
uv run python -m manage seed-all

# Apply scope_v2 columns (idempotent)
uv run python -m db.migration.scope_v2
```

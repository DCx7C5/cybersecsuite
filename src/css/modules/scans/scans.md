# @scans — Module Notes

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Scan orchestration, scan results, and finding persistence.

## Current State

Module is active and mounted at runtime. It owns scan orchestration domain models and API routes under `/api/scans`.

Primary responsibilities are:
- scan request lifecycle
- result persistence
- finding surfacing for downstream incident/compliance modules

## Remaining Contract

| Work area | Required behavior |
|-----------|-------------------|
| Orchestration | Execute a scan request through the selected tool/agent path and persist status transitions rather than leaving scans as passive rows. |
| Findings | Normalize finding severity and target evidence so incidents, reports, and compliance can consume stable records. |
| Security | Scope reads and execution requests to the authorized organization/session boundary. |

## Validation

- Cover create-to-complete/fail status changes and finding retrieval.
- Verify downstream incident/report consumers can resolve persisted findings.

## Local Rules

- ORM table models inherit `css.core.db.models.base.BaseModel`
- Module-owned `Enum` classes live in `enums.py`
- Module documentation in `src/css/modules/` uses the same-name file rule: `scans/scans.md`

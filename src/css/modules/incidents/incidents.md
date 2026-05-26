# @incidents — Module Notes

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Incident lifecycle management, timelines, and linked incident tasks.

## Current State

Implemented HTTP API (`/api/incidents`) for:
- incident CRUD
- timeline event append/list
- incident task create/list/update

Authorization enforces org ownership via `X-Org-ID` header matching request `org_id`.

## Remaining Contract

| Work area | Required behavior |
|-----------|-------------------|
| Domain lifecycle | Maintain severity/status transitions, timeline appends, and linked incident tasks under the incident's organization. |
| Alert bridge | High/critical incident creation or escalation must emit the domain event consumed by alert/notification fan-out. |
| Evidence/report bridge | Expose stable incident identifiers and timeline data for evidence linking and report generation. |

## Validation

- Cover organization isolation, legal lifecycle transitions, and timeline ordering.
- Cover alert emission for high-severity incidents and report/evidence read integration.

## Local Rules

- ORM table models inherit `css.core.db.models.base.BaseModel`
- Module-owned `Enum` classes live in `enums.py`
- Module documentation in `src/css/modules/` uses the same-name file rule: `incidents/incidents.md`

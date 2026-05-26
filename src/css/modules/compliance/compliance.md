# @compliance — Module Notes

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Compliance frameworks, control mappings, and compliance report generation.

## Current State

Implemented HTTP API (`/api/compliance`) for:
- framework CRUD
- control creation/listing
- mapping create/update/list
- report generation and listing

Authorization enforces org ownership via `X-Org-ID` header matching request `org_id`.

## Remaining Contract

| Work area | Required behavior |
|-----------|-------------------|
| Framework seeding | Seed supported framework/control fixtures deterministically and idempotently. |
| Evidence mapping | Map controls to evidence without leaking records across organization boundaries. |
| Dashboard/reporting | Produce coverage summaries and reports from persisted mappings and control states. |

## Validation

- Verify idempotent framework seeding, organization isolation, mapping updates, and reproducible coverage/report totals.

## Local Rules

- ORM table models inherit from `css.core.db.models.base`
- Module-owned `Enum` classes live in `enums.py`
- Module documentation in `src/css/modules/` uses the same-name file rule: `compliance/compliance.md`

# @alerts — Module Notes

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Alert rules, channel configuration, and alert delivery history.

## Current State

Implemented HTTP API (`/api/alerts`) for:
- alert-rule CRUD
- channel config CRUD + test trigger
- delivery history listing/details

Authorization now enforces org ownership via `X-Org-ID` header matching request `org_id`.

## Remaining Contract

| Gap | Required implementation |
|-----|-------------------------|
| Channel test route | Replace the `test_channel()` TODO with an actual dispatch through the configured channel adapter and persist delivery success/failure. |
| Production fan-out | `prod-alerts` must use alert rules to dispatch signed/retried webhook and configured notification deliveries without bypassing organization scoping. |

## Validation

- Test rule CRUD and organization isolation.
- Test successful and failed channel-test deliveries and history persistence.
- Test matching-event fan-out and retry/error recording.

## Local Rules

- ORM table models inherit `css.core.db.models.base.BaseModel`
- Module-owned `Enum` classes live in `enums.py`
- Module documentation in `src/css/modules/` uses the same-name file rule: `alerts/alerts.md`

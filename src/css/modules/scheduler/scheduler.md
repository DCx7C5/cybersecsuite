# @scheduler — Module Notes

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Scheduled task definitions and execution history.

## Current State

Implemented scheduler domain model + API routes under `/api/scheduler` for schedule creation, listing, and run tracking.

The scheduler module is mounted via `css.modules` entry points and participates in startup ORM model discovery.

## Remaining Contract

| Gap | Required implementation |
|-----|-------------------------|
| Immediate run route | Replace the queue placeholder in `run_task_now()` with a real asynchronous execution submission and persisted execution state. |
| Scheduled execution | Enforce schedule activation, next-run evaluation, and success/failure history without executing disabled tasks. |

## Validation

- Verify immediate and scheduled execution state transitions and failure history.
- Verify disabled schedules do not enqueue work.

## Local Rules

- ORM table models inherit `css.core.db.models.base.BaseModel`
- Module-owned `Enum` classes live in `enums.py`
- Module documentation in `src/css/modules/` uses the same-name file rule: `scheduler/scheduler.md`

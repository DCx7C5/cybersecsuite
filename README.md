# CyberSecSuite

CyberSecSuite is an async-first Python platform for orchestrated cybersecurity workflows, provider integrations, and modular runtime services.

## Required entry point (read first)

**Strict requirement:** before any planning, coding, or status updates, read and follow:
1. `.plan/rules.md`
2. `.plan/development-workflow.md`

Do not start implementation until both are applied. These two files are the authoritative operating contract.

## Start sequence (strict)

1. Read `.plan/rules.md`
2. Read `.plan/development-workflow.md`
3. Use `.plan/session.db` for todo selection/status transitions
4. Use `.plan/session.db::runtime` for active in-progress execution ownership

## Documentation map

- Primary planning overview: `.plan/plan.md`
- Rules and constraints: `.plan/rules.md`
- Workflow process: `.plan/development-workflow.md`
- Memory File: `.plan/memory.md`
- Checkpoint File: `.plan/checkpoints.md`
- Session/Tracking Database: `.plan/session.db`
- Runtime board (active in-progress todos): `sqlite3 .plan/session.db "SELECT run_id,todo_id,worker_slot,started_at,heartbeat_at FROM runtime ORDER BY started_at;"`
- Module and core plans: `src/css/**/plan.md`

## Project entry points

- App startup: `python manage.py serve --reload`
- Backend source: `src/css/`
- Planning workspace: `.plan/`

## Ownership notes

- `marketplace` is **core-owned only** at `src/css/core/marketplace/`.
- Legacy module package `src/css/modules/marketplace/` has been removed.

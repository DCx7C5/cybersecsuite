# CyberSecSuite

CyberSecSuite is an async-first Python platform for orchestrated cybersecurity workflows, provider integrations, and modular runtime services.

## Project entry points

- App startup: `python manage.py serve --reload`
- Backend source: `src/css/`
- Planning workspace: `.plan/`

## Documentation map

- Primary planning overview: `.plan/plan.md`
- Rules and constraints: `.plan/rules.md`
- Workflow process: `.plan/development-workflow.md`
- Memory File: `.plan/memory.md`
- Checkpoint File: `.plan/checkpoint.md`
- Session/Tracking Database: `.plan/session.db`
- Module and core plans: `src/css/**/plan.md`

## Ownership notes

- `marketplace` is **core-owned only** at `src/css/core/marketplace/`.
- Legacy module package `src/css/modules/marketplace/` has been removed.

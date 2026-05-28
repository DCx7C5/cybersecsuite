# CyberSecSuite Copilot Instructions

Before making changes in this repository:

1. Read `.plan/rules.md` completely.
2. Read `.plan/development-workflow.md` completely.
3. Query `.plan/session.db` for `in_progress` todos and ready pending todos.
4. Read the nearest local planning markdown for the target area.
5. Follow the critical rules exactly; if anything conflicts, stop and ask.

When work starts, prefer the `/start-working` prompt or the `start-working` custom agent.

Working rules:

- Use `.plan/session.db` as the source of truth for status changes.
- Keep implementation aligned with the nearest local plan and current source.
- Use the project venv tools and workflow conventions already documented in `.plan/`.

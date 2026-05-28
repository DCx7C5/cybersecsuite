---
name: start-working
description: "Bootstrap a session by loading the critical project rules and workflow"
---

# Start working

Use this prompt at the beginning of a session.

Before doing anything else:

1. Read `.plan/rules.md` completely.
2. Read `.plan/development-workflow.md` completely.
3. Query `.plan/session.db` for `in_progress` todos and ready pending todos.
4. Read the nearest local planning markdown for the target area.
5. Follow the critical rules exactly; if any instruction conflicts, stop and ask.

Then continue with the smallest safe next step for the current request.

If the request is implementation work, identify the todo, dependencies, and validation path before changing code.

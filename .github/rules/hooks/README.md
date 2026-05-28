# Hook-Specific Rules

Markdown rule files in this directory are loaded by the hook-rule loader and
injected as `additionalContext` only when their frontmatter matches the
current hook event.

## Frontmatter keys

| Key | Description |
|---|---|
| `event` | Required hook event name such as `sessionStart` or `subagentStart`. |
| `matcher` | Optional regex matched against event payload fields for that hook. |
| `title` | Optional display title for the injected rule block. |

## Current files

- `.github/rules/hooks/session-start.md`
- `.github/rules/hooks/css-plan-start.md`

## Notes

- Keep the body as the actual rule text.
- Use these files for hook-only behavior, not for file-path instructions.
- Update `.github/hooks/hooks.json` when adding a new rule file so the event
  actually loads it.

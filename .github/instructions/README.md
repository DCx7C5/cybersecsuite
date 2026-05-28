# GitHub Copilot Instructions

Repository-level instruction files live in `.github/instructions/**/*.instructions.md`.

## Official docs

- [Custom instructions](https://docs.github.com/en/copilot/concepts/prompting/response-customization)
- [Custom instructions support](https://docs.github.com/en/copilot/reference/custom-instructions-support)
- [Customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet)

## What belongs here

- reusable instructions for Copilot sessions
- scoped guidance that applies to matching Markdown files
- repository-specific rules that should stay close to the content they govern

## File format

Instruction files use YAML frontmatter, followed by Markdown content.

Required frontmatter:

- `applyTo`

Optional frontmatter:

- `excludeAgent`

Example:

```md
---
applyTo: "**/*.md"
excludeAgent: "code-review"
---

Instruction text goes here.
```

## Current files

- `.github/instructions/git-commit.instructions.md`
- `.github/instructions/plan/plan.instructions.md`

## Key reference

| Key | Description |
|---|---|
| `applyTo` | Required glob that selects files or directories for the instruction. |
| `excludeAgent` | Optional filter to omit a specific Copilot agent from the instruction. |

## Notes

- `applyTo` controls which files the instruction applies to.
- `excludeAgent` can keep specific agents from using the instruction.
- Keep instructions short, explicit, and close to the behavior they describe.
- For Copilot CLI, `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` are also supported agent instructions.

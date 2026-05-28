# GitHub Copilot Instructions

Repository-level instruction files live in `.github/instructions/**/*.md`.

## What belongs here

- reusable instructions for Copilot sessions
- scoped guidance that applies to matching Markdown files
- repository-specific rules that should stay close to the content they govern

## File format

Instruction files use YAML frontmatter, followed by Markdown content.

Example:

```md
---
applyTo: "**/*.md"
excludeAgent: "code-review"
---

Instruction text goes here.
```

## Current files

- `.github/instructions/git-commit-instructions.md`
- `.github/instructions/plan/plan-instructions.md`

## Notes

- `applyTo` controls which files the instruction applies to.
- `excludeAgent` can keep specific agents from using the instruction.
- Keep instructions short, explicit, and close to the behavior they describe.

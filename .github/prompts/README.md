# GitHub Copilot Prompts

Repository-level prompt files live in `.github/prompts/*.prompt.md`.

## What belongs here

- reusable prompt templates
- task-specific prompts for Copilot sessions
- prompts that should be easy to discover and reuse

## File format

Prompt files typically use YAML frontmatter, followed by the prompt body.

Example:

```md
---
name: review-plan-files
description: "Review the .plan/*.md planning docs for accuracy and gaps"
---

Prompt text goes here.
```

## Current files

- `.github/prompts/review-plan.prompt.md`

## Notes

- Keep names descriptive and stable.
- Use the prompt body to explain the goal, scope, and expected output.
- If a prompt depends on repo conventions, link or name the relevant files directly.

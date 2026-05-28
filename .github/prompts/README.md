# GitHub Copilot Prompts

Repository-level prompt files live in `.github/prompts/*.prompt.md`.

## Official docs

- [Prompt files](https://docs.github.com/en/copilot/concepts/prompting/response-customization?tool=vscode#about-prompt-files)
- [Customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet)
- [Custom instructions support](https://docs.github.com/en/copilot/reference/custom-instructions-support)

## What belongs here

- reusable prompt templates
- task-specific prompts for Copilot sessions
- prompts that should be easy to discover and reuse

## File format

Prompt files use YAML frontmatter, followed by Markdown instructions.

Recommended frontmatter keys:

- `name`
- `description`

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
- `.github/prompts/start-working.prompt.md`

## Key reference

| Key | Description |
|---|---|
| `name` | Prompt identifier used when referencing or browsing the file. |
| `description` | Short summary of what the prompt helps Copilot do. |

## Notes

- Keep names descriptive and stable.
- Use the prompt body to explain the goal, scope, and expected output.
- If a prompt depends on repo conventions, link or name the relevant files directly.
- Keep prompts short and reusable.

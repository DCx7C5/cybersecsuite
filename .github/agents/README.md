# GitHub Copilot Agents

Repository-level custom agents live in `.github/agents/*.agent.md`.

## Official docs

- [Custom agents](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-custom-agents)
- [Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- [Customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet)
- [Custom instructions support](https://docs.github.com/en/copilot/reference/custom-instructions-support)

## File format

Agent profiles use YAML frontmatter plus Markdown instructions.

Common frontmatter keys:

- `name`
- `description`
- `tools`
- `mcp-servers`
- `model`
- `target`

## Current files

- `.github/agents/*.agent.md` imported from `~/.copilot/agents`
- `.github/agents/start-working.agent.md`

## Key reference

| Key | Description |
|---|---|
| `name` | Optional display name for the agent; defaults to the filename. |
| `description` | Required summary of the agent’s purpose and capabilities. |
| `tools` | Tool allowlist; omit for all tools, use `[]` for none. |
| `mcp-servers` | YAML MCP server definitions scoped to this agent. |
| `model` | Optional model override where the surface supports it. |
| `target` | Optional environment target such as `vscode` or `github-copilot`. |

## Notes

- Use custom agents for reusable session behavior or specialized workflows.
- Keep the description short and explicit.
- Put the behavior in Markdown below the YAML frontmatter.
- Use `tools: []` to disable tools, or omit `tools` to allow all tools.

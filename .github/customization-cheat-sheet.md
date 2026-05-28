# GitHub Copilot Customization Cheat Sheet

Source: https://docs.github.com/en/copilot/reference/customization-cheat-sheet

## Feature overview

| Feature | What it is | Filename and location |
|---|---|---|
| Custom instructions | Always-on context that automatically applies within scope | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md`, or personal/org settings via UI |
| Prompt files | Reusable prompt templates with input variables | `.github/prompts/*.prompt.md` |
| Custom agents | Specialist persona with its own instructions, tool restrictions, and context | `.github/agents/AGENT-NAME.md`, or user/org equivalents |
| Subagents | Separate agent spawned by the main agent to handle delegated work | N/A |
| Agent skills | Folder of instructions, scripts, and resources loaded when relevant | `.github/skills/<skill-name>/SKILL.md` or user equivalents |
| Hooks | Shell commands that run at specific lifecycle points | `.github/hooks/*.json` |
| MCP servers | Connections to external systems, APIs, and databases | `mcp.json`, repo settings, or custom-agent `mcp-servers` |

## Usage comparison

| Feature | How to trigger | Best for | Example use cases |
|---|---|---|---|
| Custom instructions | Automatic | Broad standards and expectations | Coding standards, accessibility rules, review checklists |
| Prompt files | Manual | Focused one-off tasks | Generate tests, run a review checklist |
| Custom agents | Manual | Distinct stages or strict handoffs | React reviewer agent, read-only auditing agent |
| Subagents | Automatic or explicit | Isolated subtasks | Codebase research, running test suites |
| Agent skills | Automatic | Multi-step workflows with bundled assets | GitHub Actions failure debugging, release notes |
| Hooks | Automatic | Guaranteed lifecycle actions | Run a formatter, approve/deny tools, prevent leaks |
| MCP servers | Automatic or by tool name | External tools and live data | Manage issues/PRs, browser testing |

## IDE and surface support

| Feature | VS Code | Visual Studio | JetBrains IDEs | Eclipse | Xcode | GitHub.com | Copilot CLI |
|---|---|---|---|---|---|---|---|
| Custom instructions | ✓ | ✓ | P | P | P | ✓ | ✓ |
| Prompt files | ✓ | ✓ | P | ✗ | P | ✗ | ✗ |
| Custom agents | ✓ | ✗ | P | P | P | ✓ | ✓ |
| Subagents | ✓ | ✗ | P | P | P | ✗ | ✓ |
| Agent skills | ✓ | ✗ | P | ✗ | ✗ | ✓ | ✓ |
| Hooks | P | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| MCP servers | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Key: ✓ supported, ✗ not supported, P preview

## Further reading

- Customization library: https://docs.github.com/en/copilot/tutorials/customization-library

# CyberSecSuite Copilot Reference

This folder holds the repository-level Copilot customization surface and the
local reference docs for how it is wired together.

## Core entry points

| Area | Local file(s) | Official docs |
|---|---|---|
| Repository instructions | `.github/copilot-instructions.md` | [Custom instructions](https://docs.github.com/en/copilot/concepts/prompting/response-customization) |
| Path instructions | `.github/instructions/*.instructions.md` | [Custom instructions support](https://docs.github.com/en/copilot/reference/custom-instructions-support) |
| Prompt files | `.github/prompts/*.prompt.md` | [Prompt files](https://docs.github.com/en/copilot/concepts/prompting/response-customization?tool=vscode#about-prompt-files) |
| Custom agents | `.github/agents/*.agent.md` | [Custom agents](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-custom-agents) |
| Hooks | `.github/hooks/*.json` | [Hooks](https://docs.github.com/en/copilot/concepts/agents/hooks) |
| MCP / external tools | `mcp.json`, agent `mcp-servers` | [MCP](https://docs.github.com/en/copilot/concepts/context/mcp) |
| Cheat sheet | `.github/customization-cheat-sheet.md` | [Customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet) |

## Frontmatter key reference

| File type | Key | Description |
|---|---|---|
| Instructions | `applyTo` | Glob pattern for the files or folders the instruction applies to. |
| Instructions | `excludeAgent` | Optional agent filter such as `code-review` or `cloud-agent`. |
| Prompts | `name` | Stable prompt identifier shown in the prompt picker or reference. |
| Prompts | `description` | Short summary of what the prompt does. |
| Agents | `name` | Agent display name; defaults to the filename when omitted. |
| Agents | `description` | Required summary of the agent’s purpose and capabilities. |
| Agents | `tools` | Tool allowlist; omit for all tools, use `[]` to disable all. |
| Agents | `mcp-servers` | Agent-scoped MCP server definitions in YAML form. |
| Agents | `model` | Optional model override for supported surfaces. |
| Agents | `target` | Optional environment filter such as `vscode` or `github-copilot`. |
| Hooks | `version` | Hook schema version; currently `1`. |
| Hooks | `disableAllHooks` | Optional file-level toggle to skip every hook in the file. |
| Hooks | `hooks` | Object containing lifecycle event arrays such as `sessionStart` and `preToolUse`. |

## Hook entry keys

| Key | Description |
|---|---|
| `type` | Hook entry type: `command`, `http`, or `prompt` where supported. |
| `bash` | Unix shell command for a command hook. |
| `powershell` | Windows shell command for a command hook. |
| `command` | Cross-platform command fallback. |
| `cwd` | Working directory for a command hook. |
| `env` | Environment variables for a command hook. |
| `timeoutSec` | Timeout in seconds. |
| `url` | Target URL for HTTP hooks. |
| `headers` | HTTP headers for HTTP hooks. |
| `allowedEnvVars` | Env vars that may be expanded in HTTP headers. |
| `prompt` | Text submitted by a `sessionStart` prompt hook. |
| `matcher` | Optional regex used to limit which events a hook entry matches. |

## Local guide files

- `.github/copilot-instructions.md`
- `.github/instructions/README.md`
- `.github/prompts/README.md`
- `.github/agents/README.md`
- `.github/hooks/README.md`
- `.github/scripts/README.md`

## Recommended startup order

1. Read `.plan/rules.md`.
2. Read `.plan/development-workflow.md`.
3. Use `/start-working` or the `start-working` agent.
4. Check `.plan/session.db` before changing code.

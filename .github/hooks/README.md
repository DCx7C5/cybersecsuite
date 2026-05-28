# Copilot Hooks

Repository-level Copilot hook configuration lives in `.github/hooks/*.json`.

## Official docs

- [Hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference)
- [Hooks concept](https://docs.github.com/en/copilot/concepts/agents/hooks)
- [Tool names for hook matching](https://docs.github.com/en/copilot/reference/hooks-reference#tool-names-for-hook-matching)
- [Hook configuration format](https://docs.github.com/en/copilot/reference/hooks-reference#hook-configuration-format)
- [Hook events](https://docs.github.com/en/copilot/reference/hooks-reference#hook-events)
- [Hook event input payloads](https://docs.github.com/en/copilot/reference/hooks-reference#hook-event-input-payloads)
- [`preToolUse` decision control](https://docs.github.com/en/copilot/reference/hooks-reference#pretooluse-decision-control)
- [`postToolUse` output](https://docs.github.com/en/copilot/reference/hooks-reference#posttooluse-output)
- [Exit codes for command hooks](https://docs.github.com/en/copilot/reference/hooks-reference#exit-codes-for-command-hooks)
- [Disable all hooks](https://docs.github.com/en/copilot/reference/hooks-reference#disable-all-hooks)

## File format

Every hook JSON file starts with:

```json
{
  "version": 1,
  "hooks": {
    "sessionStart": [],
    "sessionEnd": [],
    "userPromptSubmitted": [],
    "preToolUse": [],
    "postToolUse": [],
    "errorOccurred": []
  }
}
```

Supported event keys:

- `agentStop`
- `errorOccurred`
- `notification`
- `permissionRequest`
- `postToolUse`
- `postToolUseFailure`
- `preCompact`
- `preToolUse`
- `sessionEnd`
- `sessionStart`
- `subagentStart`
- `subagentStop`
- `userPromptSubmitted`

## Important behavior

- `preToolUse` can allow, deny, or modify tool calls.
- `postToolUse` can modify successful tool output or add context.
- `sessionStart` prompt hooks only apply to new interactive CLI sessions.
- Cloud agent only honors `bash` or `command`; `powershell` is ignored there.
- Hook file output is fail-open: failed command hooks are logged and skipped.

## Tool names for matching

When using `matcher`, use the exact tool names from the docs:

- `ask_user`
- `bash`
- `create`
- `edit`
- `glob`
- `grep`
- `powershell`
- `task`
- `view`
- `web_fetch`

## Current repo example

- `.github/hooks/hooks.json`

It bootstraps each session with `/start-working`, logs `preToolUse`,
`postToolUse`, `sessionEnd`, and `errorOccurred` events to a temp file,
adds a `subagentStart` reminder for the `CSS Plan` agent, and keeps the
remaining supported events declared as empty arrays.

## Key reference

| Key | Description |
|---|---|
| `version` | JSON schema version; currently `1`. |
| `disableAllHooks` | Optional top-level flag to disable the hooks in one file. |
| `hooks` | Object that maps lifecycle events to hook entry arrays. |
| `sessionStart` | Runs when a session starts. |
| `sessionEnd` | Runs when a session ends. |
| `userPromptSubmitted` | Runs when the user submits a prompt. |
| `preToolUse` | Runs before a tool executes and can allow, deny, or modify it. |
| `postToolUse` | Runs after a successful tool call. |
| `postToolUseFailure` | Runs after a failed tool call. |
| `errorOccurred` | Runs when execution errors occur. |
| `agentStop` | Runs when the main agent finishes a turn. |
| `subagentStart` | Runs when a subagent starts. |
| `subagentStop` | Runs when a subagent ends. |
| `notification` | Runs on CLI notifications. |
| `permissionRequest` | Runs before permission handling. |
| `preCompact` | Runs before context compaction. |

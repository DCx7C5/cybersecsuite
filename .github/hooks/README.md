# Copilot Hooks

Repository-level Copilot hook configuration lives in `.github/hooks/*.json`.

## Canonical docs

Use these docs as the source of truth when adding or reviewing hooks:

- [Hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference)
- [Tool names for hook matching](https://docs.github.com/en/copilot/reference/hooks-reference#tool-names-for-hook-matching)
- [Hook configuration format](https://docs.github.com/en/copilot/reference/hooks-reference#hook-configuration-format)
- [Hook events](https://docs.github.com/en/copilot/reference/hooks-reference#hook-events)
- [Hook event input payloads](https://docs.github.com/en/copilot/reference/hooks-reference#hook-event-input-payloads)
- [`preToolUse` decision control](https://docs.github.com/en/copilot/reference/hooks-reference#pretooluse-decision-control)
- [`postToolUse` output](https://docs.github.com/en/copilot/reference/hooks-reference#posttooluse-output)
- [Exit codes for command hooks](https://docs.github.com/en/copilot/reference/hooks-reference#exit-codes-for-command-hooks)
- [Disable all hooks](https://docs.github.com/en/copilot/reference/hooks-reference#disable-all-hooks)

## Header checklist

Every hook JSON file should start with:

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

You can also declare any of these supported event keys:

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

The current repository hook file is:

- `.github/hooks/pre-tool-use.json`

It contains a `preToolUse` command hook that logs payloads to a temp file and keeps the other supported events declared as empty arrays.

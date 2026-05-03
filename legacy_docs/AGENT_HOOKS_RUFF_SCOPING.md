# Agent Hooks: Ruff Scoping and Dry-Run Mode

## Overview

This implementation adds **scoped ruff fixes** and **dry-run mode** to the agent hook system, making it safer for agents to modify code without unintended side effects.

**Goal:** Only run `ruff check --fix` on files the agent actually modified, and default to dry-run mode.

## Key Features

### 1. Baseline Snapshotting (`on_agent_start`)
- When an agent starts, we create a **SHA256 hash snapshot** of all target files
- Baseline stored in `~/.cybersecsuite/hooks/baselines/`
- Enables accurate change detection even across sessions

### 2. File Change Detection (`get_changed_files`)
- Uses `git diff` if available (fastest, most accurate)
- Falls back to hash comparison if git unavailable
- Only detects files that **actually changed**, not entire `src/` directory

### 3. Ruff Dry-Run Mode (`run_ruff_dry_run`)
- Default mode: `ruff check --diff` (shows diffs without applying)
- Opt-in mode: `ruff check --fix` (applies fixes, returns count)
- Prevents unintended mutations of unrelated files

### 4. Comprehensive Logging
- Baseline snapshots logged: "Agent X: baseline snapshot created for N files"
- Change detection logged: "Modified N files: [list]"
- Ruff execution logged: "Ruff dry-run output..." or "Ruff applied N fixes"
- All events audited to `hooks_audit.jsonl`

## Architecture

### New Files

```
src/hooks/agent_hooks.py          Main module (functions + CLI entry points)
src/db/migration/plan_v1.py       Migration: add target_files column to tasks
tests/unit/test_agent_hooks.py    Comprehensive test suite (17 tests)
```

### Modified Files

```
src/hooks/agent_start.py           Delegated to agent_hooks.on_agent_start()
src/hooks/agent_end.py             Delegated to agent_hooks.on_agent_stop()
src/db/models/plan.py              Added target_files field + get/set methods
src/db/managers/plan_manager.py    Added target_files support to add_task()
                                   Added delegate_task_with_hooks() helper
```

## Implementation Details

### File Change Detection Strategy

**Priority:**
1. **Git diff** (if available): Most accurate, fastest
2. **Hash comparison** (fallback): Works without git, resilient

**Hash Algorithm:** SHA256 (consistent, cryptographic)

### Data Flow

```
Agent Start
  └─ on_agent_start(agent_name, session_id, target_files)
      ├─ Create baseline snapshot: { file_path -> hash }
      └─ Store in ~/.cybersecsuite/hooks/baselines/{session}_{agent}.json

[Agent modifies files...]

Agent Stop
  └─ on_agent_stop(agent_name, session_id, target_files, dry_run=True)
      ├─ Load baseline snapshot
      ├─ Detect changed files: git diff OR hash comparison
      ├─ If dry_run=True
      │  └─ ruff check --diff [changed_files] (show diffs, don't apply)
      └─ If dry_run=False
         └─ ruff check --fix [changed_files] (apply fixes, log count)
```

### Task Integration

Tasks now support `target_files` field (JSON-serialized list):

```python
task = await Task.create(...)
task.set_target_files(["src/auth.py", "src/utils.py"])
await task.save()

# Later, when delegating:
agent_name = "my-agents"
target_files = task.get_target_files()
await on_agent_start(agent_name, session_id, target_files)
```

### Hook Invocation

**CLI:**
```bash
# Start hook
echo '{"agent_name":"my-agents", "session_id":"s123", "target_files":["file1.py"]}' | \
  python src/hooks/agent_start.py

# Stop hook (dry-run by default)
echo '{"agent_name":"my-agents", "session_id":"s123", "target_files":["file1.py"], "dry_run":true}' | \
  python src/hooks/agent_end.py stop
```

**Async API:**
```python
from hooks.agent_hooks import on_agent_start, on_agent_stop

await on_agent_start("my-agents", "s123", ["src/main.py"])
# ... agents does work ...
await on_agent_stop("my-agents", "s123", ["src/main.py"], dry_run=True)
```

## Testing

**Test Coverage (17 tests):**

| Category | Tests |
|----------|-------|
| File Hashing | 3 tests |
| Baseline Snapshotting | 2 tests |
| Change Detection | 3 tests |
| Ruff Dry-Run | 2 tests |
| Ruff Fix Mode | 2 tests |
| Agent Start Hook | 2 tests |
| Agent Stop Hook | 2 tests |
| Full Integration | 1 test |

**Run tests:**
```bash
uv run pytest tests/unit/test_agent_hooks.py -v
# Result: 17 passed
```

## Migration

Add `target_files` column to tasks table:

```bash
uv run python -m db.migration.plan_v1
```

Or manually (PostgreSQL):
```sql
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS target_files TEXT DEFAULT '';
```

## Example Usage

### Full Lifecycle

```python
from db.managers.plan_manager import PlanManager
from hooks.agent_hooks import on_agent_start, on_agent_stop

pm = PlanManager()

# Create task with target files
task = await pm.add_task(
    plan_id=1,
    title="Refactor auth module",
    target_files=["src/auth.py", "src/utils.py"],
)

# Agent starts
await on_agent_start("refactor-agents", "session123", task.get_target_files())

# [Agent modifies files src/auth.py and src/utils.py]

# Agent stops (dry-run by default)
await on_agent_stop(
    "refactor-agents",
    "session123",
    task.get_target_files(),
    dry_run=True,  # Show diffs only
)

# Or with fixes applied:
await on_agent_stop(
    "refactor-agents",
    "session123",
    task.get_target_files(),
    dry_run=False,  # Apply fixes
)
```

### What Gets Logged

```
[2024-04-27T14:32:15] AgentStart: refactor-agent (session=session123)
  └─ Baseline snapshot created: 2 files
  
[2024-04-27T14:35:42] AgentStop: refactor-agent
  └─ Modified 1/2 target files (src/auth.py changed)
  └─ Ruff dry-run: showing 3 style fixes without applying
```

## Safety Features

### 1. Scope Limiting
- Ruff only runs on files specified in `target_files`
- Prevents accidental mutation of unrelated code

### 2. Dry-Run by Default
- `dry_run=True` (default) shows diffs without applying
- Requires explicit `dry_run=False` to apply changes

### 3. Change Detection
- Only changed files are processed
- Unmodified files skipped even if in target list

### 4. Audit Trail
- All events logged to `hooks_audit.jsonl`
- File-level hashes tracked in baseline snapshots
- Full context in stdout/stderr

## Troubleshooting

### Baseline Not Found
If baseline file doesn't exist:
- Falls back to treating all target files as "changed"
- This is safe—ruff runs on provided files

### Git Diff Fails
If `git diff` unavailable:
- Falls back to hash comparison
- Still detects changes accurately

### Ruff Not Installed
Ruff is assumed to be on PATH:
- If missing, subprocess call logs error
- Continues safely without applying fixes

## Future Enhancements

1. **Ruff Configuration**: Pass `--config pyproject.toml` per task
2. **Other Linters**: Extend pattern to black, isort, mypy
3. **Persistent State**: Store baseline in database instead of filesystem
4. **Pre-commit Integration**: Hook into git pre-commit workflow
5. **Performance**: Cache baselines for repeated tasks

## References

- **Baseline**: SHA256 hashes, JSON format, session-scoped storage
- **Change Detection**: Git diff primary, hash comparison fallback
- **Dry-Run**: `ruff check --diff` (stdout) vs `ruff check --fix` (applies)
- **Logging**: Async-safe, structured events, audit trail

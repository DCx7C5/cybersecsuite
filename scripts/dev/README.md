# Developer Tools

Utilities for development, debugging, and interactive workflows.

## Scripts

### `worktree-session-manager.py`
Manage Git worktree sessions for parallel development on multiple branches.

**Usage:**
```bash
python scripts/dev/worktree-session-manager.py <command> [args]
```

**Commands:**
- `create <branch>` — Create new worktree session
- `list` — List active worktrees
- `remove <worktree>` — Remove worktree
- `clean` — Clean orphaned worktrees

**Example:**
```bash
python scripts/dev/worktree-session-manager.py create feature/new-mcps
cd ../feature-new-mcps
# ... work on feature branch
```

### `gwt-aliases.sh`
Define shell aliases for git-worktree shortcuts.

**Usage:**
```bash
source scripts/dev/gwt-aliases.sh
```

**Aliases provided:**
- `gwt-create` — Quick worktree creation
- `gwt-list` — List worktrees
- `gwt-clean` — Clean worktrees

## When to Use

- Multi-branch development workflows
- Running tests in isolation
- Parallel feature development
- Interactive debugging sessions

## Installation

Source `gwt-aliases.sh` in your `.bashrc` or `.zshrc`:
```bash
echo "source $(pwd)/scripts/dev/gwt-aliases.sh" >> ~/.bashrc
```

## See Also

- `scripts/test/` — Testing tools
- `scripts/data/` — Data processing
- `scripts/deploy/` — Deployment automation

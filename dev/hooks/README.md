# Git Hooks

Pre-commit and post-merge hooks for automated quality checks and workflows.

## Hooks

### `pre-commit.tpl`
Runs before each commit to validate code quality.

**Checks:**
- ESLint for TypeScript/JavaScript
- Ruff for Python code style
- MyPy for type checking
- Check for uncommitted file sizes
- Prevent commits to protected branches

**Bypass:**
```bash
git commit --no-verify
```

### `pre-push.tpl`
Runs before pushing to remote repository.

**Checks:**
- Test execution (Tier 1 subset)
- Linting validation
- Coverage threshold checks
- Branch protection rules

### `post-merge.tpl`
Runs after merging changes.

**Actions:**
- Update lock files
- Rebuild dependencies
- Update CHANGELOG
- Trigger integration tests

### `commit-msg.tpl`
Validates commit message format.

**Format:**
```
<type>: <subject> (max 50 chars)

<body> (optional, max 72 chars per line)

<footer> (optional)
Co-authored-by: Name <email@example.com>
```

**Types:**
- `feat` — New feature
- `fix` — Bug fix
- `test` — Test changes
- `docs` — Documentation
- `refactor` — Code refactoring
- `perf` — Performance improvements
- `chore` — Build/config changes

### `post-checkout.tpl`
Runs after changing branches.

**Actions:**
- Update Python virtual environment
- Refresh workspace state
- Clean build artifacts
- Update documentation links

## Installation

Hooks are automatically installed via `.pre-commit-config.yaml`:

```bash
pre-commit install --install-hooks
```

Or manually copy templates:
```bash
cp dev/hooks/*.tpl .git/hooks/
chmod +x .git/hooks/*
```

## Disabling Hooks

For a single commit:
```bash
git commit --no-verify
```

For all commits (temporary):
```bash
pre-commit uninstall
```

Then reinstall:
```bash
pre-commit install
```

## Configuration

Edit `.pre-commit-config.yaml` to customize:
- Which hooks run
- File patterns to check
- Tool-specific options

## Testing Hooks

```bash
pre-commit run --all-files  # Run all hooks
pre-commit run eslint --all-files  # Specific hook
```

## See Also

- `.pre-commit-config.yaml` — Hook configuration
- `scripts/dev/` — Developer tools
- `scripts/test/` — Testing tools

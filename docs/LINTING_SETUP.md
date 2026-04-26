# Linting & Type Checking Setup

## Overview

CyberSecSuite maintains zero linting and type checking errors across the entire codebase using **Ruff** (Python linting) and **mypy** (strict type checking).

**Phase 11.1 - Completion Status: ✅ COMPLETE**
- ✅ Ruff: 0 errors across 295 src + 41 test files
- ✅ Mypy: 0 errors in strict mode
- ✅ All configuration completed and documented

---

## Tools & Versions

| Tool | Version | Purpose |
|------|---------|---------|
| **ruff** | 0.15.5 | Fast Python linter & code formatter |
| **mypy** | 1.19.1 (compiled) | Static type checker (strict mode) |
| **uv** | Latest | Package manager & task runner |

---

## Configuration

### Ruff Configuration

Located in `pyproject.toml`:

```toml
[tool.ruff]
src = ["src"]
line-length = 100
exclude = [".claude"]
```

**Key settings:**
- `src = ["src"]`: Primary source directory for linting
- `line-length = 100`: Code style enforced at 100 characters (PEP 8 extended)
- `exclude = [".claude"]`: Exclude AI workspace configuration

### Mypy Configuration

Located in `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.14"
strict = true
warn_unused_configs = true
exclude = [".claude", ".venv", "__pycache__"]
plugins = ["pydantic.mypy"]

[tool.pydantic]
mypy_plugins = ["pydantic.mypy"]
```

**Key settings:**
- `python_version = "3.14"`: Target Python version for type checking
- `strict = true`: Enable strict mode (all functions require type hints, no implicit Any)
- `warn_unused_configs = true`: Warn about unused mypy configuration
- `plugins = ["pydantic.mypy"]`: Use Pydantic v2 mypy plugin for better type inference
- `exclude`: Ignore virtual environment and cache directories

---

## Running Linting Locally

### 1. Ruff Check (Lint Only)

```bash
cd /home/daen/Projects/cybersecsuite
uv run ruff check src tests
```

**Output:** Lists all linting violations without making changes.

### 2. Ruff Check with Auto-Fix

```bash
cd /home/daen/Projects/cybersecsuite
uv run ruff check src tests --fix
```

**Output:** Automatically fixes 101+ common violations (imports, unused variables, formatting).

**Note:** Some violations may require `--unsafe-fixes` for aggressive fixes:
```bash
uv run ruff check src tests --fix --unsafe-fixes
```

### 3. Mypy Type Checking (Strict Mode)

```bash
cd /home/daen/Projects/cybersecsuite
uv run mypy src tests --strict
```

**Output:** Reports all type errors in strict mode:
- Missing type annotations on functions/variables
- Type mismatches
- Uninitialized variables
- Missing return statements

### 4. Full Linting Suite (Recommended for CI)

```bash
#!/bin/bash
set -e

cd /home/daen/Projects/cybersecsuite

echo "Running Ruff checks..."
uv run ruff check src tests

echo "Running mypy type checking (strict)..."
uv run mypy src tests --strict

echo "✅ All checks passed!"
```

---

## CI/CD Integration

### GitHub Actions Workflow

Add to `.github/workflows/lint.yml`:

```yaml
name: Lint & Type Check

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: astral-sh/setup-uv@v3
      
      - name: Run Ruff linting
        run: cd /home/daen/Projects/cybersecsuite && uv run ruff check src tests
      
      - name: Run mypy type checking (strict mode)
        run: cd /home/daen/Projects/cybersecsuite && uv run mypy src tests --strict
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
set -e

cd /home/daen/Projects/cybersecsuite

echo "Running Ruff checks..."
uv run ruff check src tests || exit 1

echo "Running mypy type checking..."
uv run mypy src tests --strict || exit 1

echo "✅ Linting passed!"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Common Violations & Fixes

### 1. Unused Imports

**Error:**
```python
from typing import Any  # F401: imported but unused
```

**Fix:**
```bash
uv run ruff check src tests --fix
```

Ruff automatically removes unused imports.

### 2. Module Level Imports Not at Top

**Error:**
```python
# E402: Module level import not at top of file
import sys
sys.path.insert(0, "/path")
import module  # ← E402 error
```

**Fix:**
Add `# noqa: E402` comment to imports that must come after sys.path manipulation:

```python
import sys
sys.path.insert(0, "/path")
import module  # noqa: E402
```

### 3. Unused Variables

**Error:**
```python
unused_var = some_function()  # F841: assigned but never used
```

**Fix:** Prefix with underscore to indicate intentional:
```python
_ = some_function()
```

Or use the variable:
```python
result = some_function()
assert result is not None
```

### 4. Type Annotation Issues (mypy)

**Error:**
```python
def process(data):  # Missing type annotation
    return data.upper()
```

**Fix:**
```python
def process(data: str) -> str:
    return data.upper()
```

---

## File Statistics (Phase 11.1)

| Category | Count |
|----------|-------|
| Source files linted | 295 |
| Test files linted | 41 |
| **Total Python files** | **336** |
| Ruff errors fixed | 101 |
| Ruff errors remaining | 0 |
| Mypy errors (strict) | 0 |

---

## Troubleshooting

### Issue: `mypy: command not found`

**Solution:** Install via uv:
```bash
uv pip install mypy
```

### Issue: Ruff reports E402 errors on imports

**Solution:** Use `# noqa: E402` if imports must follow sys.path manipulation:
```python
import sys
sys.path.insert(0, str(SRC_PATH))
import my_module  # noqa: E402
```

### Issue: mypy fails with "No module named X"

**Solution:** Ensure src directory is in Python path:
```bash
export PYTHONPATH="/home/daen/Projects/cybersecsuite/src:$PYTHONPATH"
uv run mypy src tests --strict
```

Or verify `pytest.ini` includes:
```ini
pythonpath = ["src"]
```

---

## Maintenance

### Weekly Checks

```bash
cd /home/daen/Projects/cybersecsuite
uv run ruff check src tests
uv run mypy src tests --strict
```

### Quarterly Updates

Update tool versions in `pyproject.toml`:
```bash
uv pip install --upgrade ruff mypy
```

### New Code Guidelines

**Before committing new code:**
1. Add full type annotations to all functions
2. Run `ruff check --fix` to auto-correct style
3. Run `mypy --strict` to verify types
4. All imports must be at module top (or use `# noqa: E402`)

---

## Related Documentation

- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [PEP 8 - Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)

---

**Last Updated:** Phase 11.1  
**Status:** ✅ All checks passing  
**Next Review:** Phase 12.0

# CyberSecSuite Custom Validation Scripts

Automated validators and workflow helpers that replace manual steps from `.plan/development-workflow.md`.

## Quick Start

**One-command validation (all checks):**
```bash
python .github/scripts/pre-commit-check.py
```

**Manual validation by category:**
```bash
python .github/scripts/validate-crypto.py src/css/
python .github/scripts/validate-sql-safety.py src/css/
python .github/scripts/validate-async-safety.py src/css/
python .github/scripts/validate-dependencies.py src/css/
```

**Todo workflow helper:**
```bash
python .github/scripts/todo-workflow.py ready
python .github/scripts/todo-workflow.py phase-status
python .github/scripts/todo-workflow.py mark-todo-in-progress SOME-ID claude-haiku-4.5 my-session
```

**Hook-rule loader:**
```bash
python .github/scripts/load_hook_rules.py sessionStart
python .github/scripts/load_hook_rules.py subagentStart
```

## Scripts

### 1. `validate-crypto.py`
Enforces cryptographic stack invariants.

**Validates:**
- BLAKE2b-256: requires `digest_size=32`
- Ed25519: correct imports from `cryptography` library
- Argon2id: parameters `memory_cost=262144, lanes=4, length=32, iterations=4`
- AES-256-GCM: 256-bit keys and auth tag verification
- Salts: never hardcoded, must use `os.urandom()` or `secrets.token_bytes()`

**Usage:**
```bash
python .github/scripts/validate-crypto.py src/css/core/
python .github/scripts/validate-crypto.py src/css/core/crypto.py
```

**Output:** `CRITICAL` findings (blocks merge), file:line references

---

### 2. `validate-sql-safety.py`
Detects SQL injection risks.

**Validates:**
- SQL f-strings: `f"SELECT ... WHERE id = {var}"` ← CRITICAL
- SQL concatenation: `"SELECT " + var` ← CRITICAL
- Missing parameterization (heuristic checks)
- ORM query patterns

**Usage:**
```bash
python .github/scripts/validate-sql-safety.py src/css/api_services/
```

**Output:** `CRITICAL` findings for injection risk patterns

---

### 3. `validate-async-safety.py`
Detects blocking calls in async functions.

**Validates:**
- `time.sleep()` in `async def` → should be `await asyncio.sleep()`
- `requests.get()` in `async def` → should use `aiohttp` or `httpx` async
- Blocking file I/O in `async def` → should use `aiofiles`
- Unclosed async context managers (heuristic)

**Usage:**
```bash
python .github/scripts/validate-async-safety.py src/css/
```

**Output:** `HIGH` findings for event loop blocking patterns

---

### 4. `validate-dependencies.py`
Enforces `uv`-only package management.

**Validates:**
- `pip install` in `.py` files → violates stack
- `pip install` in shell scripts → violates stack
- `subprocess.run(['pip', ...])` in code → violates stack
- Missing `uv.lock` sync

**Usage:**
```bash
python .github/scripts/validate-dependencies.py src/css/
```

**Output:** `HIGH` findings for forbidden package managers

---

### 5. `pre-commit-check.py`
Master orchestrator — runs all validators + type checking.

**Runs in sequence:**
1. `validate-crypto.py`
2. `validate-sql-safety.py`
3. `validate-async-safety.py`
4. `validate-dependencies.py`
5. Optional: `pyright` type checking

**Usage:**
```bash
python .github/scripts/pre-commit-check.py
python .github/scripts/pre-commit-check.py --staged      # git pre-commit hook
```

**Output:** Summary report; exits `0` (all pass) or `1` (failures)

---

### 6. `todo-workflow.py`
CLI for `.plan/session.db` operations (replaces SQL queries).

**Commands:**

| Command | Purpose | Example |
|---------|---------|---------|
| `ready` | Show next ready todos (no blocked deps) | `python ... todo-workflow.py ready` |
| `phase-status` | Progress by phase | `python ... todo-workflow.py phase-status` |
| `mark-todo-in-progress` | Claim a todo for work | `python ... mark-todo-in-progress ID MODEL SESSION_ID` |
| `mark-todo-done` | Mark todo complete | `python ... mark-todo-done ID` |
| `show-blockers` | What's blocking a todo | `python ... show-blockers ID` |
| `list-phase` | All todos in a phase | `python ... list-phase PHASE_NAME` |

**Usage Examples:**
```bash
# Start of session: see what's ready
python .github/scripts/todo-workflow.py ready

# Claim a todo for work
python .github/scripts/todo-workflow.py mark-todo-in-progress some-todo-id claude-haiku-4.5 my-session-id

# Check your progress
python .github/scripts/todo-workflow.py phase-status

# Mark done when complete
python .github/scripts/todo-workflow.py mark-todo-done some-todo-id
```

---

### 7. `load_hook_rules.py`
Loads Markdown rule files from `.github/rules/hooks/` and emits hook
`additionalContext` only when the file frontmatter matches the current event.

**Validates:**
- frontmatter `event` matches the hook event
- optional `matcher` matches the relevant payload field
- injected content is built from the Markdown body only

**Usage:**
```bash
python .github/scripts/load_hook_rules.py sessionStart
python .github/scripts/load_hook_rules.py subagentStart
```

**Output:** JSON with `additionalContext`, or `{}` if no rule matches

---

## Integration Patterns

### Git Pre-Commit Hook

**Create `.git/hooks/pre-commit`:**
```bash
#!/bin/bash
python .github/scripts/pre-commit-check.py --staged
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

Now validation runs automatically on every `git commit`.

---

### GitHub Actions Workflow

**Example: `.github/workflows/validate.yml`**
```yaml
name: Code Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        run: uv sync
      
      - name: Validate crypto
        run: python .github/scripts/validate-crypto.py src/css/
      
      - name: Validate SQL safety
        run: python .github/scripts/validate-sql-safety.py src/css/
      
      - name: Validate async safety
        run: python .github/scripts/validate-async-safety.py src/css/
      
      - name: Validate dependencies
        run: python .github/scripts/validate-dependencies.py src/css/
      
      - name: Type checking
        run: uv run pyright src/css/
```

---

## Replacing Workflow Steps

| Workflow Step | Before (Manual) | After (Automated) |
|---|---|---|
| **Pre-TODO: Check if safe to touch file** | `grep` + manual review | `python .github/scripts/validate-crypto.py src/...` |
| **Mid-TODO: Validate crypto** | Read `src/crypto/` manually | `validate-crypto.py` |
| **Post-TODO: Ensure no SQL injection** | Manual code review | `validate-sql-safety.py` |
| **Post-TODO: No blocking in async** | Manual inspection of `async def` | `validate-async-safety.py` |
| **Post-TODO: Only uv for packages** | grep for pip | `validate-dependencies.py` |
| **TASK start: Claim next todo** | SQL query + manual UPDATE | `python ... mark-todo-in-progress ID MODEL SESSION` |
| **TASK end: Mark done** | SQL UPDATE | `python ... mark-todo-done ID` |
| **PHASE review: Check progress** | SQL GROUP BY phase | `python ... phase-status` |

---

## Exit Codes & CI Integration

All validators follow standard exit codes:
- `0` = All checks passed
- `1` = Validation failures found

Use in CI/CD:
```bash
python .github/scripts/pre-commit-check.py || exit 1
```

---

## Extending Scripts

Each validator is a standalone Python script. To add new checks:

1. Create `validate-my-check.py` in this directory
2. Follow the `Finding(file, line, severity, ...)` pattern
3. Add to `VALIDATORS` list in `pre-commit-check.py`
4. Call from GitHub Actions workflow

Example structure:
```python
class Finding(NamedTuple):
    file: str
    line: int
    severity: str  # CRITICAL | HIGH | MEDIUM
    pattern: str
    issue: str
    fix: str

# Scan logic...

if findings:
    print(f"\n{len(findings)} FINDING(S):")
    for f in findings:
        print(f"  {f.file}:{f.line} - {f.issue}")
    sys.exit(1)
else:
    print("✅ Check: PASS")
    sys.exit(0)
```

---

## Troubleshooting

**"Database not found: .plan/session.db"**
- Ensure you're in the repo root: `cd /home/daen/Projects/cybersecsuite`
- Ensure `.plan/session.db` exists (should be committed)

**Validators not finding issues I know exist**
- These are *heuristic* pattern detectors, not semantic analyzers
- For complex patterns, use manual code review + pyright
- File an issue to improve pattern detection

**Pre-commit hook runs but doesn't block commit**
- Ensure hook is executable: `chmod +x .git/hooks/pre-commit`
- Ensure it calls the validator with correct exit code

---

## Reference

- **Crypto stack**: `.plan/rules.md` → "Crypto correctness"
- **SQL safety**: `.plan/rules.md` → "SQL safety"
- **Async discipline**: `.plan/rules.md` → "Async discipline"
- **Dependency hygiene**: `.plan/rules.md` → "Dependency hygiene"
- **Workflows**: `.plan/development-workflow.md` → "Workflow N"

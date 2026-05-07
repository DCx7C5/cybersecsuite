# Development Workflow

**⚠️ CRITICAL**: Read this file completely before touching any code. Follow every step exactly. No shortcuts.

**Project root**: `/home/daen/Projects/cybersecsuite/`
**Plan directory**: `/home/daen/Projects/cybersecsuite/.plan/`
**Source directory**: `/home/daen/Projects/cybersecsuite/src/css/`
**Python venv**: `/home/daen/Projects/cybersecsuite/.venv/bin/python`

---

## 🔍 DEPENDENCY ANALYZER INTEGRATION

**Script**: `.plan/codebase_dependency_analyzer.py`
**Output**: JSON `{"file.py": {"consumed_by": [...], "consumes": [...]}}`

### When to Run (copy-paste ready):

```bash
# BEFORE editing — see what depends on files you're about to touch
.venv/bin/python .plan/codebase_dependency_analyzer.py . \
  --path src/css/modules/<module>/ \
  --output /tmp/deps.json

# AFTER editing — verify no illegal cross-module deps
.venv/bin/python .plan/codebase_dependency_analyzer.py . \
  --path src/css/modules/<module>/ \
  --output /tmp/deps_after.json
.venv/bin/python -c "
import json
d = json.load(open('/tmp/deps_after.json'))
for f, data in d.items():
    for dep in data['consumes']:
        if dep.startswith('src/css/modules/') and not dep.startswith('src/css/modules/<module>/'):
            print(f'ILLEGAL DEP: {f} consumes {dep}')
"

# TASK completion — full module dep map
.venv/bin/python .plan/codebase_dependency_analyzer.py . \
  --path src/css/modules/<module>/ \
  --output /tmp/task_deps.json

# PHASE completion — full project impact analysis
.venv/bin/python .plan/codebase_dependency_analyzer.py . \
  --output /tmp/full_deps.json
```

### JSON Output (trivial for LLM to parse):
```json
{
  "src/css/modules/foo/types.py": {
    "consumed_by": ["src/css/modules/foo/endpoints.py"],
    "consumes": ["src/css/core/types/base_entity.py"]
  }
}
```

### Where It Adds Value:
| Workflow | Analyzer Use | Value |
|----------|----------------|-------|
| TODO | `consumed_by` on file you're editing | Avoid breaking files that depend on you |
| TODO | `consumes` after editing | Catch illegal cross-module imports early |
| TASK | Full module scan | Verify no circular deps before declaring task done |
| PHASE | Full project scan | Impact analysis for PHASE completion |

---

## 📊 SQL QUERIES (reference from workflows — single source of truth)

```sql
-- Ready todos (no blocked deps) — use this most often
SELECT id, title, phase, task FROM todos
WHERE status = 'pending'
AND NOT EXISTS (
  SELECT 1 FROM todo_deps td
  JOIN todos dep ON td.depends_on = dep.id
  WHERE td.todo_id = todos.id AND dep.status != 'done'
)
ORDER BY phase, task;

-- Phase summary — how far along is each phase?
SELECT phase,
  COUNT(*) as total,
  SUM(status = 'done') as done,
  SUM(status = 'pending') as pending,
  SUM(status = 'blocked') as blocked
FROM todos GROUP BY phase ORDER BY phase;

-- What's blocking a specific todo?
SELECT dep.id as blocking_todo, dep.title, dep.status
FROM todo_deps td
JOIN todos dep ON td.depends_on = dep.id
WHERE td.todo_id = 'your-todo-id';

-- All todos for a specific task
SELECT id, title, status FROM todos WHERE task = 'TASK_NAME';

-- Full description of a todo
SELECT id, title, description FROM todos WHERE id = 'your-todo-id';

-- Mark todo in_progress
UPDATE todos SET status = 'in_progress', updated_at = datetime('now') WHERE id = 'your-todo-id';

-- Mark todo done
UPDATE todos SET status = 'done', updated_at = datetime('now') WHERE id = 'your-todo-id';

-- Check for in_progress leftovers
SELECT id, title, phase, task FROM todos WHERE status = 'in_progress';

-- Verify all todos in a task are done
SELECT id, title, status FROM todos WHERE task = 'TASK_NAME' AND status != 'done';

-- Verify all phase todos are done
SELECT COUNT(*) as remaining FROM todos WHERE phase = 'PHASE_NAME' AND status != 'done';
```

**⚠️ THERE IS NO `tasks` TABLE. THERE IS NO `completed_at` COLUMN. DO NOT USE THEM.**

**Status lifecycle**: `pending` → `in_progress` → `done` (or `blocked`)

---

## ✅ WORKFLOW 1 — COMPLETING A SINGLE TODO

This is the most common workflow. Do this for each todo.

### 🔴 PRE-TODO (run BEFORE starting any todo)

```sql
-- 1. Check for in_progress leftovers (finish these FIRST!)
SELECT id, title FROM todos WHERE status = 'in_progress';

-- 2. Pick next ready todo (no blocked deps)
SELECT id, title, phase, task, description
FROM todos
WHERE status = 'pending'
AND NOT EXISTS (
  SELECT 1 FROM todo_deps td
  JOIN todos dep ON td.depends_on = dep.id
  WHERE td.todo_id = todos.id AND dep.status != 'done'
)
ORDER BY phase, task LIMIT 1;

-- 3. Mark it in_progress (replace TODO_ID with result from step 2)
UPDATE todos SET status = 'in_progress', updated_at = datetime('now')
WHERE id = 'TODO_ID';
```

**Read these files** (based on the todo's `phase`/`task`):
```bash
# Always read the local plan.md for the module you're working in:
cat "src/css/modules/$(echo TODO_ID | cut -d'-' -f1)/plan.md" 2>/dev/null || \
cat "src/css/core/$(echo TODO_ID | cut -d'-' -f1)/plan.md" 2>/dev/null || \
cat "src/css/api_services/$(echo TODO_ID | cut -d'-' -f1)/plan.md" 2>/dev/null

# Read architecture doc if phase mentions it:
# Phase 6 → cat .plan/architecture/core-audit-matrix.md
# Phase 14 → cat .plan/architecture/observability.md
# Phase 21 → cat .plan/architecture/sdks.md

# Read the full todo description:
# SELECT description FROM todos WHERE id = 'TODO_ID';
```

**Run dependency analyzer** (see what depends on your files):
```bash
.venv/bin/python .plan/codebase_dependency_analyzer.py . \
  --path src/css/modules/<module>/ --output /tmp/deps.json
```

---

### 🟢 ACTIVE (the actual work)

**Step 1 — Check what already exists**
```bash
# List files in target directory (quiet, parseable)
ls src/css/modules/<module_name>/ 2>/dev/null || ls src/css/core/<subdir>/ 2>/dev/null

# Find related code (use python to avoid regex issues)
.venv/bin/python -c "
import pathlib
for p in pathlib.Path('src/css/').rglob('*.py'):
    try:
        content = p.read_text(errors='replace')
        if 'ClassName' in content or 'function_name' in content:
            print(p)
    except: pass
" | head -10
```

**Step 2 — Implement the code**
- Edit files in `src/css/` or `src/frontend/` (if exists) only
- Follow **consistent file naming and patterns** across modules. Baseline structure includes `models.py`, `types.py`, `enums.py`, `exceptions.py`, `__init__.py`, but the number of files is flexible: use more files if domain complexity requires it; use fewer if certain file types aren't needed. The goal is consistency in naming and patterns within each domain.
- Always `async def` for any I/O (never sync wrappers)
- HTTP clients: always `aiohttp`, NEVER `httpx`
- Structs/value types: `msgspec.Struct`, not `@dataclass`

**Step 3 — Lint**
```bash
# Fix auto-fixable issues
.venv/bin/ruff check --fix src/css/<path>/
# Verify clean (re-run ONCE, fail if errors remain)
.venv/bin/ruff check src/css/<path>/
```

**Step 4 — Run dependency analyzer (verify no illegal deps added)**
```bash
.venv/bin/python .plan/codebase_dependency_analyzer.py . \
  --path src/css/modules/<module>/ --output /tmp/deps_check.json
.venv/bin/python -c "
import json
d = json.load(open('/tmp/deps_check.json'))
for f, data in d.items():
    for dep in data['consumes']:
        if dep.startswith('src/css/modules/') and not dep.startswith('src/css/modules/<module>/'):
            print(f'ILLEGAL DEP: {f} consumes {dep}')
"
```

---

### 🔵 POST-TODO (run AFTER implementation)

**Step 1 — Update local plan.md**
```bash
# Find the checklist item and mark it checked (use sed, not nano!)
sed -i 's/- \[ \] \(.*TODO_ID.*\)/- [x] \1/' "src/css/modules/<module>/plan.md"
sed -i "s/Last Updated: .*/Last Updated: $(date +%Y-%m-%d)/" "src/css/modules/<module>/plan.md"
```

**Step 2 — Update .plan/plan.md**
```sql
-- Find the phase section and update todo count
SELECT phase, COUNT(*), SUM(status='done') FROM todos WHERE phase = 'PHASE_NAME' GROUP BY phase;
```

**Step 3 — Mark done**
```sql
UPDATE todos SET status = 'done', updated_at = datetime('now') WHERE id = 'TODO_ID';
```

**Step 4 — Commit (logical and atomic)**
```bash
git add -A
git commit -m "[TODO_ID] Brief description of what was done

- File created/edited: src/css/...
- Class/function implemented: ..."
```

**NEVER add `Co-authored-by:` to any new commit.** Historical commits contain it — do not amend history, but all future commits must omit it.

**Commit rules**:
- **Logical**: Each commit should represent one logical change (one todo, one fix, one feature)
- **Atomic**: Each commit should be self-contained — it compiles, passes ruff, and doesn't break existing functionality
- **Focused**: Don't mix unrelated changes in one commit (e.g., don't combine a todo implementation with an unrelated lint fix)
- **Message format**: `[TODO_ID] Brief description` followed by bullet points of what was done

---

## ✅ WORKFLOW 2 — FINISHING A TASK (all todos in a task are done)

A task is the parent grouping (e.g. "T14.1 @instrument Decorator Core"). When all its todos are `done`:

### 🔴 PRE-TASK (run BEFORE declaring task done)

```sql
-- Verify ALL todos in task are done (replace TASK_NAME)
SELECT id, title, status FROM todos WHERE task = 'TASK_NAME' AND status != 'done';
-- Must return 0 rows
```

**Run dependency analyzer** (full module dep map):
```bash
.venv/bin/python .plan/codebase_dependency_analyzer.py . \
  --path src/css/modules/<module>/ --output /tmp/task_deps.json
```

---

### 🟢 ACTIVE

**Step 1 — Search for duplicated code (USE DEPENDENCY ANALYZER + AST)**
```bash
# Find all files in the task's module(s)
.venv/bin/python .plan/codebase_dependency_analyzer.py . \
  --path src/css/modules/<module>/ --output /tmp/task_deps.json

# Check for duplicated class/function names
.venv/bin/python -c "
import json, ast, pathlib
d = json.load(open('/tmp/task_deps.json'))
files = [k for k in d.keys()]
definitions = {}
for f in files:
    try:
        tree = ast.parse(pathlib.Path('$PWD/' + f).read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                definitions.setdefault(node.name, []).append(f)
    except: pass
for name, locations in definitions.items():
    if len(locations) > 1:
        print(f'DUPLICATE: {name} in {locations}')
"
```

**Step 2 — Run ruff on all touched directories**
```bash
.venv/bin/ruff check --fix src/css/<dir1>/ src/css/<dir2>/
.venv/bin/ruff check src/css/<dir1>/ src/css/<dir2>/
```

**Step 3 — Fix remaining errors (5 turns max)**
Fix the remaining errors of prior ruff run.

---

### 🔵 POST-TASK (run AFTER task complete)

**Step 1 — Update plan.md**
```bash
# Update local plan.md (mark task complete)
sed -i "s/Last Updated: .*/Last Updated: $(date +%Y-%m-%d)/" "src/css/modules/<module>/plan.md"

# Add to .plan/plan.md task section:
echo "**Status**: ✅ DONE — $(date +%Y-%m-%d)" >> .plan/plan.md
```

**Step 2 — Update memory.md**
```bash
# Update the phase table row (done count)
.venv/bin/python -c "
import sqlite3
conn = sqlite3.connect('.plan/session.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*), SUM(status=\"done\") FROM todos WHERE phase = \"PHASE_NAME\"')
total, done = cur.fetchone()
print(f'Phase: {total} total, {done} done')
"
# Edit .plan/memory.md: update the phase row
```

**Step 3 — Commit (logical and atomic)**
```bash
git add -A
git commit -m "[TASK-TASK_NAME] Task complete

- N todos completed
- Ruff: clean (3 passes)"
```

---

## ✅ WORKFLOW 3 — FINISHING A PHASE (all tasks done)

A phase is the top grouping (e.g. "Phase 14 — Event Hooks & Entry/Exit Instrumentation").

### 🔴 PRE-PHASE (run BEFORE declaring phase done)

```sql
-- Verify ALL phase todos are done (replace PHASE_NAME)
SELECT COUNT(*) as remaining FROM todos
WHERE phase = 'PHASE_NAME' AND status != 'done';
-- Must return 0 rows
```

**Run dependency analyzer** (full project impact analysis):
```bash
.venv/bin/python .plan/codebase_dependency_analyzer.py . \
  --output /tmp/full_deps.json
```

---

### 🟢 ACTIVE

**Step 1 — Run ruff on all touched directories (2 passes max)**
```bash
.venv/bin/ruff check --fix src/css/<dir1>/ src/css/<dir2>/
.venv/bin/ruff check src/css/<dir1>/ src/css/<dir2>/
```

**Step 2 — Delegate rubber-duck agent (copy-paste prompt)**
```
Use Task tool with:
- subagent_type: general
- prompt: |
    Analyze the completed phase PHASE_NAME:
    1. Read .plan/plan.md (phase section)
    2. Read .plan/memory.md (phase table)
    3. Read .plan/checkpoints.md
    4. Read all src/css/modules/<module>/plan.md for modules in this phase
    5. Run: python .plan/codebase_dependency_analyzer.py . --path src/css/<module>/
    6. Check: Are all todos really done? Any missing integration points?
    7. Report: Phase completeness score (0-100%), any gaps found, recommendations
```

**Step 3 — Run full test suite**
```bash
.venv/bin/pytest -v
```

---

### 🔵 POST-PHASE (run AFTER phase complete)

**Step 1 — Update all .plan/ files (CHECKLIST)**
```bash
# [ ] .plan/plan.md — mark phase ✅ DONE, update CURRENT STATUS
# [ ] .plan/memory.md — update phase table row (done count, blocked count)
# [ ] .plan/checkpoints.md — add phase checkpoint entry
# [ ] .plan/architecture/*.md — ONLY if system design changed (not for progress tracking)

# Local plan.md files REQUIRED — update every directory you touched:
# [ ] src/css/plan.md — if root-level changes
# [ ] src/css/core/<subdir>/plan.md — for each core subdir touched
# [ ] src/css/modules/<module>/plan.md — for each module touched
# [ ] src/css/api_services/plan.md — if api_services touched
# NOTE: local plan.md files are NOT part of .plan/ whitelist; they are codebase files
```

**Step 2 — Commit (logical and atomic)**
```bash
git add -A
git commit -m "[PHASE-PHASE_NAME] Phase complete

- N todos done across M tasks
- Ruff: clean
- Tests: passing
- .plan/ synced"
```

---

## 🏗️ MODULE FILE PATTERN (always follow this)

Every directory under `src/css/modules/<name>/` should have:

```
modules/<name>/
├── __init__.py      ← REQUIRED. Exports public API via __all__. Nothing else.
├── models.py        ← Tortoise ORM models (auto-discovered by loader if present)
├── endpoints.py     ← FastAPI routes (auto-discovered by loader if present)
├── types.py         ← msgspec.Struct value types (manually imported where needed)
├── enums.py         ← Enum definitions (manually imported where needed)
└── exceptions.py    ← Custom exceptions (manually imported where needed)
```

**Rules**:
- `__all__` lives **only** in `__init__.py`
- Never mix `@dataclass` with `ABC` on the same class — pick one
- `msgspec.Struct` for value types, `Protocol` for structural contracts
- All I/O must be `async def` — never sync
- Never `httpx` — always `aiohttp`
- Never `npm` — always `bun` for frontend

---

## 🚫 NEVER DO THESE

| ❌ WRONG | ✅ RIGHT |
|---------|---------|
| `UPDATE tasks SET status = 'done'` | `UPDATE todos SET status = 'done'` — there is no tasks table |
| `UPDATE todos SET completed_at = ...` | `UPDATE todos SET updated_at = datetime('now')` — no completed_at column |
| `httpx.AsyncClient()` | `aiohttp.ClientSession()` |
| `import npm` / `npx` | `bun run` / `bun install` |
| Create `.md` files outside `.plan/` whitelist | Merge content into whitelisted files |
| `@dataclass class Foo(ABC)` | Choose one: pure abstract `class Foo(ABC)` or pure concrete `@dataclass class Foo` |
| Commit with `Co-authored-by:` trailer | Plain commit message, no trailer |
| Test code during a phase | Test only after the entire phase is complete |
| Cross-module imports | Import only from `core/` between modules |
| Mix unrelated changes in one commit | **Logical and atomic commits** |

---

## 📁 .PLAN/ WHITELIST (7 files only — no others allowed)

```
.plan/
├── plan.md                  ← Master plan, all phases
├── memory.md                ← Compressed session context
├── rules.md                 ← Dev rules (CRITICAL section is absolute)
├── development-workflow.md  ← THIS FILE
├── checkpoints.md           ← Phase summaries
├── session.db               ← ONLY task tracker (SQLite)
└── architecture/            ← System design docs (*.md files)
    ├── observability.md
    ├── sdks.md
    ├── system-overview.md
    └── ... (other arch docs)
```

**If you find a `.md` file under `.plan/` that isn't in this list**: move its content into the nearest whitelisted file, then delete it.

---

**Status**: 📋 Active | **Last Updated**: 2026-05-07

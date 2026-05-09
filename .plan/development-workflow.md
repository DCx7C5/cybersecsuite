# Development Workflow

**⚠️ CRITICAL**: Read this file completely before touching any code. Follow every step exactly. No shortcuts.

**Project root**: `/home/daen/Projects/cybersecsuite/`
**Plan directory**: `/home/daen/Projects/cybersecsuite/.plan/`
**Source directory**: `/home/daen/Projects/cybersecsuite/src/css/`
**Python venv**: `/home/daen/Projects/cybersecsuite/.venv/bin/python`
**Type checker**: `uvx basedpyright` (default scope = touched files or smallest touched directory)

---

## 🔍 DEPENDENCY ANALYZER INTEGRATION

**Script**: `scripts/codebase_dependency_analyzer.py`
**Invocation**: `.venv/bin/python scripts/codebase_dependency_analyzer.py <path> [options]`
**Output**: JSON — `{"<rel/file.py>": {"consumed_by": [...], "consumes": [...], "markdown_references": {...}}}`

### Key Features

| Feature                 | CLI Flags                                                    | Default                                                             | Use When                                                                                                                                                       |
|-------------------------|--------------------------------------------------------------|---------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Convenience mode**    | `scripts/analyzer.py src/css/modules/foo/`                   | auto                                                                | Pass a subdirectory or file; root auto-detected from `.git` / `pyproject.toml`. Parses full project for accurate `consumed_by`, outputs only the focused path. |
| **Bidirectional graph** | (always on)                                                  | —                                                                   | `consumed_by` = who imports me; `consumes` = who I import                                                                                                      |
| **Exclude directories** | `--exclude .git __pycache__ .venv`                           | `.git __pycache__ venv .venv node_modules build dist .idea .vscode` | Skip noise in projects with generated dirs                                                                                                                     |
| **Exclude globs**       | `--exclude-glob '**/migrations/**' '*.generated.py'`         | none                                                                | Skip test files, migrations, generated code                                                                                                                    |
| **Markdown references** | `--markdown-case-insensitive --markdown-max-hits-per-term 5` | off, unlimited, 180 chars                                           | Find docs that mention this file or its symbols — verify docs stay in sync                                                                                     |
| **Skip markdown**       | `--no-markdown-refs`                                         | on                                                                  | Speed up raw dep scans                                                                                                                                         |
| **Output to file**      | `--output /tmp/deps.json`                                    | stdout                                                              | Pipe-able JSON for LLM consumption                                                                                                                             |
| **Import roots**        | `--module-root src/`                                         | auto-detects `src/`                                                 | Projects with unusual package layouts                                                                                                                          |
| **Concurrency**         | `--concurrency 64`                                           | 64                                                                  | Tune for very large projects                                                                                                                                   |

### Mode Examples

```bash
# Convenience mode (subdirectory — root auto-detected):
.venv/bin/python scripts/codebase_dependency_analyzer.py src/css/modules/<module>/ \
  --output /tmp/deps.json

# Convenience mode (single file):
.venv/bin/python scripts/codebase_dependency_analyzer.py src/css/modules/<module>/types.py \
  --output /tmp/deps.json

# Explicit project root + focus (same result):
.venv/bin/python scripts/codebase_dependency_analyzer.py . \
  --path src/css/modules/<module>/ --output /tmp/deps.json

# Cross-module violation check (copy-paste for <module>):
.venv/bin/python scripts/codebase_dependency_analyzer.py src/css/modules/<module>/ \
  --no-markdown-refs --output /tmp/xmod.json
.venv/bin/python -c "
import json
d = json.load(open('/tmp/xmod.json'))
bad = [(f, dep) for f, data in d.items() for dep in data['consumes']
       if dep.startswith('src/css/modules/') and not dep.startswith('src/css/modules/<module>/')]
if bad:
    [print(f'ILLEGAL DEP: {f} -> {dep}') for f, dep in bad]
else:
    print('OK — no cross-module violations')
"

# Markdown reference audit (find docs that reference this module):
.venv/bin/python scripts/codebase_dependency_analyzer.py src/css/modules/<module>/ \
  --markdown-case-insensitive --markdown-max-hits-per-term 5 \
  --markdown-snippet-len 120 --output /tmp/md_refs.json
.venv/bin/python -c "
import json
d = json.load(open('/tmp/md_refs.json'))
for f, data in d.items():
    mref = data.get('markdown_references', {})
    for h in mref.get('file_hits', []):
        print(f\"  {h['markdown_file']}:{h['line']}  ({h['term']})  {h['snippet']}\")
    for sym, symdata in mref.get('symbols', {}).items():
        for h in symdata.get('hits', []):
            print(f\"  {h['markdown_file']}:{h['line']}  [{sym}]  {h['snippet']}\")
"

# Full project impact (PHASE level):
.venv/bin/python scripts/codebase_dependency_analyzer.py . \
  --exclude-glob '**/migrations/**' --markdown-case-insensitive \
  --markdown-max-hits-per-term 3 --output /tmp/phase_deps.json
```

### JSON Output (trivial for LLM to parse):
```json
{
  "src/css/modules/foo/types.py": {
    "consumed_by": ["src/css/modules/foo/endpoints.py"],
    "consumes": ["src/css/core/types.py/base_entity.py"],
    "markdown_references": {
      "file_hits": [{"term": "types.py", "markdown_file": ".plan/types.md", "line": 42, "snippet": "..."}],
      "symbols": {"FooType": {"kinds": ["class"], "definitions": [{"line": 12, "kind": "class"}], "hits": []}}
    }
  }
}
```

### Value per Workflow

| Workflow      | Command                                            | What It Tells You                                 |
|---------------|----------------------------------------------------|---------------------------------------------------|
| **PRE-TODO**  | `convenience mode` → check `consumed_by`           | Who will break if you touch this file             |
| **POST-TODO** | `convenience mode` → check `consumes` cross-module | Did you introduce illegal module imports          |
| **POST-TODO** | `convenience mode` + markdown refs                 | Which docs need updating after symbol renames     |
| **TASK**      | `convenience mode` full module scan                | Module-internal dependency health + circular deps |
| **PHASE**     | `full project scan` + markdown refs                | Project-wide impact analysis + doc sync audit     |

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
ORDER BY sort_order, task, id;

-- Phase summary — how far along is each phase?
SELECT phase,
  COUNT(*) as total,
  SUM(status = 'done') as done,
  SUM(status = 'pending') as pending,
  SUM(status = 'blocked') as blocked,
  SUM(status = 'in_progress') as in_progress
FROM todos GROUP BY phase ORDER BY MIN(sort_order);

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
ORDER BY sort_order, task, id LIMIT 1;

-- 3. Mark it in_progress (replace TODO_ID with result from step 2)
UPDATE todos SET status = 'in_progress', updated_at = datetime('now')
WHERE id = 'TODO_ID';
```

**Read these files** (based on the todo's `phase`/`task`):
```bash
# Always read the local planning markdown for the area you're working in:
cat "src/css/modules/$(echo TODO_ID | cut -d'-' -f1)/$(echo TODO_ID | cut -d'-' -f1).md" 2>/dev/null || \
cat "src/css/core/$(echo TODO_ID | cut -d'-' -f1)/plan.md" 2>/dev/null || \
cat "src/css/api_services/api_services.md" 2>/dev/null

# Read architecture doc if phase mentions it:
# Phase 6 → read .plan/types.md (Phase 6 section)
# Phase 14 → cat .plan/architecture/observability.md
# Phase 21 → cat .plan/architecture/sdks.md

# Read the full todo description:
# SELECT description FROM todos WHERE id = 'TODO_ID';
```

**Run dependency analyzer** (see what depends on your files):
```bash
# Convenience mode — auto-detects project root, focuses on your module
.venv/bin/python scripts/codebase_dependency_analyzer.py src/css/modules/<module>/ \
  --no-markdown-refs --output /tmp/deps.json

# Check consumed_by to know who depends on what you'll touch:
.venv/bin/python -c "
import json
d = json.load(open('/tmp/deps.json'))
for f, data in d.items():
    if data['consumed_by']:
        print(f'{f} is consumed by: {data[\"consumed_by\"]}')
"
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
- In `src/css/modules/`, the local planning document is `src/css/modules/<module>/<module>.md`, not `plan.md`
- In `src/css/modules/*/models.py`, all Tortoise ORM table entities inherit `css.core.db.models.base.BaseModel`
- If a module defines `Enum` classes, put them in `enums.py`
- Never (re)create `src/css/modules/accounts/`, `src/css/modules/events/`, `src/css/modules/memory/`, or `src/css/modules/marketplace/`; these are core-owned only.
- Always `async def` for any I/O (never sync wrappers)
- HTTP clients: always `aiohttp`, NEVER `httpx`
- Structs/value types: `msgspec.Struct`, not `@dataclass`
- Event ownership rule for any TODO/TASK/PHASE touching observability or runtime hooks:
  - Event-emitting classes should inherit `css.core.types.base_emitter.BaseEmitterClass` where practical.
  - Observer hooks belong in `src/css/modules/hooks/registry.py` (`@on_event`, fire-and-forget).
  - Mutating/blocking hooks belong in `src/css/modules/hooks/interceptors.py` (`@pre_hook`, `@post_hook`).

**Step 3 — Lint**
```bash
# Fix auto-fixable issues
.venv/bin/ruff check --fix src/css/<path>/
# Verify clean (re-run ONCE, fail if errors remain)
.venv/bin/ruff check src/css/<path>/
```

**Step 4 — Type-check touched Python files (reasonable scope)**
```bash
# Preferred: run on the exact files you changed
uvx basedpyright src/css/<path>/file1.py src/css/<path>/file2.py

# If the change spans a small cohesive area, run the directory instead
uvx basedpyright src/css/<path>/
```

**Type-check rule**:
- `0 errors` is the gate for the touched scope
- Warnings are advisory: fix the local cheap ones, but do not widen the change just to silence unrelated warnings
- If a directory run drags in unrelated legacy noise, rerun on the exact touched files and continue

**Step 5 — Run dependency analyzer (verify no illegal deps added, check markdown refs)**
```bash
# --- Cross-module violation check ---
.venv/bin/python scripts/codebase_dependency_analyzer.py src/css/modules/<module>/ \
  --no-markdown-refs --output /tmp/deps_check.json
.venv/bin/python -c "
import json
d = json.load(open('/tmp/deps_check.json'))
bad = [(f, dep) for f, data in d.items() for dep in data['consumes']
       if dep.startswith('src/css/modules/') and not dep.startswith('src/css/modules/<module>/')]
if bad:
    [print(f'ILLEGAL DEP: {f} -> {dep}') for f, dep in bad]
else:
    print('OK — no cross-module violations')
"

# --- Markdown reference audit ---
# Finds docs that reference renamed symbols or moved files in this module
.venv/bin/python scripts/codebase_dependency_analyzer.py src/css/modules/<module>/ \
  --markdown-case-insensitive --markdown-max-hits-per-term 5 \
  --markdown-snippet-len 120 --output /tmp/md_refs.json
.venv/bin/python -c "
import json
d = json.load(open('/tmp/md_refs.json'))
for f, data in d.items():
    mref = data.get('markdown_references', {})
    file_hits = mref.get('file_hits', [])
    sym_hits = [(sym, h) for sym, sd in mref.get('symbols', {}).items() for h in sd.get('hits', [])]
    if file_hits or sym_hits:
        print(f'--- {f} ---')
        for h in file_hits:
            print(f\"  MD ref: {h['markdown_file']}:{h['line']}  ({h['term']})\")
        for sym, h in sym_hits[:5]:
            print(f\"  MD ref: {h['markdown_file']}:{h['line']}  [{sym}]\")
"
```

---

### 🔵 POST-TODO (run AFTER implementation)

**Step 1 — Update local module markdown**
```bash
# Find the checklist item and mark it checked (use sed, not nano!)
sed -i 's/- \[ \] \(.*TODO_ID.*\)/- [x] \1/' "src/css/modules/<module>/<module>.md"
sed -i "s/Last Updated: .*/Last Updated: $(date +%Y-%m-%d)/" "src/css/modules/<module>/<module>.md"
```

**Step 2 — Update .plan/plan.md**
```sql
-- Find the phase section and update todo count
SELECT phase, COUNT(*), SUM(status='done') FROM todos WHERE phase = 'PHASE_NAME' GROUP BY phase;
```

**Note**: Do not update `.plan/memory.md` or `.plan/checkpoints.md` here in normal TODO flow. Exception: if you just changed architecture baselines, source-of-truth rules, or tracker structure in a way that would mislead the next session, refresh `.plan/memory.md` immediately.

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
- **Atomic**: Each commit should be self-contained — it compiles, passes ruff, passes touched-scope basedpyright, and doesn't break existing functionality
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

**Run dependency analyzer** (full module dep map + cross-module + markdown refs):
```bash
.venv/bin/python scripts/codebase_dependency_analyzer.py src/css/modules/<module>/ \
  --markdown-case-insensitive --markdown-max-hits-per-term 5 \
  --output /tmp/task_deps.json

# Check cross-module violations
.venv/bin/python -c "
import json
d = json.load(open('/tmp/task_deps.json'))
bad = [(f, dep) for f, data in d.items() for dep in data['consumes']
       if dep.startswith('src/css/modules/') and not dep.startswith('src/css/modules/<module>/')]
if bad:
    [print(f'CROSS-MODULE: {f} -> {dep}') for f, dep in bad]
else:
    print('OK — no cross-module violations')
"

# Check markdown reference coverage for key files
.venv/bin/python -c "
import json
d = json.load(open('/tmp/task_deps.json'))
for f, data in sorted(d.items()):
    mref = data.get('markdown_references', {})
    fh = len(mref.get('file_hits', []))
    syms = len(mref.get('symbols', {}))
    print(f'{f}: {fh} file hits, {syms} symbols referenced in docs')
"
```

---

### 🟢 ACTIVE

**Step 1 — Search for duplicated code (USE DEPENDENCY ANALYZER + AST)**
```bash
# Find all files in the task's module(s) — reuse cached deps from PRE-TASK
.venv/bin/python scripts/codebase_dependency_analyzer.py src/css/modules/<module>/ \
  --no-markdown-refs --output /tmp/task_dedup.json

# Check for duplicated class/function names
.venv/bin/python -c "
import json, ast, pathlib
d = json.load(open('/tmp/task_dedup.json'))
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

**Step 3 — Run basedpyright on touched files or directories**
```bash
# Prefer touched files if the directories are noisy
uvx basedpyright src/css/<dir1>/file1.py src/css/<dir2>/file2.py

# Otherwise run the smallest touched directories
uvx basedpyright src/css/<dir1>/ src/css/<dir2>/
```

**Step 4 — Fix remaining verification failures (5 turns max)**
- Ruff errors: always fix
- Basedpyright errors: always fix in touched scope
- Basedpyright warnings: fix when local and low-cost

---

### 🔵 POST-TASK (run AFTER task complete — ALL steps required)

**Step 1 — Update local module markdown**
```bash
# Mark task complete in the module's markdown file
sed -i "s/Last Updated: .*/Last Updated: $(date +%Y-%m-%d)/" "src/css/modules/<module>/<module>.md"
# Add status line to the task section:
sed -i "/TASK_NAME/a **Status**: ✅ DONE — $(date +%Y-%m-%d)" "src/css/modules/<module>/<module>.md"
```

**Step 2 — Update .plan/plan.md**
```sql
-- Verify task done count for the phase
SELECT phase, COUNT(*), SUM(status='done') FROM todos WHERE task = 'TASK_NAME';
```
```bash
# Update the phase section in .plan/types.md:
# Find the phase section, update todo counts to match session.db
sed -i "s/| Phase X — NAME | N | D | P | B |/| Phase X — NAME | N | D | P | B |/" .plan/types.md
```

**Note**: Do not update `.plan/memory.md` or `.plan/checkpoints.md` at task completion in normal flow. If this task finishes the phase, continue with WORKFLOW 3. Exception: refresh `.plan/memory.md` immediately if the task changed architecture baselines or planning/source-of-truth rules.

**Step 3 — Commit (logical and atomic)**
```bash
git add -A
git commit -m "[TASK-TASK_NAME] Task complete

- N todos completed
- Ruff: clean"
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
# Full project scan with markdown refs (skip test files and migrations for speed)
.venv/bin/python scripts/codebase_dependency_analyzer.py . \
  --exclude-glob '**/migrations/**' '**/tests/**' \
  --markdown-case-insensitive --markdown-max-hits-per-term 3 \
  --output /tmp/full_deps.json

# Summary statistics
.venv/bin/python -c "
import json
d = json.load(open('/tmp/full_deps.json'))
total = len(d)
with_deps = sum(1 for v in d.values() if v['consumes'])
with_callers = sum(1 for v in d.values() if v['consumed_by'])
md_refs = sum(len(v.get('markdown_references', {}).get('file_hits', [])) for v in d.values())
print(f'Total files: {total}')
print(f'Files with imports: {with_deps}')
print(f'Files with dependents: {with_callers}')
print(f'Markdown references: {md_refs}')
"

# Cross-module violation summary
.venv/bin/python -c "
import json
d = json.load(open('/tmp/full_deps.json'))
violations = []
for f, data in d.items():
    for dep in data['consumes']:
        f_mod = f.split('/')[3] if f.startswith('src/css/modules/') else None
        d_mod = dep.split('/')[3] if dep.startswith('src/css/modules/') else None
        if f_mod and d_mod and f_mod != d_mod:
            violations.append((f, dep))
if violations:
    print(f'Cross-module violations: {len(violations)}')
    for f, dep in violations:
        print(f'  {f} -> {dep}')
else:
    print('No cross-module violations')
"
```

---

### 🟢 ACTIVE

**Step 1 — Run ruff on all touched directories (3 passes max)**
```bash
.venv/bin/ruff check --fix src/css/<dir1>/ src/css/<dir2>/
.venv/bin/ruff check src/css/<dir1>/ src/css/<dir2>/
```

**Step 2 — Run basedpyright on touched directories or explicit touched files**
```bash
# Do not default to repo-wide type checking here; keep scope aligned to the phase work
uvx basedpyright src/css/<dir1>/ src/css/<dir2>/

# If needed, narrow to explicit touched files to avoid unrelated legacy noise
uvx basedpyright src/css/<dir1>/file1.py src/css/<dir2>/file2.py
```

**Rule**:
- Phase completion still uses touched-scope basedpyright by default
- Only run repo-wide basedpyright during an intentional type-cleanup task or phase

**Step 3 — Delegate rubber-duck agent (copy-paste prompt)**
```
Use Task tool with:
- subagent_type: general
- prompt: |
    Analyze the completed phase PHASE_NAME:
    1. Read .plan/plan.md (phase section)
    2. Read .plan/memory.md (phase table)
    3. Read .plan/checkpoints.md
    4. Read all src/css/modules/<module>/<module>.md files for modules in this phase
    5. Run: .venv/bin/python scripts/codebase_dependency_analyzer.py \
             src/css/modules/<module>/ \
             --markdown-case-insensitive --markdown-max-hits-per-term 5 \
             --output /tmp/rubberduck_deps.json
    6. Read /tmp/rubberduck_deps.json — check:
       - Cross-module violations (consumes that cross module boundaries)
       - Markdown reference coverage (which docs reference which symbols)
       - consumed_by patterns (who depends on the module's exports)
    7. Check: Are all todos really done? Any missing integration points?
    8. Report: Phase completeness score (0-100%), any gaps found, recommendations
```

**Step 4 — Run full test suite**
```bash
.venv/bin/pytest -v
```

---

### 🔵 POST-PHASE (run AFTER phase complete)

**Step 1 — Update all .plan/ files (CHECKLIST)**
```bash
# [ ] .plan/types.md — mark phase ✅ DONE, update CURRENT STATUS
# [ ] .plan/memory.md — update phase table row (done count, blocked count)
# [ ] .plan/checkpoints.md — add phase checkpoint entry
# [ ] .plan/architecture/*.md — ONLY if system design changed (not for progress tracking)

# Update every touched local planning markdown:
# [ ] src/css/core.md — if root-level changes
# [ ] src/css/core/<subdir>/core.md or the nearest area planning markdown
# [ ] src/css/modules/<module>/<module>.md
# [ ] src/css/api_services/api_services.md
```

**Exception rule**: even if the phase is not finished, update `.plan/memory.md` immediately after major architecture, source-of-truth, or tracker-structure changes so the next session starts from an accurate baseline.

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
- In `models.py`, inherit ORM entities from `css.core.db.models.base.BaseModel`, not raw `tortoise.models.Model`
- In `models.py`, use semantic helpers from `css.core.db.fields` whenever the column meaning matches an existing helper
- All I/O must be `async def` — never sync
- Never `httpx` — always `aiohttp`
- Never `npm` — always `bun` for frontend

---

## 🚫 NEVER DO THESE

| ❌ WRONG                                       | ✅ RIGHT                                                                            |
|-----------------------------------------------|------------------------------------------------------------------------------------|
| `UPDATE tasks SET status = 'done'`            | `UPDATE todos SET status = 'done'` — there is no tasks table                       |
| `UPDATE todos SET completed_at = ...`         | `UPDATE todos SET updated_at = datetime('now')` — no completed_at column           |
| `httpx.AsyncClient()`                         | `aiohttp.ClientSession()`                                                          |
| `import npm` / `npx`                          | `bun run` / `bun install`                                                          |
| Create `.md` files outside `.plan/` whitelist | Merge content into whitelisted files                                               |
| `@dataclass class Foo(ABC)`                   | Choose one: pure abstract `class Foo(ABC)` or pure concrete `@dataclass class Foo` |
| Commit with `Co-authored-by:` trailer         | Plain commit message, no trailer                                                   |
| Test code during a phase                      | Test only after the entire phase is complete                                       |
| Cross-module imports                          | Import only from `core/` between modules                                           |
| Mix unrelated changes in one commit           | **Logical and atomic commits**                                                     |

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

**Status**: 📋 Active | **Last Updated**: 2026-05-09

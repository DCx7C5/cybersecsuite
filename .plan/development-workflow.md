# Development Workflow

**⚠️ CRITICAL**: Read this file completely before touching any code. Follow every step exactly. No shortcuts.

**Project root**: `/home/daen/Projects/cybersecsuite/`
**Plan directory**: `/home/daen/Projects/cybersecsuite/.plan/`
**Source directory**: `/home/daen/Projects/cybersecsuite/src/css/`
**Python venv**: `/home/daen/Projects/cybersecsuite/.venv/bin/python`

---

## ⚡ STARTUP RITUAL — DO THIS FIRST, EVERY SESSION

Run these commands before anything else. They tell you the current state.

```bash
# 1. Go to project root
cd /home/daen/Projects/cybersecsuite

# 2. Check git status (understand what was last touched)
git log --oneline -10
git status
```

```sql
-- 3. Find what todos are ready to work on RIGHT NOW (no blocked deps)
-- Run this in: sqlite3 /home/daen/Projects/cybersecsuite/.plan/session.db
SELECT t.id, t.title, t.phase, t.task
FROM todos t
WHERE t.status = 'pending'
AND NOT EXISTS (
  SELECT 1 FROM todo_deps td
  JOIN todos dep ON td.depends_on = dep.id
  WHERE td.todo_id = t.id AND dep.status != 'done'
)
ORDER BY t.phase, t.task
LIMIT 10;
```

```sql
-- 4. Check if anything is in_progress (was left incomplete)
SELECT id, title, phase, task FROM todos WHERE status = 'in_progress';
```

```bash
# 5. Read the master plan to understand context
head -100 /home/daen/Projects/cybersecsuite/.plan/plan.md
```

**If step 4 returns rows**: finish those in_progress todos BEFORE starting anything new.

---

## 🗃️ SESSION.DB — THE ONLY TASK TRACKER

All work is tracked in `.plan/session.db`. This is a SQLite database.

**How to open it**:
```bash
sqlite3 /home/daen/Projects/cybersecsuite/.plan/session.db
```

**Schema (exact columns — do NOT use columns that aren't listed here)**:

```sql
-- todos table
CREATE TABLE todos (
  id          TEXT PRIMARY KEY,   -- e.g. "events-instrument-decorator"
  title       TEXT NOT NULL,      -- short label
  description TEXT,               -- full implementation spec
  status      TEXT DEFAULT 'pending'
              CHECK(status IN ('pending', 'in_progress', 'done', 'blocked')),
  created_at  TEXT DEFAULT (datetime('now')),
  updated_at  TEXT DEFAULT (datetime('now')),
  phase       TEXT DEFAULT 'unassigned',  -- e.g. "Phase 14 — ..."
  task        TEXT DEFAULT 'unassigned'   -- e.g. "T14.1 ..."
);

-- todo_deps table (dependency links)
CREATE TABLE todo_deps (
  todo_id    TEXT NOT NULL,  -- the todo that is BLOCKED
  depends_on TEXT NOT NULL,  -- the todo that must be DONE first
  PRIMARY KEY (todo_id, depends_on)
);
```

**⚠️ THERE IS NO `tasks` TABLE. THERE IS NO `completed_at` COLUMN. DO NOT USE THEM.**

**Status lifecycle**: `pending` → `in_progress` → `done` (or `blocked`)

---

## ✅ WORKFLOW 1 — COMPLETING A SINGLE TODO

This is the most common workflow. Do this for each todo.

### Step 1 — Pick a todo

```sql
-- Find the first ready todo (no blocked dependencies)
SELECT t.id, t.title, t.description, t.phase, t.task
FROM todos t
WHERE t.status = 'pending'
AND NOT EXISTS (
  SELECT 1 FROM todo_deps td
  JOIN todos dep ON td.depends_on = dep.id
  WHERE td.todo_id = t.id AND dep.status != 'done'
)
ORDER BY t.phase, t.task
LIMIT 1;
```

If this returns nothing: either all todos are done, or all pending todos are blocked. Run this to find out:

```sql
-- See what's blocking everything
SELECT t.id as blocked_todo, t.title, dep.id as blocked_by, dep.status
FROM todos t
JOIN todo_deps td ON t.id = td.todo_id
JOIN todos dep ON td.depends_on = dep.id
WHERE t.status = 'pending' AND dep.status != 'done'
ORDER BY t.phase, t.task;
```

### Step 2 — Mark it in_progress

```sql
-- Replace 'your-todo-id' with the actual id
UPDATE todos SET status = 'in_progress', updated_at = datetime('now')
WHERE id = 'your-todo-id';
```

### Step 3 — Read what the todo actually wants

```sql
SELECT description FROM todos WHERE id = 'your-todo-id';
```

Read the **full description**. It tells you exactly what file to create/edit, what class/function to implement, and what the result should look like.

Also read the relevant architecture doc:
```bash
# For events module work:
cat /home/daen/Projects/cybersecsuite/src/css/modules/events/plan.md
cat /home/daen/Projects/cybersecsuite/.plan/architecture/observability.md

# For SDK/LLM work:
cat /home/daen/Projects/cybersecsuite/.plan/architecture/sdks.md

# For routing/intelligence work:
cat /home/daen/Projects/cybersecsuite/src/css/modules/intelligence/plan.md

# For any module, always read its own plan.md first:
cat /home/daen/Projects/cybersecsuite/src/css/modules/<module_name>/plan.md
```

### Step 4 — Check what already exists

```bash
# See what's already in the relevant directory
ls -la /home/daen/Projects/cybersecsuite/src/css/modules/<module_name>/

# Search for related code
grep -r "ClassName\|function_name" /home/daen/Projects/cybersecsuite/src/css/ --include="*.py" | head -20
```

### Step 5 — Implement the code

- Edit files in `src/css/` only
- Follow the **5-file pattern** for modules: `models.py`, `types.py`, `enums.py`, `exceptions.py`, `__init__.py`
- Always `async def` for any I/O (never sync wrappers)
- HTTP clients: always `aiohttp`, NEVER `httpx`
- Structs/value types: `msgspec.Struct`, not `@dataclass`

### Step 6 — Lint the changed files

```bash
cd /home/daen/Projects/cybersecsuite

# Run ruff on exactly the files you touched (replace path):
/home/daen/Projects/cybersecsuite/.venv/bin/ruff check --fix src/css/modules/<module_name>/
/home/daen/Projects/cybersecsuite/.venv/bin/ruff check src/css/modules/<module_name>/
```

If ruff reports errors: fix them before continuing. Run up to 3 times.

### Step 7 — Update the local plan.md

Every module/api_service/core subdir has its own `plan.md`. Update it:
```bash
# Open the plan.md for the area you worked on
# e.g. nano src/css/modules/events/plan.md
# Update the checklist item to checked: - [x] ...
# Update "Last Updated" date to today (2026-05-04)
```

### Step 8 — Update the master plan.md

Mark done and update in `.plan/plan.md`.


### Step 9 — Mark done and commit

```sql
-- Mark done
UPDATE todos SET status = 'done', updated_at = datetime('now')
WHERE id = 'your-todo-id';
```

```bash
git add -A
git commit -m "[your-todo-id] Brief description of what was done

- File created/edited: src/css/...
- Class/function implemented: ..."
```

**NEVER add `Co-authored-by:` to commits.**

---

## ✅ WORKFLOW 2 — FINISHING A TASK (all todos in a task are done)

A task is the parent grouping (e.g. "T14.1 @instrument Decorator Core"). When all its todos are `done`:

### Step 1 — Verify all todos in the task are done

```sql
-- Replace 'T14.1 @instrument Decorator Core' with the actual task name
SELECT id, title, status FROM todos
WHERE task = 'T14.1 @instrument Decorator Core';
```

All rows must show `status = 'done'`. If any are `pending` or `in_progress`: complete them first.

### Step 2 — Search in the module or codebase for duplicated code warnings

### Step 3 — Run ruff on the area

```bash
DIRECTORIES_WORKED_IN=<space separated list of directories you touched>
/home/daen/Projects/cybersecsuite/.venv/bin/ruff check --fix "$DIRECTORIES_WORKED_IN"
```
### Step 4 - Fix remaining errors (5 turns max)

Fix the remaining errors of prior ruff run

### Step 5 — Update plan.md

In `.plan/plan.md`, find the task section and add a completion note:
```
**Status**: ✅ DONE — 2026-05-04
```

### Step 6 — Update session.db

In `.plan/session.db`, update the corresponding entries.

### Step 7 — Update memory.md

Update memory file at `.plan/memory.md`.


### Step 8 — Create/Update the documentary if needed

Create/Update documentation `docs/` if necessary. 
Also write a concise changelog at `docs/changelog/`.

### Step 9 — Mark TASK done and Commit

```bash
git add -A
git commit -m "[TASK-T14.1] @instrument decorator + singletons complete

- N todos completed
- Ruff: clean (3 passes)"
```


---

## ✅ WORKFLOW 3 — FINISHING A PHASE (all tasks done)

A phase is the top grouping (e.g. "Phase 14 — Event Hooks & Entry/Exit Instrumentation").

### Step 1 — Verify all phase todos are done

```sql
-- Replace phase name with the actual phase
SELECT id, title, status FROM todos
WHERE phase = 'Phase 14 — Event Hooks & Entry/Exit Instrumentation'
AND status != 'done';
```

Must return 0 rows. If not: complete remaining todos first.


### Step 2 — Run ruff on the area

```bash
DIRECTORY_LIST=<space separated list of directories you touched>
/home/daen/Projects/cybersecsuite/.venv/bin/ruff check --fix $DIRECTORY_LIST
```

### Step 3 - Fix remaining errors

Fix the remaining errors of prior ruff output

### Step 3.5 — Repeat Step 3 & 4 up to two times

Run again:
```bash
/home/daen/Projects/cybersecsuite/.venv/bin/ruff check --fix $DIRECTORY_LIST
```

If still errors in ruff output, repeat Step 2 & 3.
If no errors, proceed with next step.

### Step 4 - Delegate rubber-duck agent

Delegate a rubber-duck agent to inspect the complete plan at `.plan/*.md`, `.plan/architecture/*.md`, and a list of directories you worked in as context, as well as a set of tasks to inspect the code and plan.
Let it report back to you, follow recommendations and update TODOs/TASKs/PHASEs if needed.


### Step 5 — Run full test suite

```bash
cd /home/daen/Projects/cybersecsuite
/home/daen/Projects/cybersecsuite/.venv/bin/pytest -v
```

Fix any failures before proceeding.

### Step 6 — Update all .plan/ files

```bash
# These 7 files must be updated (the whitelist):
# 1. .plan/plan.md        — mark phase DONE, add summary
# 2. .plan/memory.md      — update phase row (done count)
# 3. .plan/checkpoints.md — add phase checkpoint entry
# 4. .plan/architecture/observability.md (or relevant arch file)
# 5. The corresponding file in .plan/architecture/*.md (if it exists)
# 6. The local plan.md in every module you touched
```

### Step 7 — Commit

```bash
git add -A
git commit -m "[PHASE-14] Event Hooks & Instrumentation: complete

- 18 todos done across 5 tasks
- Ruff: clean
- Tests: passing
- .plan/ synced"
```

---

## 📊 USEFUL SQL QUERIES (copy-paste ready)

```sql
-- All ready todos (no blocked deps) — use this most often
SELECT t.id, t.title, t.phase, t.task
FROM todos t
WHERE t.status = 'pending'
AND NOT EXISTS (
  SELECT 1 FROM todo_deps td
  JOIN todos dep ON td.depends_on = dep.id
  WHERE td.todo_id = t.id AND dep.status != 'done'
)
ORDER BY t.phase, t.task;

-- Phase summary — how far along is each phase?
SELECT phase,
  COUNT(*) as total,
  SUM(status = 'done') as done,
  SUM(status = 'pending') as pending,
  SUM(status = 'in_progress') as active
FROM todos GROUP BY phase ORDER BY phase;

-- What's blocking a specific todo?
SELECT dep.id as blocking_todo, dep.title, dep.status
FROM todo_deps td
JOIN todos dep ON td.depends_on = dep.id
WHERE td.todo_id = 'your-todo-id';

-- All todos for a specific task
SELECT id, title, status FROM todos WHERE task = 'T14.5 Interceptor Chain';

-- Full description of a todo (to know exactly what to implement)
SELECT id, title, description FROM todos WHERE id = 'your-todo-id';

-- Mark todo in_progress
UPDATE todos SET status = 'in_progress', updated_at = datetime('now') WHERE id = 'your-todo-id';

-- Mark todo done
UPDATE todos SET status = 'done', updated_at = datetime('now') WHERE id = 'your-todo-id';
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

**Status**: 📋 Active | **Last Updated**: 2026-05-04

# Development Workflow

**⚠️ CRITICAL**: AI MUST follow these completion workflows rigorously. Always execute TODO → TASK → PHASE in order. No shortcuts.

**Workspace**: `/home/daen/Projects/cybersecsuite/.plan/`

---

## ✅ COMPLETION WORKFLOWS (Primary Reference)

Follow **exactly one workflow** based on unit size. Always start with **Pre-Task** if beginning a new task.

### 📋 PRE-TODO WORKFLOW (Before starting any todo)

**1. Select next ready todo**

```sql
-- Find next pending todo with no blocking dependencies
SELECT t.id, t.title, t.description FROM todos t
WHERE t.status = 'pending'
AND NOT EXISTS (
  SELECT 1 FROM todo_deps td
  JOIN todos dep ON td.depends_on = dep.id
  WHERE td.todo_id = t.id AND dep.status != 'done'
)
LIMIT 1;
```

**2. Inspect codebase for existing implementation**

```bash
# Based on todo description, search src/css for related files
grep -r "pattern_or_keyword" src/css --include="*.py" | head -20

# Check if module/feature already partially exists
ls -la src/css/modules/  # or api_services/ or core/
```

**3. Adapt todo to existing codebase**

- If partial implementation exists: **Focus on completing it**, not recreating
- If no implementation exists: **Create from scratch** per todo spec
- Update todo description in session.db if assumptions need adjustment
- **Update status to `in_progress` ONLY after adapting** (ready to implement)

**4. Proceed to TODO workflow**

---

### 📋 PRE-TASK WORKFLOW (Before starting any task)

**1. Verify all dependencies are satisfied (UNDERSTANDING STATE)**

```sql
-- Check blocking dependencies
SELECT t.id, t.title FROM todos t
JOIN todo_deps td ON t.id = td.todo_id
JOIN todos dep ON td.depends_on = dep.id
WHERE dep.status != 'done'
AND t.id LIKE 'task-prefix-%';
```

**If blocked**: Document in `plan.md` why this task cannot start. Mark as `blocked` in session.db.

**2. Inspect codebase for existing implementation (UNDERSTANDING STATE)**

```bash
# List files modified during this task's previous todos
git log --name-only --oneline | grep -A 10 "task-prefix"

# Check module/area structure for this task
ls -la src/css/modules/  # or api_services/ or core/
find src/css -type f -name "*.py" | grep -E "(task-keyword)" | head -20
```

**3. Adapt todos to existing codebase (UNDERSTANDING STATE)**

- Review which files already exist from previous work
- Identify gaps that remaining todos should fill
- Update todo descriptions if new files discovered
- Document in `plan.md` any structural assumptions

**4. Deep inspect the PLANNED implementation in .plan/ (UNDERSTANDING INTENT)**

Before looking at actual code, deeply study the PLANNED design in the corresponding .plan/ documentation:

```bash
# Identify task scope (which module/service/area?)
# Example: working on @tools module

# Find corresponding .plan/ documentation:
# Pattern: src/css/{area}/{name}/ → .plan/{area}/{name}.md

# For modules:
cat .plan/modules/tools.md       # Study planned @tools architecture
cat .plan/modules/triage.md      # Study planned @triage architecture
cat .plan/modules/cache.md       # Study planned @cache architecture

# For API services:
cat .plan/api_services/ollama-sdk.md    # Study planned Ollama provider
cat .plan/api_services/openai-sdk.md    # Study planned OpenAI provider

# For core infrastructure:
cat .plan/core/orchestration.md  # Study planned orchestration
cat .plan/core/types.md          # Study planned type system
```

**Deep inspection checklist for .plan/ docs**:
- [ ] **Purpose & Use Cases** — Why does this exist? What problems does it solve?
- [ ] **Architecture & Design** — How is it structured? What patterns?
- [ ] **5-File Pattern** (if module) — models.py, types.py, enums.py, exceptions.py, __init__.py
- [ ] **Integration Points** — Where/how does it connect to other modules?
- [ ] **API & Public Interface** — What classes/functions should be exported?
- [ ] **Performance Targets** — Latency, throughput, accuracy, reliability goals
- [ ] **Success Criteria** — What does "done" look like?
- [ ] **Implementation Roadmap** — Phases/milestones/breakdown
- [ ] **Dependencies & Blockers** — What must be done first?
- [ ] **Known Gaps or TODOs** — What's acknowledged as incomplete?

**Example: Studying .plan/modules/tools.md**:
```bash
$ cat .plan/modules/tools.md | head -200
# Sections to review:
- Purpose: "auto-discover and normalize ALL builtin tools from 26 LLM providers"
- Architecture: registry design, MCP server integration
- 5-File Pattern: models.py (ToolSchema), types.py, enums.py, exceptions.py, __init__.py
- Integration Points: api_services (26 providers), response_strategy_router, REST endpoints
- Performance: <100ms for tool discovery
- Success: All 26 providers catalogued, MCP server running
```

**Why**: You need to deeply understand the INTENDED design before seeing what's been built. This prevents:
- Building the wrong thing
- Missing integration requirements
- Creating inconsistent API
- Duplicating work

**Document findings in session**: Note what the plan says should be built.

**5. Inspect ACTUAL implementation in src/css/**

Now that you understand the PLAN, see what's actually been implemented:

```bash
# For modules (e.g., @tools):
ls -lh src/css/modules/tools/
find src/css/modules/tools -name "*.py" -exec wc -l {} +
cat src/css/modules/tools/__init__.py    # What's exported?
grep -r "class\|def\|TODO" src/css/modules/tools/*.py | head -30

# For API services (e.g., Ollama):
ls -lh src/css/api_services/ollama/
find src/css/api_services/ollama -name "*.py" -exec wc -l {} +
cat src/css/api_services/ollama/__init__.py
grep -r "TODO\|FIXME\|NotImplemented" src/css/api_services/ollama/*.py

# For core infrastructure:
ls -lh src/css/core/orchestration/
find src/css/core/orchestration -name "*.py" -exec wc -l {} +
grep -r "class\|TODO\|FIXME" src/css/core/orchestration/*.py
```

**Inspection checklist for src/css/**:
- [ ] Line counts for each file (size/maturity?)
- [ ] What's exported in `__init__.py`?
- [ ] How many TODOs/FIXMEs exist?
- [ ] What classes/functions are stubbed vs complete?
- [ ] What imports are present? (hints at dependencies)
- [ ] Does code match the todo description?

**6. Compare PLAN vs ACTUAL & understand the GAP**

Now you've seen both:
- **PLAN** (.plan/ docs): What SHOULD be built
- **ACTUAL** (src/css/ code): What HAS been built

Compare to understand the work:

```
Gap = Planned - Actual

Example: @tools module
  Planned: 5-file pattern (models, types, enums, exceptions, __init__)
           + registry.py for 26 providers
           + MCP server integration
  Actual:  registry.py exists but is 0 lines (stub)
           No models.py, types.py, enums.py yet
  
  Gap: Need to implement 4 files + fill in registry.py
```

**Questions to answer**:
- [ ] Does actual implementation match planned architecture?
- [ ] What files are missing?
- [ ] What functions/classes are stubbed (TODO markers)?
- [ ] Are there TODOs in code that match .plan/ sections?
- [ ] What refactoring is needed to match the plan?
- [ ] What's partially done vs not started?

**Document in session**: Update todo descriptions with specific findings.

**If clear**: Proceed to TODO workflow for each todo.

---

### 🔧 TODO COMPLETION WORKFLOW (~1-2 hours, atomic unit)

```sql
-- 1. Mark in_progress
UPDATE todos SET status = 'in_progress' WHERE id = 'my-todo-id';
```

```bash
-- 2. Implement code changes
# Modify files in src/css/
```

```bash
-- 3. Lint (single pass, context-aware)
# If working in modules:
ruff check --fix src/css/modules/<module_name>/

# If working in api_services:
ruff check --fix src/css/api_services/<provider_name>/

# If working in core:
ruff check --fix src/css/core/
```

```bash
-- 4. Delegate rubber-duck agent to deep-inspect .plan/ (SANITY CHECK)
# Launch async rubber-duck agent to verify:
#   - Corresponding .plan/modules/*.md file was updated
#   - Corresponding .plan/api_services/*.md file was updated
#   - Corresponding .plan/core/*.md file was updated
#   - All changes align with todo specification
#   - No conflicts or inconsistencies in .plan/ hierarchy

# Use: task tool with agent_type="explore" to deep-inspect .plan/ directory
# Agent reports findings, then proceed to Step 5
```

```sql
-- 5. Mark done
UPDATE todos SET status = 'done', completed_at = CURRENT_TIMESTAMP WHERE id = 'my-todo-id';
```

```bash
-- 6. Commit work (REQUIRED FINAL STEP)
git add -A
git commit -m "[TODO] my-todo-id: Brief title of what was done

- Specific change 1
- Specific change 2
- Files modified: src/css/module/file.py, etc"
```

**Done.** One todo complete. Simple.

---

### 🎯 TASK COMPLETION WORKFLOW (~2-5 days, 3-5 todos)

**Prerequisites**: All child todos marked `done`.

**1. Code Quality (3-pass Ruff)**

```bash
cd src/css

# Identify which area you worked on, then run:

# If worked in modules/<name>:
for i in {1..3}; do
  echo "=== Ruff Pass $i ==="
  ruff check --fix src/css/modules/<module_name>/
  ruff check src/css/modules/<module_name>/
  if [ $? -eq 0 ]; then
    echo "✓ Pass $i: Clean"
    break
  fi
done

# If worked in api_services/<provider>:
for i in {1..3}; do
  echo "=== Ruff Pass $i ==="
  ruff check --fix src/css/api_services/<provider_name>/
  ruff check src/css/api_services/<provider_name>/
  if [ $? -eq 0 ]; then
    echo "✓ Pass $i: Clean"
    break
  fi
done

# If worked in core:
for i in {1..3}; do
  echo "=== Ruff Pass $i ==="
  ruff check --fix src/css/core/
  ruff check src/css/core/
  if [ $? -eq 0 ]; then
    echo "✓ Pass $i: Clean"
    break
  fi
done
```

**Stop if**: Ruff reports errors after pass 3. Mark task as `blocked` in session.db.

**2. Update .plan/**

```sql
-- Update task status
UPDATE tasks SET 
  status = 'done',
  completed_at = CURRENT_TIMESTAMP
WHERE id = 'phase-X-task-Y';

-- Verify all child todos are done
SELECT * FROM todos WHERE task_id = 'phase-X-task-Y' AND status != 'done';
```

**3. Update plan.md & {core,modules,api_services}/<module or provider or core subdir>/plan.md**

- Add task completion summary
- Mark task as DONE


**4. Update session.db status**

```sql
-- Mark task completed
UPDATE tasks SET status = 'done' 
WHERE id = 'phase-X-task-Y';
```

**5. Delegate agent "rubber-duck"**
- create task with rubber-duck agent that lets him analyze every plan.md in project and .plan/session.db and generally .plan/ 


**6. Commit Work**

```bash
git add -A
git commit -m "[PHASE-X] Task Y: Brief title

- N todos completed
- 3-pass ruff: clean"
```



### 🚀 PHASE COMPLETION WORKFLOW (~2-4 weeks, 4-7 tasks)

**Prerequisites**: All child tasks marked `done`.

**1. Code Quality**

```bash
cd src/css

# Run 3-pass ruff on all areas touched in this phase:
for area in modules api_services core; do
  echo "=== Checking $area ==="
  for i in {1..3}; do
    ruff check --fix src/css/$area/
    ruff check src/css/$area/
    if [ $? -eq 0 ]; then
      echo "✓ $area Pass $i: Clean"
      break
    fi
  done
done

# Run full test suite
pytest -v
```

**Stop if**: Ruff errors after 3 passes OR tests fail. Mark phase as `blocked` in session.db.

**2. Update session.db**
```sql
UPDATE todos SET status = 'done' WHERE phase_id = 'phase-X' AND status != 'done';
```

**3. Sync all .plan/ files** (8 files total):
- `plan.md` — Phase summary, next steps
- `architecture.md` — New patterns, diagrams
- `rules.md` — New rules discovered
- `features_overview.md` — Mark complete
- `checkpoints.md` — Phase checkpoint
- `development-workflow.md` — New workflows
- `frontend.md` — UI changes
- `session.db` — All status updates

**4. Commit Phase**
```bash
git commit -m "[PHASE-X] Phase Name: Summary

- All X tasks completed (Y todos)
- 3-pass ruff: clean
- Tests: passing
- .plan/ synced"
```

---

## 🗂️ WORKSPACE

### 8-File Whitelist

```
.plan/
├── plan.md                 ← Timeline, milestones, progress
├── development-workflow.md ← THIS FILE (completion workflows)
├── architecture.md         ← System design (or /architecture/ subdir)
├── rules.md                ← Tech stack, patterns, rules
├── features_overview.md    ← Feature specs
├── checkpoints.md          ← Phase summaries
├── frontend.md             ← UI/UX architecture
└── session.db              ← Todo tracker (SQL)
```

### File Responsibilities

| File                        | When to Update             |
|-----------------------------|----------------------------|
| **plan.md**                 | Each task/phase completion |
| **development-workflow.md** | New workflows discovered   |
| **architecture.md**         | New design patterns        |
| **rules.md**                | New rules or patterns      |
| **features_overview.md**    | Features marked complete   |
| **checkpoints.md**          | Phase complete             |
| **frontend.md**             | UI changes                 |
| **session.db**              | Every todo completion      |

---

## 🔄 GIT COMMITS

**Format**: `[PHASE-X] Feature: Brief description`

```bash
git commit -m "[PHASE-0] TeamScope: Add model to scope.py

- Create TeamScope DB model
- Add team_id FK to orchestrator_instances"
```

---

## 📊 USEFUL SQL

**Ready todos** (no pending dependencies):
```sql
SELECT t.* FROM todos t
WHERE t.status = 'pending'
AND NOT EXISTS (
  SELECT 1 FROM todo_deps td
  JOIN todos dep ON td.depends_on = dep.id
  WHERE td.todo_id = t.id AND dep.status != 'done'
);
```

**Blocked todos**:
```sql
SELECT t.id, t.title, dep.id as blocked_by, dep.status
FROM todos t
JOIN todo_deps td ON t.id = td.todo_id
JOIN todos dep ON td.depends_on = dep.id
WHERE dep.status != 'done';
```

**Task progress**:
```sql
SELECT t.id, t.title, COUNT(todo.id) as total,
  SUM(CASE WHEN todo.status = 'done' THEN 1 ELSE 0 END) as done
FROM tasks t
LEFT JOIN todos todo ON t.id = todo.task_id
GROUP BY t.id;
```

---

## 🎓 RULES

1. **Always follow completion workflows** (TODO → TASK → PHASE)
2. **Pre-Task before any task** — Check dependencies
3. **Mark status** before and after work
4. **One todo** = one atomic change (~1-2 hours)
5. **Commit frequently** — After task completion
6. **Update .plan/** — Keep docs in sync
7. **No external files** — Only 8 whitelisted files

---

**Status**: 📋 Active | **Last Updated**: 2026-05-03


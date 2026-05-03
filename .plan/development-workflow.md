# Development Workflow & Guidelines

**Workspace**: `/home/daen/Projects/cybersecsuite/.plan/`  
**Status**: 📋 Process Documentation

---

## 📝 PLANNING PHASES (How We Work)

### Phase: PLAN Mode 🎯
**When**: Requirement gathering, architecture design, task planning  
**What to do**:
- Update `.plan/*.md` documents
- Insert todos into `.plan/session.db` (SQL)
- Describe what needs to happen (not execute yet)
- Review & refine with team

**Artifacts**:
- Markdown plans (*.md files)
- SQL todos (session.db)
- INDEX.md summary
- Decision matrices

**Exit Criteria**:
- ✅ Architecture approved
- ✅ All tasks in session.db
- ✅ Dependencies mapped
- ✅ Ready for execution

---

### Phase: EXECUTE Mode 🚀
**When**: Implementing features, building code  
**What to do**:
- Read plan.md to check current status
- Mark todo `status = 'in_progress'` before starting
- Implement code changes (modify files)
- Git auto-tracking (no manual updates needed)
- Test changes locally
- Mark todo `status = 'done'` when complete

**Artifacts**:
- Code commits (auto-tracked)
- Modified files
- Updated session.db todos
- Test results

**Exit Criteria**:
- ✅ Code passes tests
- ✅ All todos for phase marked 'done'
- ✅ Git commits made
- ✅ Ready for next phase

---

### Phase: VERIFY Mode ✅
**When**: Testing, validation, production readiness  
**What to do**:
- Run full test suite
- Verify no regressions
- Update documentation
- Load test if needed
- Create release notes

**Artifacts**:
- Test results
- Performance metrics
- Release notes
- Updated README

**Exit Criteria**:
- ✅ 100% tests passing
- ✅ No performance regression
- ✅ Docs updated
- ✅ Ready to ship

---

## 🗄️ TODO TRACKING (session.db)

### SQL Queries

**View pending todos** (ready to start):
```sql
SELECT id, title, status FROM todos 
WHERE status = 'pending' 
AND NOT EXISTS (
  SELECT 1 FROM todo_deps td
  JOIN todos dep ON td.depends_on = dep.id
  WHERE td.todo_id = todos.id AND dep.status != 'done'
)
ORDER BY id;
```

**Mark todo in progress**:
```sql
UPDATE todos SET status = 'in_progress' WHERE id = 'phase-0-teamscope';
```

**Mark todo done**:
```sql
UPDATE todos SET status = 'done' WHERE id = 'phase-0-teamscope';
```

**View all todos with status**:
```sql
SELECT id, title, status, 
  (SELECT COUNT(*) FROM todo_deps WHERE todo_id = todos.id) as deps
FROM todos 
ORDER BY status, id;
```

---

## 📂 WORKSPACE STRUCTURE

### 7-File Whitelist (See rules.md § FILE OWNERSHIP)

```
.plan/
├── plan.md                    ← Project overview, timeline, milestones
├── development-workflow.md    ← THIS FILE (development process & workflows)
├── features_overview.md       ← Feature specifications & API surface
├── architecture.md            ← System design, scope hierarchy, database schema
├── rules.md                   ← Development rules, tech stack, patterns
├── checkpoints.md             ← Phase milestones & historical records
├── frontend.md                ← Frontend architecture & UI/UX patterns
└── session.db                 ← TODO tracker (SQLite, authoritative)
```

**IMPORTANT**: Only these 8 files allowed. All content must fit within them.
**NO** external .md files (FEATURES_PLAN, TEAMSCOPE, MASTER_PLAN, DEEP_INSPECTION, INDEX).

### File Responsibilities

| File | Purpose | Content | Update When |
|------|---------|---------|------------|
| **plan.md** | Project overview | Timeline, milestones, status, design decisions | Phase complete |
| **development-workflow.md** | Development process | TODO/TASK/PHASE workflows, SQL queries, git process | Workflow changes |
| **features_overview.md** | Feature specifications | Feature 1 (Multi-Orch), Feature 2 (TeamScope), API surface | Feature spec change |
| **architecture.md** | System design | Scope hierarchy, orchestrator design, database schema, Role layer, SDK tools | Architecture changes |
| **rules.md** | Development rules | Tech stack, module pattern, config pattern, code conventions | Rule changes |
| **frontend.md** | Frontend architecture | UI/UX patterns, component structure, styling, state management | Frontend spec change |
| **checkpoints.md** | Historical milestones | Phase summaries, decisions made, lessons learned | Phase complete |
| **session.db** | Todo tracker | Phases, tasks, todos, dependencies, update log | Every phase completion |

---

## 🔄 GIT WORKFLOW

### Commits
**Format**: Git auto-tracks commits (no manual update needed)

**Message pattern**:
```
[PHASE-X] Feature: Brief description

Longer description of what changed and why.
```

**Example**:
```
[PHASE-0] TeamScope: Add TeamScope model to scope.py

- Create TeamScope DB model with orchestrator config
- Add team_id FK to orchestrator_instances table
- Extend SessionScope with max_teams, team_count fields
- Create Team entity dataclass
```

### Branch Strategy
- Work on `main` (or create feature branch if needed)
- Commits auto-tracked in git
- .plan/ files NOT committed to source (planning workspace)
- `.plan/session.db` tracked (todo source of truth)

---

## 📋 PHASE CHECKLIST

### Before Starting Phase
- [ ] Read `plan.md` (current status)
- [ ] Check `session.db` for ready todos (not blocked)
- [ ] Review `architecture.md` or `features_overview.md` for context
- [ ] Understand dependencies in todo_deps

### During Phase
- [ ] Mark todo `status = 'in_progress'`
- [ ] Implement code changes (modify `/src/`)
- [ ] Test locally (pytest, linting)
- [ ] Commit changes (git auto-tracks)
- [ ] Document any blockers

### After Phase
- [ ] Mark todo `status = 'done'`
- [ ] All tests passing
- [ ] Verify no regressions
- [ ] Update `plan.md` with completion status
- [ ] Ready for next phase

---

## 🚨 BLOCKING PATTERNS

### If blocked by dependency
```sql
-- Check what's blocking this todo
SELECT dep.id, dep.title, dep.status 
FROM todo_deps td
JOIN todos dep ON td.depends_on = dep.id
WHERE td.todo_id = 'my-blocked-todo'
AND dep.status != 'done';

-- Manually unblock if needed (rare)
UPDATE todos SET status = 'done' WHERE id = 'blocking-todo';
```

### If todo needs re-planning
```sql
-- Mark as blocked with reason
UPDATE todos SET status = 'blocked' 
WHERE id = 'my-todo';

-- Add to description why blocked
UPDATE todos SET description = 
  'Original: ... Blocked: reason here' 
WHERE id = 'my-todo';
```

---

## 📊 METRICS & TRACKING

### Per-Phase Metrics
- Time spent
- Todos completed
- Tests added
- Code commits
- Issues found

### Query examples:
```sql
-- Count todos per status
SELECT status, COUNT(*) FROM todos GROUP BY status;

-- List all Phase 1 todos
SELECT * FROM todos WHERE id LIKE 'phase-1%';

-- Check dependencies
SELECT COUNT(*) FROM todo_deps;
```

---

## 🎓 BEST PRACTICES

1. **One todo = One task** — Atomic, completable in 1-2 days
2. **Clear descriptions** — Someone else should understand it
3. **Track dependencies** — Use todo_deps for blockers
4. **Commit frequently** — Small commits, clear messages
5. **Test before done** — Mark 'done' only when passing
6. **Update docs** — Keep plan.md in sync with reality
7. **Communicate blockers** — Early & often

---

## 🔗 RELATED DOCS

- **plan.md** — Overview & milestones
- **architecture.md** — System design & decision documentation
- **features_overview.md** — Feature specifications & requirements
- **rules.md** — Development rules & module patterns

---

**Last Updated**: 2026-05-03  
**Status**: Active (PLAN mode)

---

## Tracking 115 Todos (NEW)

### Todo Categories

| Category | Count | Status | Docs |
|----------|-------|--------|------|
| Architecture (Phases 0-6) | 10 | 1 done, 9 pending | phases-* |
| SDK Pattern (response.py + 4 SDKs + unified client) | 15 | 0 done, 15 pending | response-*, unified-* |
| Module Consistency (19 modules, 95 files) | 42 | 0 done, 42 pending | modules-* |
| Core Consistency (8 subdirs, 28 files) | 38 | 0 done, 38 pending | core-*, loader-core* |
| Multi-Orchestrator Feature | 10 | 0 done, 10 pending | orchestrator-* |
| TeamScope Feature | 12 | 0 done, 12 pending | teamscope-* |
| Other (inspection, consolidation) | 10 | 7 done, 3 pending | agent-*, consolidate-*, etc. |
| **TOTAL** | **137** | **8 done, 129 pending** | — |

### SQL Query: Show Ready Todos

```sql
-- Todos with no pending dependencies (ready to work)
SELECT t.* FROM todos t
WHERE t.status = 'pending'
AND NOT EXISTS (
  SELECT 1 FROM todo_deps td
  JOIN todos dep ON td.depends_on = dep.id
  WHERE td.todo_id = t.id AND dep.status != 'done'
);
```

### SQL Query: Track Progress by Track

```sql
SELECT 
  CASE 
    WHEN id LIKE 'response-%' OR id LIKE 'unified-%' THEN 'SDK Pattern'
    WHEN id LIKE 'modules-%' THEN 'Module Consistency'
    WHEN id LIKE 'core-%' OR id LIKE 'loader-core%' THEN 'Core Consistency'
    WHEN id LIKE 'phase-%' THEN 'Architecture'
    ELSE 'Other'
  END as track,
  COUNT(*) as total,
  SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
  SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as done
FROM todos
GROUP BY track
ORDER BY track;
```

### SQL Query: Add Todo & Dependency

```sql
-- Example: Add new todo with dependency
INSERT INTO todos (id, title, description, status) VALUES
  ('my-task-id', 'My Task Title', 'Description here', 'pending');

INSERT INTO todo_deps (todo_id, depends_on) VALUES
  ('my-task-id', 'dependency-todo-id');
```

---

## 📊 HIERARCHY: PHASE > TASK > TODO

```
PHASE (7 total, ~2-4 weeks each)
  ├─ TASK (31 total, ~2-5 days each)
  │   └─ TODO (133 total, ~1-2 hours each)
```

### Schema

**phases** table:
- id, title, description, duration_days, status (pending/in_progress/done), timestamps

**tasks** table:
- id, phase_id, title, description, duration_days, priority, status, timestamps

**todos** table:
- id, task_id, title, description, status, dependencies (todo_deps), timestamps

---

## ✅ TODO COMPLETION WORKFLOW

**Smallest atomic unit (1-2 hours)**

```sql
-- 1. Start todo
UPDATE todos SET status = 'in_progress' WHERE id = 'my-todo-id';
```

```bash
-- 2. Implement changes (modify src/css/)
```

```bash
-- 3. Run ruff on changed files (no output check)
ruff check --fix src/css/modules/my_module/
```

```sql
-- 4. Mark done
UPDATE todos SET 
  status = 'done',
  completed_at = CURRENT_TIMESTAMP
WHERE id = 'my-todo-id';
```

**That's it.** Single todo is complete. No ceremony.

---

## 🎯 TASK COMPLETION WORKFLOW

**Medium work unit (2-5 days, contains 3-5 todos)**

After all child todos marked `done`:

### 1. Code Quality (3-pass Ruff)

```bash
cd src/css

for i in {1..3}; do
  echo "=== Ruff Pass $i ==="
  ruff check --fix
  ruff check
  if [ $? -eq 0 ]; then
    echo "✓ Pass $i: Clean"
    break
  fi
done
```

**Stop if**: Ruff reports errors after pass 3. Mark task as `blocked` in session.db.

### 2. Update .plan/

```sql
-- Update task status
UPDATE tasks SET 
  status = 'done',
  completed_at = CURRENT_TIMESTAMP
WHERE id = 'phase-X-task-Y';

-- Verify all child todos are done
SELECT * FROM todos WHERE task_id = 'phase-X-task-Y' AND status != 'done';
```

Update `.plan/` files:
- **plan.md**: Add TASK-Y completion summary, update milestones

### 3. Commit Work

```bash
git add -A
git commit -m "[PHASE-X] Task Y: Brief title

- N todos completed
- 3-pass ruff: clean"
```

**Result**: Task is tracked and committed. Ready for next task.

---

## 🚀 PHASE COMPLETION WORKFLOW

**Largest work unit (~2-4 weeks, contains 4-7 tasks, 20-40 todos)**

After all child tasks marked `done`:

### 1. Code Quality & Testing

```bash
cd src/css

# 3-pass ruff
for i in {1..3}; do
  echo "=== Ruff Pass $i ==="
  ruff check --fix
  ruff check
  if [ $? -eq 0 ]; then
    echo "✓ Pass $i: Clean"
    break
  fi
done

# Run full test suite
pytest -v
```

**Stop if**: Ruff errors after 3 passes OR tests fail. Mark phase as `blocked` in session.db.

### 2. Sync & Update .plan/

Update all 8 allowed files:

```sql
-- Mark phase done
UPDATE phases SET 
  status = 'done',
  completed_at = CURRENT_TIMESTAMP
WHERE id = 'phase-X';

-- Verify all tasks and todos marked done
SELECT COUNT(*) FROM tasks WHERE phase_id = 'phase-X' AND status != 'done';
SELECT COUNT(*) FROM todos WHERE task_id IN 
  (SELECT id FROM tasks WHERE phase_id = 'phase-X') AND status != 'done';
```

**Update .plan/ files**:
- **plan.md**: Add PHASE-X completion summary, update milestones, next steps
- **architecture.md**: Document new design patterns, update module diagrams
- **rules.md**: Add any new rules discovered during implementation
- **features_overview.md**: Mark implemented features as complete
- **checkpoints.md**: Add phase checkpoint with deliverables, blockers, lessons learned
- **development-workflow.md**: Update if new workflows discovered
- **frontend.md**: Update if UI patterns changed
- **session.db**: Sync phase/task/todo status, add new todos for next phase

**Clean bloated content**: Remove redundant sections, consolidate duplicate info.

### 3. Delegate Rubber-Duck Review Agent

```bash
# Agent task: review all modified files in src/css/ against rules.md
```

**Agent verifies**:
- Module pattern: 5-file structure (models, endpoints, types, enums, exceptions) for organization
- Auto-discovery: ONLY models.py and endpoints.py are auto-discovered by loader.py (both optional)
- Types/enums/exceptions: NOT auto-discovered, manually imported where needed
- Config pattern: no hardcoded defaults, all config via config.py
- ABC consistency: no mixing ABC + @dataclass (pure abstract OR pure concrete)
- Async-first: all callables are async (except CLI)
- Scope hierarchy: respected and documented

**Agent updates** (if issues found):
- Add todos for compliance fixes to session.db
- Update rules.md with missed patterns
- Update architecture.md with clarifications

### 4. Update docs/

If documentation changes needed:

```
docs/
├── architecture/       # System design
├── api/               # API reference
├── guides/            # How-to guides
└── changelog/         # Version history
```

- ✅ Update API docs if endpoints changed
- ✅ Update architecture docs if design evolved
- ✅ Add deployment guides if infrastructure changed
- ✅ All filenames use **hyphens** (not underscores)

### 5. Write Changelog Entry

```bash
cd docs/changelog

# Create file: YYYY-MM-DD.md (ISO format)
cat > 2026-05-03.md << 'EOF'
## Phase X: Phase Name — 2026-05-03

### Summary
[2-3 sentence overview of what was accomplished]

### Tasks Completed
- Task 1: Title
- Task 2: Title
- Task 3: Title

### Key Changes
- Feature/pattern 1: description
- Feature/pattern 2: description

### Files Modified
- src/css/modules/X/models.py
- src/css/core/Y/endpoints.py

### Todos Completed
- 24 todos marked done
- 3 new todos added (for next phase)

### Blockers/Issues
[If any]

### Lessons Learned
[Key insights from implementation]
EOF
```

### 6. Commit Phase

```bash
git add -A
git commit -m "[PHASE-X] Phase Name: Summary

- All X tasks completed (Y todos)
- 3-pass ruff: clean
- Tests: passing
- .plan/ synced and updated
- docs/ updated with new patterns
- Changelog entry created
- Rubber-duck review passed"
```

**Commit checklist**:
- ✅ All phase tasks marked `done` in session.db
- ✅ All todos in phase marked `done` in session.db
- ✅ 3-pass ruff: clean
- ✅ All tests passing
- ✅ .plan/ files updated and synced
- ✅ Rubber-duck review completed (no compliance issues)
- ✅ docs/ updated (if necessary)
- ✅ Changelog entry created
- ✅ Commit message format: `[PHASE-X] Title: Summary`

**Result**: Phase officially complete, all work documented, ready for next phase.

---

## 🔍 USEFUL SQL QUERIES

**Show phase progress:**
```sql
SELECT 
  p.id, p.title, p.status,
  COUNT(t.id) as tasks,
  SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) as tasks_done
FROM phases p
LEFT JOIN tasks t ON p.id = t.phase_id
GROUP BY p.id
ORDER BY p.id;
```

**Show task progress:**
```sql
SELECT 
  t.id, t.title, t.status, t.duration_days,
  COUNT(todo.id) as todos,
  SUM(CASE WHEN todo.status = 'done' THEN 1 ELSE 0 END) as todos_done
FROM tasks t
LEFT JOIN todos todo ON t.id = todo.task_id
GROUP BY t.id
ORDER BY t.id;
```

**Show current phase (in_progress):**
```sql
SELECT p.*, COUNT(DISTINCT t.id) as task_count
FROM phases p
LEFT JOIN tasks t ON p.id = t.phase_id
WHERE p.status = 'in_progress'
GROUP BY p.id;
```

**Ready tasks (all todos done):**
```sql
SELECT t.* FROM tasks t
WHERE t.status = 'pending'
AND NOT EXISTS (
  SELECT 1 FROM todos todo
  WHERE todo.task_id = t.id AND todo.status != 'done'
);
```

**Ready todos (no pending deps):**
```sql
SELECT todo.* FROM todos todo
WHERE todo.status = 'pending'
AND NOT EXISTS (
  SELECT 1 FROM todo_deps td
  JOIN todos dep ON td.depends_on = dep.id
  WHERE td.todo_id = todo.id AND dep.status != 'done'
);
```

---

## 📈 PHASES & TASKS SUMMARY

| Phase | Title | Tasks | Duration | Status |
|-------|-------|-------|----------|--------|
| 0 | TeamScope Foundation | 4 | 10d | pending |
| 1 | Multi-Orchestrator Core | 5 | 14d | pending |
| 2 | SDK Pattern & Response | 5 | 12d | pending |
| 3 | Module Consistency | 6 | 14d | pending |
| 4 | Core Consistency | 7 | 12d | pending |
| 5 | Config Integration | 4 | 8d | pending |
| 6 | Integration & Polish | 5 | 14d | pending |
| **TOTAL** | — | **31** | **84d** | — |



# 🎯 Welcome to the Jinja2 Removal Project

## Your Mission

You are an orchestrator agent assigned to execute a **complete removal of Jinja2 templating and the template_engine module** from CyberSecSuite. This is a well-scoped, 12-step refactoring project with clear dependencies and success criteria.

---

## 📚 Quick Start (5 minutes)

### 1. **Read These Files First**
- ✅ **THIS FILE** — You are here (orientation)
- 📖 **PLAN.md** — Detailed implementation plan (read before starting)
- 📋 **CHECKLIST.md** — Step-by-step execution checklist
- 🔍 **ANALYSIS.md** — Deep dive into what gets removed and why

### 2. **Understand the Goal**
Remove **Jinja2** (templating library) and **template_engine** (custom wrapper) from the codebase.  
Replace with lightweight alternatives: **f-strings, str.format(), direct imports**.

**Why?** Jinja2 is heavy. CyberSecSuite barely uses it. Cleaner to remove.

### 3. **Know Your 12 Todos**
The project has exactly **12 todos** organized in **4 phases**:
- **Phase 1:** Audit (1 todo) — understand template complexity
- **Phase 2:** Refactor (6 todos) — replace Jinja2 in 6 modules
- **Phase 3:** Remove (3 todos) — delete dependency + module + imports
- **Phase 4:** Validate (2 todos) — verify nothing broke

### 4. **Check Dependencies**
Dependencies are **strict and sequential**. Todos must be completed in this order:
```
audit-jinja2-templates
  ↓ (6 parallel refactors allowed here)
refactor-* (6 modules)
  ↓
remove-jinja2-pyproject
  ↓
delete-template-engine-module
  ↓
clean-import-statements
  ↓
test-no-import-errors
  ↓
integration-tests-render
```

---

## 🎯 Your Role

As an **orchestrator**, you will:

1. **Understand** the current state (read PLAN.md + ANALYSIS.md)
2. **Plan the execution** (coordinate across 6 refactoring tasks)
3. **Execute todos** in dependency order (use CHECKLIST.md)
4. **Validate** each step (run tests, verify no imports remain)
5. **Report** results (update PROGRESS.md with completion status)

**Do NOT hesitate to:**
- Ask for clarification on any module
- Propose simpler alternatives if Jinja2 replacement is complex
- Create sub-tasks if a todo is too large
- Delegate to specialized agents (e.g., code-review for complex refactors)

---

## 📂 Project Structure

```
/home/daen/Projects/cybersecsuite/
├── plans/                          ← You are here
│   ├── INTRODUCTION.md             ← Orientation (this file)
│   ├── PLAN.md                     ← Full implementation plan
│   ├── CHECKLIST.md                ← Step-by-step checklist
│   ├── ANALYSIS.md                 ← Deep analysis of impact
│   └── PROGRESS.md                 ← (To be created) Your working log
│
├── src/
│   ├── template_engine/            ← TO DELETE (4 files)
│   ├── crypto/template_renderer.py ← TO REFACTOR
│   ├── csmcp/cybersec/template.py  ← TO REFACTOR
│   ├── csmcp/cybersec/skill_manager.py ← TO REFACTOR
│   ├── hooks/sdk_hooks.py          ← TO REFACTOR
│   ├── cybersecsuite/sdk.py        ← TO REFACTOR
│   └── cybersecsuite/_context.py   ← TO REFACTOR
│
└── pyproject.toml                  ← Remove jinja2>=3.1
```

---

## 🔄 Workflow

### For Each Todo:

1. **Check dependencies** — Ensure prerequisite todos are marked 'done'
2. **Read the description** — Understand what needs to change
3. **Implement the change** — Write code / delete files
4. **Run tests** — Verify no breakage
5. **Update status** — Mark todo as 'done' when complete
6. **Move to next** — Follow dependency order

### Use the SQL Todos Table

All 12 todos are tracked in the SQL database. Status values:
- `pending` — Not started
- `in_progress` — You're working on it
- `done` — Complete and verified
- `blocked` — Waiting on something else

**Commands:**
```sql
-- Check todo status
SELECT id, title, status FROM todos ORDER BY id;

-- Update status (when starting a todo)
UPDATE todos SET status = 'in_progress' WHERE id = 'audit-jinja2-templates';

-- Mark as done
UPDATE todos SET status = 'done' WHERE id = 'audit-jinja2-templates';
```

---

## ⚠️ Important Constraints

1. **Drop & Reinit Philosophy** — We can drop/recreate DB tables, so schema is not sacred. But **source code must be clean**.
2. **Backward Compatibility** — Keep SDK API functions (sdk.py render_string/render) for compatibility; just change backend.
3. **No Partial Deletion** — Don't leave orphaned imports or dead code.
4. **Test Everything** — Each refactor must pass existing tests + new verification.

---

## 🎓 Quick Reference: Modules to Refactor

### 1. crypto/template_renderer.py
**Current:** `render_string(template, ctx)` from jinja2  
**After:** `template.format(**ctx)` using Python's str.format()

### 2. csmcp/cybersec/template.py
**Current:** `render(name, extra_vars)` with Jinja2 discovery  
**After:** Load from disk, use str.format()

### 3. csmcp/cybersec/skill_manager.py
**Current:** `discover_skills()` searches templates dynamically  
**After:** Config-based registration (REGISTERED_SKILLS dict)

### 4. hooks/sdk_hooks.py
**Current:** `get_context()` from template_engine  
**After:** Direct `GlobalContext()` instantiation

### 5. cybersecsuite/sdk.py
**Current:** Public `render()` and `render_string()` wrap Jinja2  
**After:** Same API, str.format() backend

### 6. cybersecsuite/_context.py
**Current:** Thin wrapper importing from template_engine  
**After:** Direct import or thin wrapper to new module

---

## 📞 When You're Stuck

1. **Read ANALYSIS.md** — Deep context on each module
2. **Check PLAN.md** — Implementation details per module
3. **Search the codebase** — Find usage patterns
4. **Ask for code review** — Use rubber-duck agent for complex refactors
5. **Propose alternative** — If a refactor seems wrong, suggest better approach

---

## ✅ Success Criteria

✅ All 12 todos marked 'done'  
✅ jinja2 removed from pyproject.toml  
✅ src/template_engine/ directory deleted  
✅ 0 references to jinja2 in source code  
✅ 0 references to template_engine in source code  
✅ All tests pass (unit + integration)  
✅ No ImportError on app startup  
✅ Artifact rendering still works  
✅ MCP tools still work  
✅ Skill discovery still works  

---

## 🚀 Ready to Start?

1. **Read PLAN.md** (10 min) — Understand the full scope
2. **Read ANALYSIS.md** (10 min) — Deep dive into what gets removed
3. **Open CHECKLIST.md** — Start with the first todo
4. **Update PROGRESS.md** — Log your work as you go

---

## 📝 Notes

- **Session ID:** Available in session workspace
- **Database:** All todos in SQL; use `sql` tool to query/update
- **Git:** Commit after each phase (audit, refactor, remove, test)
- **Timeline:** Estimated 4-8 hours total (mostly code refactoring)

---

**Your turn. Good luck! 🎯**

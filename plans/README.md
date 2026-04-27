# 📁 Jinja2 Removal Project — All Files

This directory contains everything an orchestrator agent needs to execute the **Jinja2 and template_engine removal** project.

---

## 📖 Files

### 1. **INTRODUCTION.md** ← START HERE
**Purpose:** Onboarding + orientation  
**Read Time:** 5 minutes  
**Contains:**
- Mission overview
- Quick start guide
- Project structure
- Your role as orchestrator
- Success criteria

**👉 Read this first.**

---

### 2. **PLAN.md**
**Purpose:** Detailed implementation guide  
**Read Time:** 15-20 minutes  
**Contains:**
- Why we're removing Jinja2
- Detailed breakdown of each todo (12 total)
- Step-by-step refactoring for each of 6 modules
- Dependency graph
- Risk mitigation strategies
- Git commit recommendations

**👉 Reference this while implementing.**

---

### 3. **CHECKLIST.md**
**Purpose:** Execution tracking checklist  
**Read Time:** 5 minutes  
**Contains:**
- Checkbox for every step
- Estimated time per task
- SQL commands to mark todos done
- Troubleshooting table
- Timeline tracker

**👉 Use this to track your progress.**

---

### 4. **PROGRESS.md**
**Purpose:** Working log of your session  
**Read Time:** 2 minutes (mostly blank initially)  
**Contains:**
- Status of each todo (to fill in as you work)
- Test results per module
- Blockers / issues encountered
- Git commits made
- Final sign-off

**👉 Update this as you complete each phase.**

---

## 🚀 Getting Started (5 Steps)

1. **Read INTRODUCTION.md** (5 min)
   - Understand mission + structure

2. **Read PLAN.md** (15 min)
   - Get the full picture

3. **Skim CHECKLIST.md** (5 min)
   - See the full task list

4. **Start Phase 1** (see CHECKLIST.md)
   - Run: `audit-jinja2-templates` todo
   - Mark complete in PROGRESS.md

5. **Continue through Phases 2-4**
   - Follow CHECKLIST.md
   - Reference PLAN.md for details
   - Log in PROGRESS.md

---

## 📊 Project Overview

| Aspect | Details |
|--------|---------|
| **Goal** | Remove jinja2 dependency + template_engine module |
| **Scope** | 6 modules, 12 todos, 4 phases |
| **Effort** | 4-8 hours total |
| **Risk** | Medium (straightforward refactoring) |
| **Modules Affected** | crypto, csmcp, hooks, sdk ×2, context |
| **Replacement** | str.format(), f-strings, direct imports |

---

## 🎯 The 12 Todos

### Phase 1: Audit (1)
- `audit-jinja2-templates` — Find templates, assess complexity

### Phase 2: Refactor (6)
- `refactor-artifact-renderer` — crypto/template_renderer.py
- `refactor-mcp-template-tool` — csmcp/cybersec/template.py
- `refactor-skill-discovery` — csmcp/cybersec/skill_manager.py
- `refactor-hook-context` — hooks/sdk_hooks.py
- `refactor-sdk-render` — cybersecsuite/sdk.py
- `refactor-context-wrapper` — cybersecsuite/_context.py

### Phase 3: Remove (3)
- `remove-jinja2-pyproject` — Delete from pyproject.toml
- `delete-template-engine-module` — rm -rf src/template_engine/
- `clean-import-statements` — Verify no remaining imports

### Phase 4: Validate (2)
- `test-no-import-errors` — Unit tests + import checks
- `integration-tests-render` — E2E tests of all modules

---

## 🔄 Execution Flow

```
START
  ↓
Read INTRODUCTION.md
  ↓
Read PLAN.md + CHECKLIST.md
  ↓
Phase 1: Audit
  ├─ Run: audit-jinja2-templates
  └─ Log results in PROGRESS.md
  ↓
Phase 2: Refactor (6 modules)
  ├─ Run: refactor-artifact-renderer
  ├─ Run: refactor-mcp-template-tool
  ├─ Run: refactor-skill-discovery
  ├─ Run: refactor-hook-context
  ├─ Run: refactor-sdk-render
  ├─ Run: refactor-context-wrapper
  └─ Log results + git commits in PROGRESS.md
  ↓
Phase 3: Remove (dependencies + module)
  ├─ Run: remove-jinja2-pyproject
  ├─ Run: delete-template-engine-module
  ├─ Run: clean-import-statements
  └─ Log results in PROGRESS.md
  ↓
Phase 4: Validate (tests)
  ├─ Run: test-no-import-errors
  ├─ Run: integration-tests-render
  └─ Log results + blockers in PROGRESS.md
  ↓
Final Checklist
  ├─ All 12 todos done
  ├─ All tests pass
  ├─ Git history clean
  └─ Sign-off in PROGRESS.md
  ↓
END ✅
```

---

## 💡 Key Concepts

### Why Jinja2?
Jinja2 is a full templating engine. CyberSecSuite uses it minimally (mostly simple variable substitution). Removing it reduces dependency bloat and attack surface.

### Why str.format()?
Python's built-in `str.format()` and f-strings are perfect for simple substitution. No heavy dependency needed.

### Drop & Reinit Philosophy
We can drop/recreate database tables from scratch. But the source code must be clean (no orphaned imports, no dead code).

### Backward Compatibility
Keep SDK public API functions (`render()`, `render_string()`) unchanged so existing clients don't break. Just change the backend.

---

## ⚡ Quick Reference: SQL Todos

Check current status:
```sql
SELECT id, status FROM todos ORDER BY id;
```

Start a todo:
```sql
UPDATE todos SET status = 'in_progress' WHERE id = 'todo-id';
```

Mark as done:
```sql
UPDATE todos SET status = 'done' WHERE id = 'todo-id';
```

---

## 🆘 Need Help?

1. **Stuck on a module?** → Read PLAN.md section for that module
2. **Need a checklist?** → Open CHECKLIST.md
3. **Want to track progress?** → Update PROGRESS.md
4. **Hit a blocker?** → Log in PROGRESS.md, propose alternative approach
5. **Code too complex?** → Ask for rubber-duck review

---

## 📝 Before You Leave

**When you're done, update PROGRESS.md with:**
- ✅ All 12 todos marked done
- ✅ Final time spent
- ✅ Any blockers / learnings
- ✅ Git commits list
- ✅ Sign-off date

---

## 🎓 Success = Done When:

✅ jinja2 removed from pyproject.toml  
✅ src/template_engine/ directory deleted  
✅ 0 jinja2/template_engine references in code  
✅ All tests pass  
✅ No ImportError on startup  
✅ All 6 modules still functional  

---

**Ready? Start with INTRODUCTION.md → then PLAN.md → then CHECKLIST.md**

**Good luck! 🚀**

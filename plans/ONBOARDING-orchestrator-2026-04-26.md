# 🎓 Orchestrator Onboarding Guide (2026-04-26)

## Welcome

You are inheriting the **CyberSecSuite MCP Modernization Project** — a 12-phase infrastructure transformation externalizing 87 tools into 12 self-contained MCPs with comprehensive QA.

**Duration:** 50-68 hours (6-9 days)  
**Status:** ✅ Ready for Phase 0.5 (All blockers resolved)

---

## 📋 What You Need to Do (Right Now)

1. **Read AI Instructions** (5 min)
   - File: `/home/daen/Projects/cybersecsuite/.aiassistant/rules/ai-instructions.md`
   - This is THE reference for all implementation decisions

2. **Read Orchestrator Briefing** (20 min)
   - File: `orchestrator-briefing-mcp-modernization-2026-04-26.md` (this folder)
   - Quick context + phase overview + key docs

3. **Read Main Plan** (1 hour)
   - File: `~/.copilot/session-state/3777f81e-1423-4f67-a498-029f40e5e0df/plan.md`
   - All 12 phases fully specified with deliverables

4. **Setup SQL Todos** (5 min)
   - Query: `SELECT * FROM todos WHERE id LIKE 'phase05%' ORDER BY id;`
   - See Phase 0.5 tasks (5 todos, sequential)

5. **Start Phase 0.5** (2-3 hours)
   - Create marketplace database models
   - Follow plan.md Phase 0.5 section

---

## 📁 Key Files & Folders

### Session Workspace (Source of Truth)
```
~/.copilot/session-state/3777f81e-1423-4f67-a498-029f40e5e0df/
├── plan.md ← MAIN SPEC (all 12 phases + AI instructions)
├── orchestrator-briefing-2026-04-26.md ← Quick onboarding
├── phase10-addendum.md ← Marketplace design blockers resolved
├── phase11-qa-addendum.md ← QA implementation blockers resolved
└── checkpoints/ ← Prior session history
```

### Project Plans (Reference Copy)
```
/home/daen/Projects/cybersecsuite/plans/
├── ONBOARDING-orchestrator-2026-04-26.md ← This file
├── orchestrator-briefing-mcp-modernization-2026-04-26.md ← Briefing copy
└── plan.md ← Project management (parallel streams)
```

### CyberSecSuite Docs Hub
```
/home/daen/Projects/cybersecsuite/docs/
├── index.md ← START HERE (50+ docs, complete reference)
├── architecture/overview.md ← System design
├── mcp/tools.md ← All 87 MCP tools
├── configuration/scope-model.md ← 5-level scope architecture
└── [40+ more docs]
```

### AI Marketplace
```
/home/daen/Projects/ai-marketplace/
├── mcps/ ← 12 MCPs go here (currently 1 placeholder)
├── skills/ ← 799 skills migrate here (Phase 9)
├── agents/ ← 31+ agents already there
├── index.json ← Marketplace catalog
└── docs/ ← Architecture decisions (Pre-Phase-1 done)
```

---

## 🎯 The 12 Phases (Executive Summary)

### Phase 0.5: Marketplace Models & Database (2-3h, NEW)
- Create 6 database models (MarketplaceAsset, MarketplaceMCP, etc.)
- Idempotent seeding for ~890 products
- Install status tracking (available/installed/disabled)
- Enables marketplace persistence

### Phases 1-5: MCP Extraction (22-34h)
- Phase 1: Foundation + CI/CD
- Phase 2-5: Extract 12 MCPs (4 high-priority, 3 medium, 4 operational, 1 special)
- All 87 tools extracted and tested

### Phases 6-9: Integration & Migration (11-15h)
- Phase 6: Testing + docs generation
- Phase 7: Bootstrap installer
- Phase 8: Clean 799 skills
- Phase 9: Migrate skills to marketplace

### Phases 10-11: Marketplace & QA (15-19h)
- Phase 10: Metadata generation + database sync (10.6)
- Phase 11: Comprehensive QA (linting, testing, visual regression, a11y, performance)

---

## ⚠️ CRITICAL: AI Instructions (MUST READ FIRST)

**File:** `/home/daen/Projects/cybersecsuite/.aiassistant/rules/ai-instructions.md`

Before executing ANY code, understand these 7 rules:

1. **Python:** `uv` ONLY (never `pip`/`poetry`)
   - Lint: `ruff check` (zero errors)
   - All DB: async Tortoise ORM
   - All LLM: via AI proxy + OpenObserve logging

2. **TypeScript:** No JavaScript (except browser plugin)
   - Lint: `eslint` (zero errors)
   - Type: `tsc` (zero errors)

3. **Database Storage:**
   - PostgreSQL: relational data, FK models (~41 models)
   - OpenObserve: ALL time-series/audit data
   - Rule: Never add PG table for time-series

4. **MCP Tools:** Follow SDK pattern in `src/csmcp/cybersec/`
   - `@tool()` decorator
   - Register in `__init__.py`

5. **Scope Model:** 5 levels (Global/App/Project/Runtime/Session)
   - Add `runtime_id`, `worktree_path`, `scope_level` to every `ScopedEntry`
   - `.css/` in current working directory

6. **Docker:** Restart services after code changes
   - `docker compose restart cybersec-dashboard`
   - `docker compose restart cybersec-postgres`

7. **Code Quality:**
   - No bare `except:` blocks
   - Specific exception types with logging
   - Docstrings required
   - No `Any` type hints without justification

**Return to this file when uncertain.**

---

## 🚀 Getting Started (Step by Step)

### Step 1: Read Everything (1.5 hours)
```bash
# 1. AI Instructions (CRITICAL)
cat /home/daen/Projects/cybersecsuite/.aiassistant/rules/ai-instructions.md

# 2. This onboarding
cat /home/daen/Projects/cybersecsuite/plans/ONBOARDING-orchestrator-2026-04-26.md

# 3. Orchestrator briefing
cat orchestrator-briefing-mcp-modernization-2026-04-26.md

# 4. Main plan (long but comprehensive)
cat ~/.copilot/session-state/3777f81e-1423-4f67-a498-029f40e5e0df/plan.md | less
```

### Step 2: Understand the Scope
```bash
# Read these CyberSecSuite docs
cat /home/daen/Projects/cybersecsuite/docs/index.md

# Architecture overview
cat /home/daen/Projects/cybersecsuite/docs/architecture/overview.md

# Scope model (important for database design)
cat /home/daen/Projects/cybersecsuite/docs/architecture/scope-architecture.md

# All 87 MCP tools
cat /home/daen/Projects/cybersecsuite/docs/mcp/tools.md | head -100
```

### Step 3: Query the Todos
```bash
# Phase 0.5 tasks (first phase to execute)
sqlite3 ~/.copilot/session-state/3777f81e-1423-4f67-a498-029f40e5e0df/session.db \
  "SELECT id, title FROM todos WHERE id LIKE 'phase05%' ORDER BY id;"

# Check todo status
sqlite3 ~/.copilot/session-state/3777f81e-1423-4f67-a498-029f40e5e0df/session.db \
  "SELECT COUNT(*) as done FROM todos WHERE status = 'done'; \
   SELECT COUNT(*) as pending FROM todos WHERE status = 'pending';"
```

### Step 4: Start Phase 0.5
1. Open plan.md → Phase 0.5 section
2. Execute tasks sequentially (dependencies!)
3. Update SQL todo status as you complete each task

---

## 📊 Success Criteria (Entire Project)

By end of Phase 11:

✅ **Externalization Complete**
- All 87 tools extracted → 12 MCPs
- All MCPs in `ai-marketplace/mcps/`
- Zero circular dependencies
- All support SDK + Stdio modes

✅ **Integration Verified**
- CyberSecSuite boots with externalized MCPs
- All tools callable
- Bootstrap <120s
- No functionality regression

✅ **Marketplace Ready**
- Catalog <1 MB
- Asset-centric + tool-centric search
- Browser renders without full downloads
- Database models synced (~890 products)

✅ **QA Comprehensive**
- Zero linting errors
- Unit tests >85% critical, >70% standard
- Integration tests pass (24 tests)
- Visual regression 0 regressions
- a11y 0 critical violations
- Performance no >15% regression
- CI/CD tiered (<12/<25/<35 min)

✅ **Documentation Complete**
- Auto-generated READMEs
- Marketplace + discovery documented
- Bootstrap documented
- Performance baseline established

---

## 🤝 Rubber-Duck Validation

All major phases have been validated for architectural soundness:

✅ Pre-Phase-1: 4 blockers identified + resolved (8 todos)
✅ Phase 10: 6 blockers identified + resolved (6 addendum todos)
✅ Phase 11: 6 blockers identified + resolved (6 addendum todos)

**Zero architectural unknowns remain.** Ready for execution.

---

## 📞 When You Get Stuck

1. **Check the instructions:** `/home/daen/Projects/cybersecsuite/.aiassistant/rules/ai-instructions.md`
2. **Read the phase spec:** `plan.md` → relevant phase section
3. **Read the addendum:** `phase10-addendum.md` or `phase11-qa-addendum.md`
4. **Check CyberSecSuite docs:** `docs/` (complete reference)
5. **Query SQL todos:** See if dependencies are blocking

---

## 🎯 Key Architecture Decisions (Why)

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Dual-mode MCPs | Reusable internally + externally | Each MCP: SDK or stdio |
| Tool-level metadata | Rich discovery (find tools by name) | Better UX for marketplace |
| Tiered CI pipeline | Fast PR feedback + release validation | PR <12m, main <25m, release <35m |
| Tiered coverage model | Realistic targets, quality focus | Critical 85%, standard 70% |
| Baseline-driven perf | Measured targets, not arbitrary | Baseline captured Phase 11.8 |
| Pre-commit hooks | Developer-side gate | Bugs caught before CI |
| Marketplace models (Phase 0.5) | Persistent product tracking | Install lifecycle + discovery backend |

---

## ✅ You're Ready!

The project is fully scoped, all blockers resolved, and ready for Phase 0.5 execution.

**Next action:** Start Phase 0.5 (Marketplace Models & Database Schema).

Questions? Return to:
- AI Instructions: `/home/daen/Projects/cybersecsuite/.aiassistant/rules/ai-instructions.md`
- Main Plan: `~/.copilot/session-state/.../plan.md`
- This Guide: `/home/daen/Projects/cybersecsuite/plans/ONBOARDING-orchestrator-2026-04-26.md`

Good luck! 🚀

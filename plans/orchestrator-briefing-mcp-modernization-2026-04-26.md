# 🎯 Orchestrator Briefing: CyberSecSuite MCP Modernization

**Date:** 2026-04-26  
**Project:** 12-Phase MCP Externalization + Comprehensive QA (Phase 0.5 added)
**Duration:** 50-68 hours (6-9 days)  
**Status:** ✅ Ready for Phase 0.5 Execution (All blockers resolved)

---

## 🚀 Quick Context

You are inheriting a **massive infrastructure modernization** of CyberSecSuite. The project is transitioning from:

- **Today:** 87 tools in 1 monolithic MCP (`csmcp.cybersec`)
- **Tomorrow:** 12 self-contained, distributable MCPs in `ai-marketplace/mcps/`

Plus a comprehensive QA suite (linting, testing, visual regression, a11y, performance) to ensure production readiness.

---

## ⚠️ CRITICAL: Read AI Instructions FIRST

**Before executing ANY phase:**

📄 **File:** `/home/daen/Projects/cybersecsuite/.aiassistant/rules/ai-instructions.md` (v1.4)

**Key Rules (MUST FOLLOW):**

1. **Python:** `uv` ONLY (never `pip`/`poetry`)
   - Lint: `ruff check` (zero errors)
   - All DB: async Tortoise ORM
   - All LLM: via AI proxy → OpenObserve logging

2. **TypeScript:** No JavaScript (except browser plugin)
   - Lint: `eslint` (zero errors)
   - Type check: `tsc` (zero errors)

3. **Data Storage:**
   - PostgreSQL: relational + FK models (~41 models)
   - OpenObserve: ALL time-series/audit data (never add PG table for time-series)

4. **MCP Tools:** SDK pattern (`src/csmcp/cybersec/`)
   - `@tool()` decorator
   - Register in `__init__.py`

5. **Scope Model:** 5 levels (Global/App/Project/Runtime/Session)
   - Add `runtime_id`, `worktree_path`, `scope_level` to every `ScopedEntry`

6. **Docker:** Restart services after code changes
   - `docker compose restart cybersec-dashboard`
   - `docker compose restart cybersec-postgres`

7. **Code Quality:**
   - Zero exceptions without specific types
   - Avoid bare `except:` blocks
   - No `Any` type hints without justification
   - Docstrings required

**Return to this file when uncertain about implementation patterns.**

---

## 📋 Your Job (Short Version)

Execute 12 phases of work, each with specific deliverables:

- **Phase 0.5** (2-3h): Marketplace models + database schema
- **Phases 1-5** (22-34h): Extract 87 tools into 12 MCPs
- **Phases 6-9** (11-15h): Test, document, integrate, migrate skills
- **Phases 10-11** (15-19h): Marketplace readiness + comprehensive QA

**All phases have:**
- ✅ Detailed specifications in `plan.md`
- ✅ SQL todos with dependencies in `session.db`
- ✅ Blocker analysis documents (`phase10-addendum.md`, `phase11-qa-addendum.md`)
- ✅ Rubber-duck validation (all architectural unknowns eliminated)

### ⚠️ YOUR 4 CORE RESPONSIBILITIES (CRITICAL):

#### 1. Guard Phase Transitions
- Before Phase N: Query SQL to verify Phase N-1 todos are `status='done'`
- After Phase N: Run phase exit validation (documented in plan.md Phase N section)
- If blocked: Document reason + update todo status to `blocked`

#### 2. Create Changelog & Update Documentation  
**After EACH completed phase:**
- ✏️ Create `CHANGELOG.md` entry: date + phase + deliverables + actual duration
- 📝 Update docs if structure changed: `docs/mcp/tools.md`, `docs/database.md`, etc.
- Auto-generate READMEs for new MCPs/skills
- **Before Phase 1 starts:** Create empty `CHANGELOG.md`

#### 3. Commit to Git (With Proper Format)
**After EACH completed phase:**
```bash
git commit -m "Phase N complete: <deliverable-1>, <deliverable-2>, ...

- Extracted tools: X
- Tests: all passing
- Duration: Y hours (planned Z hours)
- Artifacts: [list key files/dirs]

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

#### 4. Spawn Sub-Agents For Complex Work
You have authority to delegate. Use these patterns:

**MCP Extraction (Phases 2-5):**
```
Use `task` agent with type="python-developer"
- Provide: SQL todos for phase + plan.md phase spec
- Verify: All MCP tests pass + no linting errors
- If fails: Rollback phase, fix root cause, re-execute
```

**Testing & QA (Phases 6, 11):**
```
Use `task` agent with type="task"
- Provide: Test matrix + coverage targets
- Verify: pytest passing + coverage >= target
```

**Dependency Analysis (pre-Phase 2):**
```
Use `task` agent with type="explore"
- Provide: Tool inventory + module structure
- Verify: No circular dependencies detected
```

---

## 📚 Documentation You MUST Know

### 1. Main References

| Document | Why It Matters | Location |
|----------|---------------|----------|
| **plan.md** | Master spec for all 12 phases (INCLUDES AI INSTRUCTIONS at top) | `session-state/.../plan.md` |
| **phase10-addendum.md** | Marketplace metadata spec (resolves 6 blockers) | `session-state/.../` |
| **phase11-qa-addendum.md** | QA/testing spec (resolves 6 blockers) | `session-state/.../` |
| **ai-instructions.md** | CRITICAL: 7 key rules before coding | `.aiassistant/rules/` |
| **docs/index.md** | CyberSecSuite doc hub (50+ docs) | `docs/` |
| **docs/architecture/overview.md** | System design | `docs/architecture/` |

### 2. CyberSecSuite Architecture (Must Understand)

These docs are in `/home/daen/Projects/cybersecsuite/docs/`:

```
docs/
├── architecture/
│   ├── overview.md              ← Start here: system layers, data flow
│   ├── scope-architecture.md    ← Scope model (global/app/project/runtime/session)
│   ├── ai-proxy.md              ← AI routing layer
│   ├── data-flow.md             ← Data pipelines
│   └── 6 more architecture docs
├── api/
│   ├── http-endpoints.md        ← /api/*, /sse/* endpoints
│   ├── a2a-protocol.md          ← Agent-to-Agent communication
│   └── dashboard.md
├── mcp/
│   ├── overview.md              ← MCP server architecture
│   ├── tools.md                 ← ALL 87 tools documented here!
│   └── dystopian-tools.md
├── configuration/
│   ├── env-vars.md
│   ├── mcp-json.md              ← How MCPs configured
│   └── scope-model.md
├── development/
│   ├── quickstart.md            ← Get environment up
│   ├── database.md
│   ├── frontend.md
│   └── contributing.md
└── [deployment, features, audits, changelog, hooks]
```

**Key insights:**
- **Scope model:** 5 levels (global/app/project/runtime/session) — understand this for context
- **87 tools:** Fully documented in `docs/mcp/tools.md` — reference for segmentation
- **Data flow:** Understand how tools invoke each other (dependencies)

### 3. Project Plans (Parallel Work)

**Your project:** `/home/daen/Projects/cybersecsuite/plans/plan.md`

This has **2 parallel streams:**
1. **Stream 1:** Remove legacy non-React webinterface (4 phases, independent)
2. **Stream 2:** Remove OpenSearch/Wazu references (2.5 hours, independent)

These can run in parallel with your 11 phases; they don't conflict.

---

## 🎯 The 11 Phases: Executive Summary

### Pre-Phase-1 (2h) — ✅ DONE
- Identified 4 architectural blockers
- Created design documents (shared package, tool discovery, etc.)
- All resolved ✅

### Phase 0.5 (2-3h), Phase 1 (4-6h) — Foundation
- Create MCP template structure
- Setup CI/CD workflows
- Build marketplace installer
- **Gate:** Template ready, CI runs, installer boots

### Phases 2-5 (22-25h) — Extract 12 MCPs
- **Phase 2:** High-priority (4 MCPs, 52 tools)
- **Phase 3:** Medium-priority (3 MCPs, 21 tools)
- **Phase 4:** Operational (4 MCPs, 12 tools)
- **Phase 5:** Special (1 MCP, 12 tools)
- **Gate:** All 87 tools extracted, zero orphans

### Phases 6-9 (11-15h) — Test, Document, Integrate, Migrate
- **Phase 6:** Unit tests, auto-generated docs, index generation
- **Phase 7:** Bootstrap installer (install 7 core MCPs in <120s)
- **Phase 8:** Clean 799 skill files (remove old integration blocks)
- **Phase 9:** Migrate skills to marketplace

### Phase 10 (5-7h) — Marketplace Readiness
- Generate lightweight metadata (catalog.json, asset metadata)
- Enable browser discovery without full downloads
- Implement tool-centric search (find tools across MCPs)
- Deploy to CDN
- **Gate:** Catalog <1 MB, search <200ms, browser renders in <500ms

### Phase 11 (10-12h) — Comprehensive QA
- **Linting:** ESLint, Ruff, mypy (zero errors)
- **Unit tests:** Pytest + Vitest (critical ≥85%, standard ≥70%)
- **Integration:** MCPs, bootstrap, marketplace, 5 tools
- **Visual regression:** Playwright 4-browser baseline
- **a11y:** axe-core audit (0 critical violations)
- **Performance:** Apache Bench + Lighthouse vs baseline
- **CI/CD:** Tiered pipeline (PR <12m, main <25m, release <35m)
- **Console debugging:** Playwright captures browser console logs
- **Gate:** Zero errors, all tests pass, QA_REPORT.md generated

---

## 📊 Key Numbers

| Metric | Value |
|--------|-------|
| Total duration | 50-68 hours (6-9 days) |
| MCPs to extract | 12 |
| Tools to extract | 87 |
| Tool modules | 21 |
| Skills to clean | 799 files |
| Linting tools | 4 (ESLint, Ruff, mypy, yamllint) |
| Test frameworks | 3 (pytest, Vitest, Playwright) |
| Playwright browsers | 4 (Chromium, Firefox, WebKit, Mobile) |
| CI/CD tiers | 3 (PR/main/release) |

---

## 🗂️ Where Everything Is

### Session Files (Your Planning Workspace)
```
~/.copilot/session-state/3777f81e-1423-4f67-a498-029f40e5e0df/
├── plan.md                              ← MAIN SPEC (read first!)
├── phase10-addendum.md                  ← Marketplace blocker resolutions
├── phase11-qa-addendum.md               ← QA/testing blocker resolutions
├── orchestrator-briefing-2026-04-26.md  ← This file
├── checkpoints/                         ← Prior session history
└── files/                               ← Persistent artifacts
```

### CyberSecSuite Project Files
```
~/Projects/cybersecsuite/
├── plans/plan.md                  ← Project plan (2 parallel streams)
├── docs/                          ← 50+ docs (index.md has map)
├── src/
│   ├── csmcp/cybersec/           ← 87 tools to extract (21 modules)
│   ├── frontend/                 ← React SPA (already Phase 5E complete)
│   ├── dashboard/                ← FastAPI backend
│   └── ...
├── templates/skills/             ← 799 skills to clean
├── tests/                        ← Test suite
└── pyproject.toml, Makefile, etc.
```

### AI Marketplace (Destination)
```
~/Projects/ai-marketplace/
├── mcps/                         ← 12 MCPs go here
│   └── playwright/               ← Template example
├── skills/                       ← 799 skills migrate here (Phase 9)
├── agents/                       ← 31 agents (already there)
├── index.json                    ← Marketplace catalog
└── docs/
    ├── TOOL_DISCOVERY.md         ← Architecture decision (Pre-Phase-1)
    └── SHARED_PACKAGE.md         ← Shared code pattern (Pre-Phase-1)
```

---

## 🚀 How to Start

### Step 1: Read These (In Order)
1. `plan.md` (this session) — Full 11-phase spec
2. `phase10-addendum.md` — Understand marketplace metadata design
3. `phase11-qa-addendum.md` — Understand QA tiered approach
4. `docs/index.md` (CyberSecSuite) — Get oriented on docs

### Step 2: Understand the Data
Run these SQL queries:
```sql
-- See all todos (63 total: 21 done, 42 pending)
SELECT id, title, status FROM todos LIMIT 20;

-- See Phase 1 todos (foundation)
SELECT id, title, status FROM todos WHERE id LIKE 'phase1%';

-- See dependencies (chain of work)
SELECT t.id, d.depends_on 
FROM todo_deps d 
JOIN todos t ON d.todo_id = t.id 
LIMIT 20;
```

### Step 3: Begin Phase 1
1. Read `plan.md` → Phase 1 section
2. Update Phase 1 todo status: `UPDATE todos SET status = 'in_progress' WHERE id LIKE 'phase1%';`
3. Execute tasks sequentially (dependencies!)
4. Update status as you complete each task

### Step 4: Each Phase Start
Before starting a new phase:
1. Read the phase section in `plan.md`
2. Check SQL todos for blockers
3. Query `SELECT * FROM todos WHERE id LIKE 'phaseN%' AND status = 'pending';`
4. Execute sequentially, updating status

---

## 🎯 Success Checklist (Entire Project)

By the time Phase 11 is complete:

- [ ] All 87 tools extracted into 12 MCPs ✅
- [ ] All MCPs in `ai-marketplace/mcps/` with full structure ✅
- [ ] CyberSecSuite boots with externalized MCPs ✅
- [ ] Zero circular dependencies ✅
- [ ] Bootstrap installer <120s ✅
- [ ] 799 skills cleaned and migrated ✅
- [ ] Marketplace metadata generated + deployed ✅
- [ ] Catalog <1 MB, search <200ms ✅
- [ ] Zero linting errors ✅
- [ ] Unit tests: critical ≥85%, standard ≥70% ✅
- [ ] Integration tests all pass (24 tests) ✅
- [ ] Visual regression: 0 regressions (4-browser) ✅
- [ ] a11y: 0 critical WCAG violations ✅
- [ ] Performance: no >15% regression vs baseline ✅
- [ ] CI/CD tiered: PR <12m, main <25m, release <35m ✅
- [ ] QA_REPORT.md generated ✅

---

## 🔥 Critical Things NOT to Skip

1. **Read `phase10-addendum.md`** — Contains 6 blocking issues + resolutions (tool metadata, SemVer, asset digest, pipeline, performance, ops)
2. **Read `phase11-qa-addendum.md`** — Contains 6 blocking issues + resolutions (tiered CI, visual regression, coverage model, integration specs, a11y, performance baseline)
3. **Understand the scope model** — Read `docs/architecture/scope-architecture.md` (context for how tools work)
4. **Run SQL todos** — Don't freestyle; follow the todo dependency chain
5. **Capture performance baseline** — Do this BEFORE Phase 1 (Phase 11.8), so Phase 11 can compare against it

---

## 🤝 Rubber-Duck Validation

All major phases have been validated by rubber-duck agent to catch architectural issues:

✅ **Pre-Phase-1 Blockers:** 4 issues identified + 8 todos created (all resolved)  
✅ **Phase 10 Plan:** 6 blocking issues identified + 6 addendum todos (all resolved)  
✅ **Phase 11 Plan:** 6 blocking issues identified + 6 addendum todos (all resolved)

**Total:** 21 architectural unknowns eliminated before Phase 1.

---

## 📞 When You Get Stuck

1. **Check SQL todos** — Maybe dependencies aren't met?
2. **Read `phase10-addendum.md` or `phase11-qa-addendum.md`** — Answers to hard problems
3. **Reread the relevant phase in `plan.md`** — Details are there
4. **Check `docs/`** — CyberSecSuite architecture may clarify

---

## 🎓 Key Architecture Decisions (Why)

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Dual-mode MCPs (SDK + Stdio) | Reusable internally + externally | Each MCP works as in-process or standalone server |
| Tool-level metadata | Search tools individually | Catalog more usable, users find tools faster |
| Tiered CI pipeline | Fast PR feedback + release validation | PR <12m, main <25m, release <35m |
| Tiered coverage model | Realistic targets, quality focus | Critical ≥85%, standard ≥70%, legacy ≥50% |
| Baseline-driven perf | Avoid arbitrary targets | Baseline captured Phase 11.8, targets measured not guessed |
| Pre-commit hooks | Developer-side quality gate | Bugs caught before CI, faster iteration |
| Playwright console debugging | E2E test diagnosis | Failed tests include browser console logs + traces |

---

## ✅ You're Ready!

The project is fully scoped, all blockers resolved, and ready for Phase 1 execution.

**Next action:** Start Phase 1 (Foundation & Scaffolding).

Questions? Re-read `plan.md` or `phase10-addendum.md` / `phase11-qa-addendum.md` for detailed answers.

Good luck! 🚀

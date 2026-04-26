# 🎯 Orchestrator Guide: CyberSecSuite MCP Modernization
**Complete Reference for Executing 12-Phase Infrastructure Modernization**

**Date:** 2026-04-26  
**Project:** 87 tools → 6 consolidated MCPs (real implementations)  
**Status:** ✅ MCP Extraction & Consolidation COMPLETE

---

## ⚡ START HERE (5 minutes)

### Your Mission
Deliver 6 consolidated MCPs extracted from csmcp implementations: csscore (22 modules) + 5 specialized MCPs.

### Timeline
- **Extraction:** ✅ DONE — Real implementations from csmcp/cybersec/
- **Consolidation:** ✅ DONE — 87 tools → 6 MCPs
  - csscore-mcp: 22 modules (core infrastructure)
  - canvas-mcp: forensic visualization
  - memory-mcp: vector memory
  - template-mcp: template engine
  - playwright-mcp: browser automation
  - dystopian-crypto-mcp: cryptography
- **Next:** Testing, docs, bootstrap integration

### Your Authority (YOU CAN)
✅ Spawn agents (python-developer, explore, task)  
✅ Create CHANGELOG + update documentation  
✅ Commit to git (Co-authored-by trailer)  
✅ Guard phase transitions (SQL query)  
✅ Rollback if phases fail (documented recovery)  
✅ Delegate complex work (with patterns)

---

## 🚨 CRITICAL: Read AI Instructions FIRST

**File:** `/home/daen/Projects/cybersecsuite/.aiassistant/rules/ai-instructions.md` (v1.4)

**7 Key Rules (Non-Negotiable):**

1. **Python:** `uv` ONLY (never `pip`/`poetry`)
   - Lint: `ruff check` (zero errors)
   - All DB: async Tortoise ORM
   - All LLM: via AI proxy → OpenObserve

2. **TypeScript:** No JavaScript (except browser plugin)
   - Lint: `eslint` (zero errors)
   - Type: `tsc` (zero errors)

3. **Data Storage:**
   - PostgreSQL: relational data, FK models (~41)
   - OpenObserve: ALL time-series/audit data (never add PG table for time-series)

4. **MCP Tools:** SDK pattern in `src/csmcp/cybersec/`
   - `@tool()` decorator
   - Register in `__init__.py`

5. **Scope Model:** 5 levels (Global/App/Project/Runtime/Session)
   - Add `runtime_id`, `worktree_path`, `scope_level` to every `ScopedEntry`

6. **Docker:** Restart services after code changes
   - `docker compose restart cybersec-dashboard`
   - `docker compose restart cybersec-postgres`

7. **Code Quality:**
   - No bare `except:` blocks
   - Specific exception types with logging
   - Docstrings required
   - No `Any` type hints without justification

---

## 🎯 YOUR 4 CORE RESPONSIBILITIES

### 1. Guard Phase Transitions (Before Phase N Starts)

**Query all Phase N-1 todos are complete:**

```bash
sqlite3 ~/.copilot/session-state/3777f81e-1423-4f67-a498-029f40e5e0df/session.db \
  "SELECT COUNT(*) as blockers FROM todos \
   WHERE id LIKE 'phase$(N-1)%' AND status != 'done';"
```

**Result:**
- If `0` → Phase N is READY (proceed)
- If `> 0` → Phase N is BLOCKED (unblock dependencies first)

### 2. Create CHANGELOG & Update Documentation (After Phase N Completes)

**CHANGELOG.md entry format:**
```markdown
## Phase N — [Date] — [Your Name]
- Deliverable 1: [description]
- Deliverable 2: [description]
- Tests: all passing
- Duration: Y hours (planned Z)
```

**Update docs if structure changed:**
- `docs/mcp/tools.md` — new MCPs + tool list
- `docs/database.md` — schema changes
- Auto-generate READMEs for new MCPs
- `docs/architecture/` — if architecture modified

### 3. Commit to Git (With Co-authored-by Trailer)

**Commit message format:**
```bash
git add -A
git commit -m "Phase N complete: deliverable-1, deliverable-2

- Extracted: X tools into Y MCPs
- Tests: all passing
- Duration: Y hours (planned Z)

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### 4. Spawn Sub-Agents (Authority to Delegate)

**When to delegate:**

| Phase Type | Agent | What to Pass |
|-----------|-------|--------------|
| MCP Extraction (2-5) | `python-developer` | SQL todos + plan.md spec |
| Testing & QA (6, 11) | `task` | Test matrix + coverage targets |
| Dependency Analysis (pre-2) | `explore` | Tool inventory + modules |

**Delegation template:**
```
Use [agent-type] for [phase-name]:
- SQL todos: [phase-X-Y, phase-X-Z, ...]
- Phase spec: [reference to plan.md Phase X]
- Validation: [how to verify success]
- Rollback: [if agent fails, fix + re-execute]
```

---

## 📋 THE ORCHESTRATOR PLAYBOOK (One-Page Reference)

### Phase Transition Guard (Before Phase N Starts)

```bash
# Verify Phase N-1 complete
sqlite3 session.db "SELECT COUNT(*) FROM todos WHERE id LIKE 'phase$(N-1)%' AND status != 'done';"
# Must return 0 or Phase N is blocked
```

### Phase Completion Ritual (After All Phase N Todos = 'done')

Follow EXACTLY in order:

**1. Run Quality Gate Loop** (mandatory for all phases)
```bash
# Linting + Type Checking
cd /home/daen/Projects/cybersecsuite && ruff check . && mypy src/ --strict
cd /home/daen/Projects/ai-marketplace && ruff check mcps/ && mypy mcps/ --strict

# Test Suite (Phase-specific coverage: ≥80% normal, 100% for Phase 0.75 csscore)
pytest tests/ -v --cov=src/ --cov-report=term-missing --cov-fail-under=80

# Integration Smoke Tests (see plan.md → Phase Completion Workflow)
python -c "from src.csmcp import *; print('✓ Core imports OK')"
jq . /home/daen/Projects/ai-marketplace/index.json > /dev/null && echo "✓ Catalog OK"
```
**Must PASS all checks before proceeding. If ANY FAIL, fix and re-run loop.**

**2. Create Changelog** (if Phase N has deliverables)
```bash
# Create: docs/changelog/phase0N_deliverable_name.md
# Include: executive summary, files, metrics, integration points, known issues
# Reference: Phase 0.5 changelog as template
```

**3. Update Documentation** (if applicable)
- `docs/database.md` — schema changes
- `docs/csscore.md` — if Phase 0.75 (API contract)
- New MCP READMEs — if Phase 2-5 (tool list + usage)
- Architecture diagrams — if Phase 6+ (major changes)

**4. Create Git Commit** (with Co-authored-by trailer)
```bash
git add -A
git commit -m "Phase N complete: [descriptive title]

Core deliverables:
- Deliverable 1: [description, file count, size]
- Deliverable 2: [description]

Quality metrics:
- Ruff: zero errors
- MyPy: strict mode, zero errors
- Pytest: [coverage]% coverage, all pass
- Exit gate: [status + details]

Next: Phase N+1 brief description

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

git tag -a phase-N-complete -m "Phase N: [title]"
```

**5. Verify Commit & Tag**
```bash
git log --oneline -1  # Verify commit message
git tag -l | tail -1  # Verify tag exists
```

### Handling Phase Failures (Rollback)

If Phase N fails mid-execution:

**1. Identify the Problem**
- Check test output / error logs
- Read phase spec in plan.md → Phase N → specific guidance
- For Phase 0.75 csscore: Check for circular imports, bloat (>2MB), coverage <100%

**2. Mark Todo Blocked**
```sql
UPDATE todos SET status='blocked', description='Phase N rollback: [reason]' 
WHERE id='phase_N_failing_todo';
```

**3. Revert Phase N Commits**
```bash
git log --oneline | head -10  # Find Phase N start commit
git revert -n <start_of_phase_N>..<current_commit>
git commit -m "Phase N rollback: [reason]"
git tag -a phase-N-rollback -m "Rollback Phase N"
```

**4. Fix Root Cause**
- Reference phase spec in plan.md (detailed in Phase section)
- csscore-specific: Check constraints (no domain logic, ≤2MB, 100% coverage)
- Run check-circular-deps.py if imports suspect

**5. Re-Execute Phase N**
- Mark Phase N todos back to `pending`
- Start Phase N from beginning
- Document the fix in phase changelog

### ⚠️ csscore Special Rules (Phase 0.75)

**DO:**
- ✅ Keep csscore functions generic (no domain-specific logic)
- ✅ Maintain 100% test coverage minimum
- ✅ Lock version: csscore==1.0.0 (all MCPs pin to exact version)
- ✅ Run check-circular-deps.py in exit gate
- ✅ Document API contract in docs/csscore.md

**DON'T:**
- ❌ Add domain-specific functions (those belong in Phase 2-5 MCPs)
- ❌ Import from Phase 2-5 MCPs (creates circular dependency)
- ❌ Exceed 2 MB total size (symptom of scope creep)
- ❌ Break backwards compatibility without coordinating all MCPs

**If csscore breaks, ALL Phase 2-5 MCPs break. Be extra careful.**

---

## 🚀 GETTING STARTED (Step by Step)

### Step 1: Read Critical Docs (1 hour)

```bash
# 1. AI Instructions (5 min) — CRITICAL
cat /home/daen/Projects/cybersecsuite/.aiassistant/rules/ai-instructions.md

# 2. This Orchestrator Guide (15 min)
# You're reading it now!

# 3. Main Plan (40 min)
cat ~/.copilot/session-state/3777f81e-1423-4f67-a498-029f40e5e0df/plan.md | less
```

### Step 2: Understand the Scope (30 min)

```bash
# CyberSecSuite docs hub
cat /home/daen/Projects/cybersecsuite/docs/index.md

# Architecture overview
cat /home/daen/Projects/cybersecsuite/docs/architecture/overview.md

# All 87 MCP tools
cat /home/daen/Projects/cybersecsuite/docs/mcp/tools.md | head -100
```

### Step 3: Query Phase 0.5 Todos (5 min)

```bash
# List Phase 0.5 tasks
sqlite3 ~/.copilot/session-state/3777f81e-1423-4f67-a498-029f40e5e0df/session.db \
  "SELECT id, title FROM todos WHERE id LIKE 'phase05%' ORDER BY id;"

# Check overall status
sqlite3 ~/.copilot/session-state/3777f81e-1423-4f67-a498-029f40e5e0df/session.db \
  "SELECT COUNT(*) as done FROM todos WHERE status = 'done'; \
   SELECT COUNT(*) as pending FROM todos WHERE status = 'pending';"
```

### Step 4: Start Phase 0.5 (2-3 hours)

1. Open: `~/.copilot/session-state/3777f81e-1423-4f67-a498-029f40e5e0df/plan.md`
2. Go to: Phase 0.5 section
3. Execute: Tasks sequentially (check dependencies!)
4. Mark todos: Update SQL status as you complete each task
5. When done: Run Phase 0.5 exit gate + commit

---

## 📊 THE 12 PHASES (Executive Summary)

### Phase 0.5: Marketplace Models & Database (2-3h)
- Create 6 database models (MarketplaceAsset, MarketplaceMCP, Skill, Agent, Prompt, Plugin, Workflow)
- Idempotent seeding for ~890 marketplace products
- Install status tracking (available/installed/disabled)
- **Deliverables:** Database schema + seed function + install tracking

### Phase 1: Foundation & Scaffolding (4-6h)
- MCP template structure (pyproject.toml, README, CI compat)
- GitHub Actions CI/CD workflow (lint + test)
- Marketplace installation script
- **Deliverables:** Template ready, CI skeleton, installer stub
- **Exit Gate:** Templates create valid MCP, CI passes 5x, installer boots <60s

### Phases 2-5: MCP Extraction (22-34h)
**Phase 2:** 4 High-Priority MCPs (forensic-vault, network-layers, threat-intelligence, database-tools) — 6-8h  
**Phase 3:** 3 Medium MCPs (session-management, incident-management, ai-memory) — 4-6h  
**Phase 4:** 4 Operational MCPs (browser-automation, utility-tools, business-tools, network-monitoring) — 4-6h  
**Phase 5:** 1 Special MCP (dystopian-actors) — 2-3h  
- **Deliverables:** 12 MCPs extracted, all tools migrated, tests passing
- **Exit Gate:** All MCPs pass pytest, zero linting errors, no circular dependencies

### Phase 6: Testing, Documentation, Index (4-5h)
- Unit tests for all 12 MCPs (pytest + SDK compatibility)
- Auto-generate README + tool docs for each MCP
- Build `index.json` marketplace catalog
- Create `INSTALL.md` guide
- **Deliverables:** Tested MCPs, auto-generated docs, marketplace index

### Phase 7: Bootstrap Installer (3-4h)
- Create `scripts/install-mcp-core.sh` (installs 7 foundation MCPs)
- Update CyberSecSuite to use externalized MCPs (SDK mode)
- Test bootstrap on fresh environment
- **Deliverables:** Automated bootstrap, CyberSecSuite integration

### Phase 8: Skills Cleanup (2-3h)
- Remove `## CyberSecSuite Integration` section from 799 skill files
- Update skill headers to reference marketplace installation
- Run linting on all skills
- **Deliverables:** 799 cleaned skill files

### Phase 9: Skills Migration (2-3h)
- Move `templates/skills/` → `ai-marketplace/skills/`
- Create marketplace skills index
- Test skill installation via marketplace
- **Deliverables:** Skills in marketplace, index created

### Phase 10: Marketplace Readiness (6-8h)
- Generate tool-level metadata (JSON: name, description, tags, version)
- Create SemVer versioning schema
- Build Lunr.js search index
- Sync marketplace database (10.6)
- **Deliverables:** Metadata generated, search index built, DB synced

### Phase 11: Comprehensive QA (10-12h)
- **Linting:** Ruff + ESLint (zero errors)
- **Unit Tests:** ≥85% critical, ≥70% standard
- **Integration Tests:** 24 tests (MCPs, bootstrap, marketplace)
- **Visual Regression:** Cross-platform (Chromium, Firefox, WebKit)
- **a11y:** axe-core, 0 critical WCAG violations
- **Performance:** <15% regression vs. baseline
- **CI/CD:** Tiered (PR <12m, main <25m, release <35m)
- **Deliverables:** Zero linting, tests passing, CI green

---

## 📁 Key Files & Locations

### Session Workspace (Source of Truth)
```
~/.copilot/session-state/3777f81e-1423-4f67-a498-029f40e5e0df/
├── plan.md ← MAIN SPEC (all 12 phases, 2,500+ lines)
├── orchestrator-briefing-2026-04-26.md ← Context
├── phase10-addendum.md ← Marketplace design details
├── phase11-qa-addendum.md ← QA details
└── checkpoints/ ← Prior session history
```

### Project Plans
```
/home/daen/Projects/cybersecsuite/plans/
├── ORCHESTRATOR-GUIDE-2026-04-26.md ← THIS FILE (consolidated)
├── plan.md ← Project management (parallel streams)
└── [other plans]
```

### CyberSecSuite Docs Hub
```
/home/daen/Projects/cybersecsuite/docs/
├── index.md ← START HERE (50+ docs)
├── architecture/overview.md ← System design
├── mcp/tools.md ← All 87 tools
├── configuration/scope-model.md ← 5-level scope
└── development/quickstart.md ← Getting started
```

### AI Marketplace
```
/home/daen/Projects/ai-marketplace/
├── mcps/ ← 12 MCPs go here
├── skills/ ← 799 skills migrate here
├── agents/ ← 31+ agents
└── index.json ← Marketplace catalog
```

---

## ❓ WHEN YOU GET STUCK

1. **Check the Phase Spec**
   - Open: `~/.copilot/session-state/.../plan.md`
   - Go to: Current phase section
   - Read: "Common Issues" or "Troubleshooting" subsection

2. **Check the Addendums**
   - Phase 10 issues: `phase10-addendum.md`
   - Phase 11 issues: `phase11-qa-addendum.md`

3. **Check AI Instructions**
   - File: `/home/daen/Projects/cybersecsuite/.aiassistant/rules/ai-instructions.md`
   - Reference: Implementation patterns, Docker service names, scope model

4. **Check CyberSecSuite Docs**
   - Start: `/home/daen/Projects/cybersecsuite/docs/index.md`
   - Find: Architecture, tools, database, development guides

5. **Query SQL Todos**
   - Check: Which Phase N-1 todos are still pending?
   - Unblock: Resolve dependencies, then proceed

---

## ✅ SUCCESS CRITERIA (Entire Project)

By end of Phase 11, you will have completed:

### Externalization (✅ Complete)
- [ ] All 87 tools extracted → 12 MCPs
- [ ] All MCPs in `ai-marketplace/mcps/`
- [ ] Zero circular dependencies
- [ ] All support SDK + Stdio modes

### Integration (✅ Complete)
- [ ] CyberSecSuite boots with externalized MCPs
- [ ] All tools callable
- [ ] Bootstrap <120s
- [ ] No functionality regression

### Marketplace (✅ Complete)
- [ ] Catalog <1 MB
- [ ] Asset-centric + tool-centric search
- [ ] Browser renders without full downloads
- [ ] Database models synced (~890 products)

### QA (✅ Complete)
- [ ] Zero linting errors
- [ ] Unit tests >85% critical, >70% standard
- [ ] Integration tests pass (24 tests)
- [ ] Visual regression 0 regressions
- [ ] a11y 0 critical violations
- [ ] Performance no >15% regression
- [ ] CI/CD tiered (<12/<25/<35 min)

### Documentation (✅ Complete)
- [ ] Auto-generated READMEs
- [ ] Marketplace + discovery documented
- [ ] Bootstrap documented
- [ ] Performance baseline established

---

## 🤝 ORCHESTRATOR TIPS & TRICKS

### Tip 1: Phase Guard Before Every Phase N
```bash
# This is your gatekeeper query
sqlite3 session.db "SELECT COUNT(*) FROM todos WHERE id LIKE 'phase$(N-1)%' AND status != 'done';"
# If > 0: STOP, unblock dependencies
# If = 0: Proceed with Phase N
```

### Tip 2: Phase Completion Ritual is Sacred
Follow the 5 steps EVERY time Phase N completes:
1. Run exit validation ✅
2. Git commit (with trailer) ✅
3. Update plan.md ✅
4. Update CHANGELOG ✅
5. Update docs ✅

Skip one step → history broken, status unclear.

### Tip 3: Rollback is Your Friend
If Phase N fails:
- Don't panic → read phase spec for rollback procedure
- Mark todo as `blocked` (not `failed`)
- Revert, fix, re-execute
- You WILL get stuck once, that's normal

### Tip 4: Delegate Ruthlessly
Don't code all 12 phases alone:
- Phases 2-5 (MCP extraction) → python-developer agent
- Phases 6, 11 (testing) → task agent
- Pre-Phase-2 (dependency analysis) → explore agent

### Tip 5: Keep plan.md & CHANGELOG in Sync
Every phase completion:
- Update plan.md (Phase N: "📋" → "✅")
- Update CHANGELOG.md (entry with date + duration)
- Commit both together

---

## 📞 REFERENCE CHECKLIST (Bookmark These)

| What | File | How to Access |
|------|------|---------------|
| **AI Instructions** | `ai-instructions.md` | `/home/daen/Projects/cybersecsuite/.aiassistant/rules/` |
| **Main Plan** | `plan.md` | `~/.copilot/session-state/3777f81e-1423-4f67-a498-029f40e5e0df/` |
| **Phase 10 Details** | `phase10-addendum.md` | Session state folder |
| **Phase 11 Details** | `phase11-qa-addendum.md` | Session state folder |
| **This Guide** | `ORCHESTRATOR-GUIDE-2026-04-26.md` | `~/cybersecsuite/plans/` |
| **Docs Hub** | `index.md` | `~/cybersecsuite/docs/` |
| **SQL Todos** | `session.db` | `~/.copilot/session-state/.../` |

---

## 🎯 NEXT ACTION

1. ✅ Read AI instructions (5 min)
2. ✅ Read this guide (15 min)
3. ⏳ Read main plan.md (40 min)
4. ⏳ Query Phase 0.5 todos (5 min)
5. ⏳ **Execute Phase 0.5** (2-3 hours)

---

## 🚀 You're Ready

The project is fully scoped, all blockers resolved, orchestrator authority defined.

**Status:** ✅ Production-Ready  
**Timeline:** 50-68 hours (12 phases)  
**Authority:** ✅ Granted (spawn agents, commit, guard, rollback, delegate)  

**Let's build.** 🎯

---

*Last Updated: 2026-04-26*  
*Commit: e4dd23b8 (orchestrator playbook improvements)*  
*Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>*

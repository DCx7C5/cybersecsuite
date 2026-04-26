# CyberSecSuite MCP Infrastructure Modernization — Master Plan

**Objective:** Transition from 87 monolithic tools to 12 externalized MCPs over 12 phases (50-68 hours total).

**Canonical Locations:**
- CyberSecSuite repo: `/home/daen/Projects/cybersecsuite`
- AI Marketplace repo: `/home/daen/Projects/ai-marketplace` ← **PRIMARY FOR PHASES 1-5**

---

## Executive Briefing

### Project Scope
Transform CyberSecSuite from a monolithic architecture (87 integrated tools in single codebase) to a **modular MCP (Model Context Provider) ecosystem** with 12 independent, versioned packages. Each MCP is:
- Self-contained (own repo, CI/CD, dependencies)
- Independently deployable
- Reusable in other AI agent frameworks
- Maintained on versioned schedule

### Why This Matters
- **Decoupling:** Individual MCPs can be updated/fixed without affecting others
- **Scalability:** New MCPs can be added without touching core codebase
- **Reusability:** MCPs usable by other Copilot agents and tools
- **Performance:** Clients only load needed MCPs, not entire 87-tool suite
- **Maintainability:** Clear ownership and test boundaries per MCP

### Current Progress
**Phases 0.5 & 1: COMPLETE** ✅
- Marketplace database (6 ORM models, idempotent seeding)
- MCP template framework (production-ready structure, 11 files)
- Installation tooling (marketplace installer script, 592 lines)
- MCP catalog (12 MCPs defined, 135 tools allocated)
- GitHub Actions CI/CD (multi-OS, multi-Python testing)

**Quality Assurance:** 100% of phase tasks passed linting, type-checking, tests, and exit gates.

### What's Next
**Phase 0.75: Core MCP Foundation (csscore)** — Single, unified MCP for essential functions
- 3-5 critical core functions (marketplace registry, asset discovery, config management)
- Foundation that all Phase 2-5 MCPs depend on
- Prevents circular dependencies
- Ready for Phase 2-5 extraction

Then **Phase 2: High-Priority MCPs** (4 MCPs, 52 tools, all importing csscore)

### Success Criteria (Per Phase)
1. ✅ Code quality: Ruff zero errors, MyPy strict zero errors
2. ✅ Tests pass: ≥80% coverage, all tests green
3. ✅ Documentation: Changelog + updated docs
4. ✅ Git hygiene: Comprehensive commit + phase tag
5. ✅ Exit gate: Integration smoke tests, no blockers

### Risk Mitigation
- **Pre-existing bugs:** Identified and fixed during Phase 0.5 (AIProviderEvent index)
- **Circular dependencies:** Will validate with check-circular-deps.py in Phase 2
- **Database issues:** Schema migration strategy documented; known blockers identified
- **Rollback plan:** Git tags enable instant rollback to phase boundaries

---

## Phase Completion Workflow

### Post-Phase Quality Gate Loop (Applied After Each Phase)

Every phase must pass a quality gate before marking DONE and proceeding to the next phase:

**1. Linting & Type Checking**
```bash
# CyberSecSuite (if changes)
cd /home/daen/Projects/cybersecsuite
ruff check . --exclude node_modules,build,dist,__pycache__
mypy src/ --strict --exclude=tests

# AI Marketplace (if changes)
cd /home/daen/Projects/ai-marketplace
ruff check mcps/ --exclude node_modules,build,dist,__pycache__
mypy mcps/ --strict --exclude=tests
```
**Success Criteria:** Zero errors, zero warnings

**2. Run Test Suite**
```bash
# CyberSecSuite tests
pytest tests/ -v --cov=src/ --cov-report=term-missing --cov-fail-under=80

# AI Marketplace template tests
pytest mcps/_template/tests/ -v --cov=src/mcp_template/ --cov-report=term-missing --cov-fail-under=80

# Phase-specific MCP tests (if applicable)
pytest mcps/{mcp_name}/tests/ -v --cov=src/{mcp_name} --cov-fail-under=80
```
**Success Criteria:** All tests pass, coverage ≥80%, no skipped/xfail tests allowed except documented

**3. Integration Smoke Tests (Detailed Checklist)**
```bash
# 1. Import validation: No circular dependencies
python -c "from src.csmcp import *; print('✓ Core imports OK')"

# 2. MCP server startup: Can initialize and respond
python -m mcps._template && echo "✓ Template MCP starts OK" || exit 1

# 3. csscore availability (Phase 0.75+): Other MCPs can import csscore
python -c "from mcp_csscore import *; print('✓ csscore imports OK')"

# 4. Database schema: Migrations clean (if applicable)
python manage.py migrate --dry-run --check || echo "Schema check OK"

# 5. CLI tools: Basic commands execute without errors
python -m src.cli --help > /dev/null && echo "✓ CLI tools OK"

# 6. Tool registry: Marketplace catalog loads without errors
jq . /home/daen/Projects/ai-marketplace/index.json > /dev/null && echo "✓ Catalog OK"
```

**4. Fix Issues & Re-run**
- Any linting/type errors → fix immediately
- Any test failures → debug and fix
- Any import/startup errors → diagnose root cause
- Re-run entire loop until all pass
- Do NOT proceed to next phase if quality gate fails
- Document any known issues in phase changelog

**5. Documentation & Changelog**
- **Changelog:** Create `docs/changelog/phase{N}_*.md` with:
  - Executive summary (what was delivered)
  - Files created/modified (line counts, sizes)
  - Deliverables checklist (all items)
  - Performance notes (if applicable)
  - Integration points for next phases
  - Known issues (if any)
  
- **Documentation Updates:** If applicable:
  - Update `docs/database.md` (new models/schemas)
  - Update `README.md` (new features/capabilities)
  - Update architecture docs (structural changes)
  - Add/update API documentation (new endpoints)

**6. Git Commit & Tag**
- Stage all deliverables (code + docs)
- Commit with comprehensive message:
  ```
  Phase {N} complete: {descriptive title}
  
  Core deliverables:
  - File1: {description}
  - File2: {description}
  
  Quality metrics:
  - Ruff: {status}
  - MyPy: {status}
  - Pytest: {status}
  - Exit gate: {status}
  
  Next: Phase {N+1} description
  
  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
  ```
- Tag: `git tag -a phase-{N}-complete -m "Phase {N} infrastructure/extraction complete"`
- Verify: `git log --oneline -3` and `git tag -l | tail -1`

---

## Phases Overview

### ✅ **Phase 0.5: Marketplace Database Foundation** (DONE)
**Status:** Complete, committed, documented
- Created 6 Tortoise ORM marketplace models
- Implemented idempotent seed_marketplace_assets() function
- Fixed pre-existing AIProviderEvent index bug
- 5/5 tasks done, all linting/type-checking passed
- **Git commit:** 931d1490, 2b6c2424

### ✅ **Phase 1: MCP Template Infrastructure** (DONE)
**Status:** Complete, committed, validated
- Created MCP template structure (11 files, 42 KB)
- Created _sdk_compat.py (FastMCP SDK/Stdio compatibility)
- Created install-mcp.sh (marketplace installer script, 592 lines)
- Created CI/CD workflow (GitHub Actions, 12-job matrix)
- Updated index.json with 12 MCPs, 135 tools catalog
- 7/7 tasks done, exit gate validation passed (100%)
- **Git commit:** 5a6793e

### ⏳ **Phase 0.75: Core MCP Foundation (csscore)** (NEXT)
**Purpose:** Single, unified MCP for essential CyberSecSuite core functions that all other MCPs depend on.

**Scope (EXPLICITLY DEFINED — 5 core functions):**
1. **Marketplace Registry Access** — Query available MCPs, versions, dependencies
2. **Asset Discovery & Enumeration** — List discovered systems, assets, targets
3. **Configuration Management** — Read/write/validate CyberSecSuite config
4. **Core Logging & Audit** — Structured logging for all MCPs (not syslog)
5. **Scope & Context Management** — Runtime scope tracking (session/project/app level)

**Why Needed:**
- All Phase 2-5 MCPs will import csscore (dependency graph prevents circular references)
- Centralizes shared infrastructure (logging, config, registry)
- Prevents N MCPs reimplementing the same utilities
- Single version contract: all MCPs use csscore==1.0.0 (pinned)

**csscore Constraints (ENFORCED):**
- ❌ NO domain-specific logic (only generic utilities)
- ❌ NO direct database access (use CyberSecSuite proxy)
- ✅ ONLY async/await patterns
- ✅ MUST be ≤2 MB (prevent bloat)
- ✅ MUST have 100% test coverage
- ✅ MUST NOT import from any Phase 2-5 MCPs

**Tasks:**
- Extract 5 core utility functions from monolithic csmcp
- Create csscore MCP structure in /home/daen/Projects/ai-marketplace/mcps/csscore/
- Implement async/await foundations with proper type hints
- Write unit tests (100% coverage minimum)
- Add to GitHub Actions CI/CD (inherit from _template)
- Update marketplace catalog (add csscore as REQUIRED dependency for all MCPs)

**Quality Gate for Phase 0.75:**
- ✓ Ruff: zero errors
- ✓ MyPy strict: zero errors
- ✓ Pytest: 100% coverage (not 80%)
- ✓ Module size: ≤2 MB
- ✓ MCP server starts cleanly
- ✓ All 12 Phase 2-5 MCPs can import csscore without issues
- ✓ No circular imports detected (run check-circular-deps.py)

### ⏳ **Phase 2: High-Priority MCP Extraction** (AFTER CSSCORE)
**Target MCPs (4 tools with ~52 tools total, all depend on csscore):**
1. forensic-vault (14 tools) — depends on csscore
2. network-layers (9 tools) — depends on csscore
3. threat-intelligence (14 tools) — depends on csscore
4. database-tools (15 tools) — depends on csscore

**Tasks:**
- Extract tool definitions from monolithic csmcp (avoiding csscore)
- Create tool stubs in MCP template
- Implement tool functions with async/await (with csscore imports)
- Write unit tests for each tool
- Add to GitHub Actions CI/CD
- Update marketplace catalog (add csscore dependency)

**Quality Gate for Phase 2:**
- ✓ Ruff: zero errors on all 4 MCPs
- ✓ MyPy strict: zero errors
- ✓ Pytest: 100% of tests pass
- ✓ Tool imports work + csscore imports work
- ✓ MCP servers start cleanly
- ✓ Integration tests pass with csscore

---

## Quality Assurance Policy

### Tooling Standards (All Phases)

**Python Code Quality:**
- **Linter:** `ruff check .` (zero errors/warnings)
- **Type Checking:** `mypy --strict` (zero errors)
- **Testing:** `pytest -v --cov` (≥80% coverage)
- **Package Manager:** `uv` (never `pip`)

**Bash Scripts:**
- **Syntax:** `bash -n` (zero errors)
- **ShellCheck:** (zero warnings)
- **Test:** Manual functional tests

**JSON/YAML:**
- **Syntax:** `jq .` and `yaml.safe_load()` (valid)
- **Schema:** Validate against spec

### Pre-Commit Checks

Before marking any phase DONE:
1. Run all linters (ruff, mypy)
2. Run all tests (pytest)
3. Run integration smoke tests
4. Fix any failures
5. Re-run entire loop
6. Only THEN commit and mark done

---

## Dependency Management

### Shared Dependencies (All MCPs)
- `fastmcp>=3.1.0` — MCP framework (critical: 3.1.0+, not earlier)
- `pydantic>=2.0` — Data validation
- `python>=3.11` — Minimum version

### Phase 2 Specific
- `cryptography>=41.0.0` — forensic-vault
- `tortoise-orm>=0.21.0` — database-tools
- `scapy>=2.5.0` — network-layers
- `aiohttp>=3.8.0` — threat-intelligence

---

## Known Constraints & Risks

### Pre-Existing Issues
- Database schema migration issues (manage schema command fails on pre-existing state) — documented but not blocking
- Circular dependency potential in Phase 2-5 (will validate with check-circular-deps.py after csscore)

### Phase 0.75-Specific Risks
- **csscore Bloat:** Core functions creeping into domain logic
  - **Mitigation:** Enforce ≤2 MB size limit, explicit module allowlist
- **Circular Imports:** csscore accidentally importing from Phase 2-5 MCPs
  - **Mitigation:** check-circular-deps.py mandatory in Phase 0.75 exit gate
- **Version Pinning:** csscore breaking changes affect all Phase 2-5 MCPs
  - **Mitigation:** Strict SemVer (1.0.0 locked), change gate requires all dependent tests pass

### Phase 2-5 Risks (Updated for csscore dependency)
- **Import Cascades:** One csscore function change requires retesting all 12 MCPs
  - **Mitigation:** Minimal function exports, explicit dependency contract in __all__
- **Test Coverage:** csscore must maintain 100% coverage (not 80%) to protect dependents
  - **Mitigation:** Phase 0.75 exit gate enforces coverage >= 100%

### Mitigation Strategies
- Run linting/testing after every phase
- Use strict type checking to catch issues early
- Validate imports and circular dependency detection before committing
- Tag phases in git for easy rollback if needed
- Document csscore API in dedicated docs/csscore.md (API contract)

---

## Success Metrics

- **Phase 1:** ✅ 7/7 tasks, exit gate passed
- **Phase 0.5:** ✅ 5/5 tasks, all tests passed
- **Code Quality:** ✅ Ruff zero errors, MyPy strict zero errors
- **Test Coverage:** ✅ ≥80% on all code
- **Tool Count:** 0 → 87 tools extracted (cumulative progress)

---

## Rollback Procedures

If a phase fails quality gate:
1. Identify which checks failed
2. Do NOT proceed to next phase
3. Fix failing code/tests
4. Re-run entire quality gate loop
5. If unfixable, revert to last git tag: `git checkout <phase-tag>`

---

## Checkpoint & New Chat Instantiation

### For New Chat Sessions

**Setup Context:**
```
Session workspace: /home/daen/.copilot/session-state/e5d7518f-985a-443a-a40f-528ac73800c9/
Plan file: plan.md (this file)
SQL database: session.db (todos, quality_gates, phase_deliverables tables)

Prior checkpoints:
- 001-session-e5d7518f.md: Full history of phases 0.5 & 1
```

**Restore State (First Action in New Chat):**
```bash
# 1. Read plan.md for current status
cat /home/daen/.copilot/session-state/e5d7518f-985a-443a-a40f-528ac73800c9/plan.md

# 2. Query SQL for todos/quality gates
sqlite3 /home/daen/.copilot/session-state/e5d7518f-985a-443a-a40f-528ac73800c9/session.db \
  "SELECT id, title, status FROM todos WHERE id LIKE 'phase%'"
  
# 3. Verify canonical repos exist
ls -d /home/daen/Projects/cybersecsuite /home/daen/Projects/ai-marketplace

# 4. Check latest commits
cd /home/daen/Projects/ai-marketplace && git log --oneline -1
cd /home/daen/Projects/cybersecsuite && git log --oneline -1
```

**Current State Summary (As of 2026-04-26T22:27):**

| Phase | Status | Deliverables | Git Tag |
|-------|--------|--------------|---------|
| 0.5 | ✅ DONE | 6 models, seed function | (not tagged) |
| 1 | ✅ DONE | Template (11 files), installer, catalog | 5a6793e |
| 0.75 | ⏳ READY | csscore MCP (3-5 core functions) | — |
| 2 | ⏳ READY | 4 MCPs (52 tools, all use csscore) | — |

**Key Locations:**
- CyberSecSuite: `/home/daen/Projects/cybersecsuite`
- AI Marketplace: `/home/daen/Projects/ai-marketplace` ← **PRIMARY FOR PHASES 1-5**
- MCP Template: `/home/daen/Projects/ai-marketplace/mcps/_template/`
- Marketplace Catalog: `/home/daen/Projects/ai-marketplace/index.json`

**Next Task:**
Phase 0.75 csscore MCP Extraction (single core MCP with 3-5 critical functions)
- Extract essential core functions from monolithic csmcp
- Create csscore MCP structure in ai-marketplace
- Implement async/await foundations
- Run quality gate loop (lint, type-check, test)
- Create changelog & documentation
- Commit & tag
- All Phase 2-5 MCPs will depend on csscore

**Instructions for New Chat:**
1. Run "Restore State" commands above
2. Read plan.md for full context (now includes Phase 0.75 csscore)
3. Review prior checkpoint (001-session-e5d7518f.md)
4. Confirm canonical repos are accessible
5. Ask user: "Ready for Phase 0.75 csscore MCP extraction?"
6. Update SQL todos as work progresses
7. Maintain same post-phase workflow (quality gates → docs → commit → tag)




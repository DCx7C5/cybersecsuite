# Scripts Reorganization Plan

**Date:** 2026-04-27  
**Status:** PLANNING  
**Goal:** Reorganize scripts into better logical paths aligned with project structure

---

## Current State Analysis

### Existing Scripts (5 files in `/scripts/`)

1. **install-mcp-core.sh** (11 KB)
   - Purpose: Bootstrap installer for 6 core MCPs
   - Type: Deployment/Infrastructure
   - Scope: Project-wide
   - Used: Phase 7, production deployment

2. **benchmark_tiers.py** (3.2 KB, incomplete docstring visible)
   - Purpose: Performance benchmark suite for model tiers
   - Type: Performance/Testing
   - Scope: LLM model evaluation
   - Metrics: Latency, throughput, memory, cost, error rates

3. **fix_skills.py** (2.1 KB)
   - Purpose: Skill file canonicalization/validation
   - Type: Data validation/migration
   - Scope: Skill metadata standardization
   - Verbs: 22 canonical action verbs (blue/red/neutral)

4. **worktree-session-manager.py** (~2 KB)
   - Purpose: Git worktree session management
   - Type: Development tooling
   - Scope: Multi-branch development workflow
   - Feature: Session persistence, cleanup

5. **gwt-aliases.sh** (0.5 KB)
   - Purpose: Shell aliases for git worktree
   - Type: Development tooling/Shell configuration
   - Scope: Developer convenience
   - Feature: Bash/Zsh aliases

6. **hooks/** (directory)
   - Purpose: Git hooks
   - Type: Development tooling
   - Current: Likely contains pre-commit, post-commit, etc.

---

## Proposed New Structure

### Option A: Category-Based Organization (Recommended)

```
cybersecsuite/
├── scripts/
│   ├── README.md                    ← Script index & usage guide
│   ├── .gitkeep
│   │
│   ├── dev/                         ← Development & workflow tools
│   │   ├── worktree-session-manager.py
│   │   ├── gwt-aliases.sh
│   │   └── hooks/                   ← Git hooks (moved here)
│   │
│   ├── deploy/                      ← Deployment & infrastructure
│   │   ├── install-mcp-core.sh
│   │   └── README.md
│   │
│   ├── test/                        ← Testing & benchmarking
│   │   ├── benchmark_tiers.py
│   │   └── README.md
│   │
│   └── data/                        ← Data processing & migration
│       ├── fix_skills.py
│       └── README.md
```

### Option B: Functional Grouping (Alternative)

```
scripts/
├── infrastructure/       (deployment, bootstrap, installation)
│   └── install-mcp-core.sh
├── development/         (dev workflow tools, git helpers)
│   ├── worktree-session-manager.py
│   ├── gwt-aliases.sh
│   └── hooks/
├── quality/             (testing, benchmarking, validation)
│   ├── benchmark_tiers.py
│   └── fix_skills.py
```

---

## Script Details & Recommendations

### 1. install-mcp-core.sh
- **Current:** `/scripts/install-mcp-core.sh`
- **Recommended:** `/scripts/deploy/install-mcp-core.sh`
- **Reason:** Deployment/infrastructure automation script
- **Alias:** Add `make deploy-mcp` or `scripts/deploy.sh` wrapper

### 2. benchmark_tiers.py
- **Current:** `/scripts/benchmark_tiers.py`
- **Recommended:** `/scripts/test/benchmark_tiers.py`
- **Reason:** Performance testing/benchmarking tool
- **CLI:** Add entry point in `pyproject.toml`: `csscore-benchmark`
- **Output:** Results should go to `reports/benchmarks/`

### 3. fix_skills.py
- **Current:** `/scripts/fix_skills.py`
- **Recommended:** `/scripts/data/fix_skills.py` (or `src/tools/migrate/`)
- **Reason:** Data validation/migration utility
- **Warning:** May be phase-specific (Phase 8) - consider deprecating if one-time use
- **Alternative:** Move to `src/tools/data/` if ongoing utility

### 4. worktree-session-manager.py
- **Current:** `/scripts/worktree-session-manager.py`
- **Recommended:** `/scripts/dev/worktree-session-manager.py`
- **Reason:** Developer workflow tooling
- **CLI:** Add entry point in `pyproject.toml`: `gwt-manager`
- **Config:** Consider moving config to `~/.config/css/` or `.css/worktree.yaml`

### 5. gwt-aliases.sh
- **Current:** `/scripts/gwt-aliases.sh`
- **Recommended:** `/scripts/dev/gwt-aliases.sh` or `dev/shell/aliases/`
- **Reason:** Developer convenience (shell aliases)
- **Installation:** Document sourcing in `README.md` and `.bashrc` setup
- **Alternative:** Could live in `~/.config/css/shell-aliases.sh`

### 6. hooks/
- **Current:** `/scripts/hooks/`
- **Recommended:** `/dev/hooks/` or `.githooks/` (Git standard)
- **Reason:** Standard Git hooks location
- **Config:** Add to `.git/config`: `core.hooksPath = dev/hooks`
- **Benefits:** Follows Git conventions, enables `git config --global core.hooksPath ~/.git-hooks`

---

## Implementation Steps

### Phase 1: Create Directory Structure
1. Create `/scripts/dev/`
2. Create `/scripts/deploy/`
3. Create `/scripts/test/`
4. Create `/scripts/data/`
5. Create `/dev/hooks/` (new top-level directory)

### Phase 2: Move Scripts
1. Move `install-mcp-core.sh` → `scripts/deploy/`
2. Move `benchmark_tiers.py` → `scripts/test/`
3. Move `fix_skills.py` → `scripts/data/`
4. Move `worktree-session-manager.py` → `scripts/dev/`
5. Move `gwt-aliases.sh` → `scripts/dev/`
6. Move `hooks/` → `dev/hooks/`

### Phase 3: Update Documentation
1. Create `/scripts/README.md` (script index)
2. Create `/scripts/dev/README.md` (dev tools guide)
3. Create `/scripts/deploy/README.md` (deployment guide)
4. Create `/scripts/test/README.md` (testing guide)
5. Create `/scripts/data/README.md` (data tools guide)
6. Create `/dev/hooks/README.md` (Git hooks setup)

### Phase 4: Update Configuration & References
1. Update `pyproject.toml` entry points:
   - `csscore-benchmark` → benchmark_tiers.py
   - `gwt-manager` → worktree-session-manager.py
2. Update `.github/workflows/*.yml` if they reference scripts
3. Update `Makefile` with new paths
4. Add `.git/config` hook path configuration
5. Update root `README.md` with script locations

### Phase 5: Testing & Verification
1. Verify all scripts still execute from new paths
2. Update CI/CD to use new script paths
3. Test Git hooks from new location
4. Verify shell aliases still work

### Phase 6: Git Cleanup & Commits
1. Git mv for each script to new location
2. Update `.gitignore` if needed
3. Commit with message: "refactor: reorganize scripts into functional categories"

---

## Estimated Effort

| Phase | Time | Notes |
|-------|------|-------|
| 1 | 5 min | Create directories |
| 2 | 10 min | Move files (git mv) |
| 3 | 30 min | Write documentation |
| 4 | 20 min | Update config & references |
| 5 | 15 min | Test execution paths |
| 6 | 10 min | Git commits |
| **Total** | **90 min** | ~1.5 hours |

---

## Benefits

✅ **Organization:** Clear categorization (dev, deploy, test, data)  
✅ **Discoverability:** Easy to find related scripts  
✅ **Scalability:** Room to add more scripts in each category  
✅ **Standards:** Follows Git conventions (hooks)  
✅ **Documentation:** Clear README in each category  
✅ **Automation:** CLI entry points for common tools  

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| References break | Update all paths in code/CI/docs |
| Git history lost | Use `git mv` (preserves history) |
| Confusion during transition | Comprehensive README documentation |
| Forgot a reference | Search codebase for old paths |

---

## Todos

- [ ] Create directory structure (Phase 1)
- [ ] Move scripts with git mv (Phase 2)
- [ ] Write category READMEs (Phase 3)
- [ ] Update configuration files (Phase 4)
- [ ] Test all scripts from new paths (Phase 5)
- [ ] Create git commits (Phase 6)
- [ ] Update main README.md
- [ ] Update CI/CD workflows (if needed)
- [ ] Update Makefile (if exists)
- [ ] Add CLI entry points to pyproject.toml

---

## Decision Required

**Proposed Structure:** Option A (Category-Based)  
**Rationale:** 
- Clearest organization
- Aligns with typical project layouts
- Easier to document and discover
- Scalable for future scripts

**Alternative:** Option B (Functional Grouping) if you prefer different naming

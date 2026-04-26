# Plan: Remove OpenSearch and Wazu References

**Date:** 2026-04-26  
**Status:** Planned  
**Scope Owner:** Backend Integration Layer

---

## 🎯 Objective

Remove all OpenSearch (search engine) and Wazu (likely monitoring/integration plugin) references from the codebase. These appear to be legacy integrations no longer required by the cybersecurity forensics suite.

---

## 📊 Current State Analysis

### References Found: 22 total
- **OpenSearch**: 22 references in Python + TS code
- **Wazu**: 0 references in source code (only in templates/skills directory)

### Files to Remove/Update:

**Backend (Python):**
1. `src/dashboard/api/openobserve_stats.py` — OpenSearch stats API endpoint
2. `src/dashboard/api/__init__.py` — OpenSearch import + export
3. `src/dashboard/routes.py` — OpenSearch route registration

**Frontend (TypeScript):**
1. `src/dashboard/static/ts/opensearch.ts` — OpenSearch module
2. `src/dashboard/static/ts/index.ts` — OpenSearch loader reference

**Configuration:**
1. `pyproject.toml` — Line 36: `"opensearch-py[async]>=2.7"` dependency

**Templates (Out of scope for now):**
1. `templates/skills/network/ids/wazuh/` — Wazu skill template
2. `templates/skills/soc/wazuh/` — Wazu skill template
3. Virtual environment packages (will be cleaned on reinstall)

---

## 📋 Execution Plan

### Phase 1: Code Analysis & Impact Assessment (30 min)

**Actions:**
1. Verify no active code (not test/template) depends on OpenSearch
2. Grep for all OpenSearch instantiation, config vars, environment setup
3. Check if OpenSearch is used in any API responses or middleware
4. Document any conditional logic around OpenSearch presence

**Exit Gate:**
- Confirm OpenSearch removal won't break active APIs
- No production code has runtime dependency on OpenSearch

**Commands:**
```bash
cd /home/daen/Projects/cybersecsuite

# Find all OpenSearch references
rg -n "opensearch|OpenSearch" src/ --type py --type ts --type tsx

# Check for env vars
rg -n "OPENSEARCH|openSearch" src/ .env.example

# Check imports
rg -n "from opensearch|import opensearch|from key_value.aio.stores.opensearch" src/
```

---

### Phase 2: Remove OpenSearch from Backend (30 min)

**Files to Delete:**
```
src/dashboard/api/openobserve_stats.py
src/dashboard/static/ts/opensearch.ts
```

**Files to Edit:**
```
src/dashboard/api/__init__.py
  - Remove: from dashboard.api.openobserve_stats import api_opensearch
  - Remove: api_opensearch from __all__ export

src/dashboard/routes.py
  - Remove: api_opensearch import
  - Remove: Route("/api/opensearch", api_opensearch, methods=["GET"])
```

**Dependency to Remove:**
```
pyproject.toml
  - Remove: "opensearch-py[async]>=2.7" (line 36)
  - Remove: "key_value" if only used for OpenSearch store (verify first)
```

**Exit Gate:**
- All OpenSearch imports/references removed from backend
- pyproject.toml has no opensearch dependencies
- No broken imports remain

**Validation:**
```bash
rg "opensearch|OpenSearch" src/dashboard/api/ src/dashboard/routes.py
# Should return 0 results
```

---

### Phase 3: Remove OpenSearch from Frontend (20 min)

**Files to Edit:**
```
src/dashboard/static/ts/index.ts
  - Remove: import { loadOpenSearch } from './opensearch.js';
  - Remove: loadOpenSearch function call
  - Remove: loadOpenSearch from window.api type definition
```

**Exit Gate:**
- No TypeScript file imports opensearch module
- Frontend builds without OpenSearch references

**Validation:**
```bash
rg "opensearch" src/dashboard/static/
# Should return 0 results
```

---

### Phase 4: Clean Dependencies & Rebuild (45 min)

**Actions:**
1. Remove dependency from pyproject.toml
2. Clean install Python dependencies:
   ```bash
   rm -rf src/frontend/node_modules src/frontend/package-lock.json
   cd src/frontend && npm cache clean --force && npm install
   
   cd /home/daen/Projects/cybersecsuite
   rm -rf .venv/lib/python*/site-packages/opensearch*
   uv sync  # Reinstall without opensearch-py
   ```
3. Rebuild frontend to verify no OpenSearch references
4. Run backend tests to verify no OpenSearch API calls

**Exit Gate:**
- Frontend builds cleanly
- Backend tests pass
- No OpenSearch traces in output

**Validation:**
```bash
cd src/frontend && npm run build
pytest tests/test_dashboard_routing.py -v
```

---

### Phase 5: Test & Validation (20 min)

**Python Tests:**
```bash
# Verify dashboard routing works without OpenSearch
pytest tests/test_dashboard_routing.py -v

# Full backend test suite
pytest tests/ -v

# Check no opensearch in imports
python -c "import sys; [print(p) for p in sys.path if 'opensearch' in p.lower()]"
```

**Frontend Tests:**
```bash
cd src/frontend
npm run type-check
npm run test
npm run build
```

**Exit Gate:**
- ✅ All tests pass
- ✅ No OpenSearch references in code
- ✅ No OpenSearch packages installed

---

## 🔗 Wazu References (Templates - Optional)

**Current State:**
- `templates/skills/network/ids/wazuh/` — Wazu IDS skill
- `templates/skills/soc/wazuh/` — Wazu SOC skill

**Decision:**
- **Keep templates**: These are skill definitions, not active code
- **If removing**: Delete both directories, update docs if templates are referenced in README

**Action (if removing):**
```bash
rm -rf templates/skills/network/ids/wazuh/
rm -rf templates/skills/soc/wazuh/
```

---

## ⚠️ Potential Issues & Mitigations

| Issue | Likelihood | Mitigation |
|-------|-----------|-----------|
| OpenSearch used in hidden import chain | LOW | Run `pytest` after removal; check test output |
| Environment config expects OPENSEARCH vars | LOW | Check `.env.example` and startup logs |
| API client code references old endpoint | LOW | Search `/api/opensearch` usage in frontend |
| Dependency tree issue (opensearch-py pulls other deps) | MEDIUM | Check `uv tree` output; may need to keep other deps |

---

## 📈 Effort & Timeline

| Phase | Task | Time | Notes |
|-------|------|------|-------|
| 1 | Analysis | 30 min | Verify no production dependency |
| 2 | Backend removal | 30 min | Delete 1 file, edit 2 files, remove dependency |
| 3 | Frontend cleanup | 20 min | Edit 1 file |
| 4 | Rebuild & clean | 45 min | Includes dependency reinstall time |
| 5 | Testing & validation | 20 min | Run full test suite |
| **TOTAL** | **OpenSearch Removal** | **~2.5 hours** | Can run in parallel with Phase 5E |

---

## ✅ Success Criteria

- ✅ No `opensearch` or `OpenSearch` strings in `/src` (except comments/docs)
- ✅ `pyproject.toml` has no `opensearch-py` dependency
- ✅ Frontend builds without errors
- ✅ Backend tests all pass
- ✅ `npm run build` succeeds in frontend
- ✅ No hidden import chains to opensearch packages
- ✅ Dashboard functionality unchanged (no API breakage)

---

## 🚀 Recommended Approach

**This work can run PARALLEL with Phase 5E TypeScript fixes!**

1. **Immediately:** Start Phase 1 (analysis) — verify no production dependency
2. **If safe:** Execute Phases 2-5 while Phase 5E TypeScript fixes run
3. **Validation:** Run full test suite before merging

**Rationale:**
- OpenSearch removal is independent of Phase 5E work
- No shared files between OpenSearch removal and Phase 5E components
- Frees up 2-3 hours by running in parallel

---

## 📝 Rollback Plan

If issues arise post-removal:

1. Keep git working tree clean before starting Phase 2
2. If tests fail: `git checkout src/dashboard/api/` and `git checkout pyproject.toml`
3. Reinstall: `uv sync && npm install`
4. Re-run tests to confirm rollback

```bash
git diff src/dashboard/api/openobserve_stats.py  # Document before delete
git checkout pyproject.toml  # Revert dependency removal
uv sync  # Reinstall opensearch-py
```

---

## 📊 Impact Assessment

| Component | Impact | Risk |
|-----------|--------|------|
| Backend API | Removes `/api/opensearch` endpoint | LOW (not used in Phase 5E) |
| Frontend | Removes opensearch.ts module + references | LOW (legacy dashboard) |
| Dependencies | Reduces install size by ~5MB | NONE (improvement) |
| Tests | May need to update test mocks | LOW (1-2 files) |

---

## 🎯 Next Steps

1. ✅ Add to master plan.md
2. ⏳ Execute Phase 1 (analysis) immediately
3. ⏳ If safe: Execute Phases 2-5 in parallel with Phase 5E fixes
4. ⏳ Final validation before merge

# Execution Checklist: Jinja2 Removal

Use this checklist to track progress. Check off each item as you complete it.

---

## Phase 1: Audit

- [ ] **audit-jinja2-templates**
  - [ ] Search for all .jinja2/.j2 template files
  - [ ] Document Jinja2 features used (loops, filters, conditions)
  - [ ] Assess complexity (simple = OK for str.format, complex = needs special handling)
  - [ ] Update status: `UPDATE todos SET status = 'done' WHERE id = 'audit-jinja2-templates'`
  - **Estimated:** 30-60 min

---

## Phase 2: Refactor (Can be parallelized)

**Prerequisite:** audit-jinja2-templates = done

### Module 1: crypto/template_renderer.py
- [ ] **refactor-artifact-renderer**
  - [ ] Open file: `src/crypto/template_renderer.py`
  - [ ] Remove: `from template_engine import render_string`
  - [ ] Replace: `render_string(template, ctx)` → `template.format(**ctx)`
  - [ ] Handle any KeyError exceptions gracefully
  - [ ] Run artifact generation tests
  - [ ] Verify output matches pre-removal behavior
  - [ ] Update status: `UPDATE todos SET status = 'done' WHERE id = 'refactor-artifact-renderer'`
  - **Estimated:** 30 min

### Module 2: csmcp/cybersec/template.py
- [ ] **refactor-mcp-template-tool**
  - [ ] Open file: `src/csmcp/cybersec/template.py`
  - [ ] Remove: `from template_engine import render`
  - [ ] Add: Direct file loading (Path + read_text)
  - [ ] Replace: `render(name, vars)` → `template.format(**vars)`
  - [ ] Add error handling for missing templates
  - [ ] Test MCP tool with sample templates
  - [ ] Update status: `UPDATE todos SET status = 'done' WHERE id = 'refactor-mcp-template-tool'`
  - **Estimated:** 45 min

### Module 3: csmcp/cybersec/skill_manager.py
- [ ] **refactor-skill-discovery**
  - [ ] Open file: `src/csmcp/cybersec/skill_manager.py`
  - [ ] Remove: `from template_engine.discovery import discover_skills`
  - [ ] **Choose approach:**
    - [ ] Option A: Create `skills/registry.py` with REGISTERED_SKILLS dict
    - [ ] Option B: Add static filesystem scan in __init__
  - [ ] Update `__init__()` to use new approach (3 locations)
  - [ ] Test skill loading
  - [ ] Verify all skills still available
  - [ ] Update status: `UPDATE todos SET status = 'done' WHERE id = 'refactor-skill-discovery'`
  - **Estimated:** 1 hour

### Module 4: hooks/sdk_hooks.py
- [ ] **refactor-hook-context**
  - [ ] Open file: `src/hooks/sdk_hooks.py`
  - [ ] Remove: `from template_engine.context import get_context`
  - [ ] Replace: `get_context()` → `GlobalContext()` (direct instantiation)
  - [ ] Verify context module exists (or create if needed)
  - [ ] Test hook setup
  - [ ] Update status: `UPDATE todos SET status = 'done' WHERE id = 'refactor-hook-context'`
  - **Estimated:** 20 min

### Module 5: cybersecsuite/sdk.py
- [ ] **refactor-sdk-render**
  - [ ] Open file: `src/cybersecsuite/sdk.py`
  - [ ] Remove: `from template_engine.renderer import render as _render, render_string as _render_string`
  - [ ] Replace: `_render()` and `_render_string()` with local implementations
  - [ ] Use `str.format()` as backend
  - [ ] Keep function signatures identical (backward compatibility)
  - [ ] Add template file loading logic to `render()`
  - [ ] Test SDK render functions
  - [ ] Update status: `UPDATE todos SET status = 'done' WHERE id = 'refactor-sdk-render'`
  - **Estimated:** 30 min

### Module 6: cybersecsuite/_context.py
- [ ] **refactor-context-wrapper**
  - [ ] Open file: `src/cybersecsuite/_context.py`
  - [ ] Remove: `from template_engine.context import ...`
  - [ ] **Choose approach:**
    - [ ] Option A: Delete _context.py, update all imports
    - [ ] Option B: Keep as thin wrapper to new context module
  - [ ] Update all imports if removing
  - [ ] Test context resolution
  - [ ] Update status: `UPDATE todos SET status = 'done' WHERE id = 'refactor-context-wrapper'`
  - **Estimated:** 20 min

**Checkpoint:** All 6 refactors complete before moving to Phase 3

---

## Phase 3: Remove

**Prerequisite:** All 6 refactors = done

### Step 1: Remove from pyproject.toml
- [ ] **remove-jinja2-pyproject**
  - [ ] Edit: `pyproject.toml`
  - [ ] Find line: `"jinja2>=3.1",`
  - [ ] Delete it
  - [ ] Run: `uv lock` (to update uv.lock)
  - [ ] Verify: `grep -i jinja2 pyproject.toml` returns nothing
  - [ ] Update status: `UPDATE todos SET status = 'done' WHERE id = 'remove-jinja2-pyproject'`
  - **Estimated:** 5 min

### Step 2: Delete template_engine module
- [ ] **delete-template-engine-module**
  - [ ] Run: `rm -rf src/template_engine/`
  - [ ] Verify: `ls -la src/template_engine/` fails (file not found)
  - [ ] Update status: `UPDATE todos SET status = 'done' WHERE id = 'delete-template-engine-module'`
  - **Estimated:** 2 min

### Step 3: Clean up any remaining imports
- [ ] **clean-import-statements**
  - [ ] Search: `grep -r "from template_engine\|import template_engine\|import jinja2\|from jinja2" src/ --include="*.py"`
  - [ ] If found: update/delete each reference
  - [ ] Re-search to verify clean
  - [ ] Update status: `UPDATE todos SET status = 'done' WHERE id = 'clean-import-statements'`
  - **Estimated:** 15 min

---

## Phase 4: Validate

**Prerequisite:** All removal steps = done

### Step 1: Test imports
- [ ] **test-no-import-errors**
  - [ ] Test SDK imports: `python -c "from src.cybersecsuite.sdk import render, render_string"`
  - [ ] Test artifact renderer: `python -c "from src.crypto.template_renderer import ArtifactTemplateRenderer"`
  - [ ] Test MCP template: `python -c "from src.csmcp.cybersec.template import render_template"`
  - [ ] Test skill manager: `python -c "from src.csmcp.cybersec.skill_manager import SkillManager"`
  - [ ] Test hooks: `python -c "from src.hooks.sdk_hooks import setup_hooks"`
  - [ ] Run test suite: `pytest tests/test_sdk.py -v`
  - [ ] Verify no ImportError, no jinja2/template_engine references
  - [ ] Update status: `UPDATE todos SET status = 'done' WHERE id = 'test-no-import-errors'`
  - **Estimated:** 30 min

### Step 2: Integration tests
- [ ] **integration-tests-render**
  - [ ] Test artifact rendering works
  - [ ] Test MCP template tool works
  - [ ] Test skill discovery works
  - [ ] Test hook context works
  - [ ] Test SDK render functions work
  - [ ] Run: `pytest tests/ -v -k "render or template or skill or context"`
  - [ ] All tests should pass
  - [ ] Update status: `UPDATE todos SET status = 'done' WHERE id = 'integration-tests-render'`
  - **Estimated:** 1 hour

---

## Final Verification

- [ ] All 12 todos marked 'done'
- [ ] No jinja2 in pyproject.toml
- [ ] template_engine/ directory deleted
- [ ] No remaining jinja2/template_engine imports
- [ ] All tests pass
- [ ] No ImportError on startup
- [ ] All modules functional

---

## Git Commits

Suggested commits:

```bash
# After Phase 2
git add src/crypto src/csmcp src/hooks src/cybersecsuite
git commit -m "refactor: Replace Jinja2 with str.format() in 6 modules

- crypto/template_renderer.py: use template.format()
- csmcp/cybersec/template.py: direct file loading + str.format()
- csmcp/cybersec/skill_manager.py: config-based skill registration
- hooks/sdk_hooks.py: direct GlobalContext instantiation
- cybersecsuite/sdk.py: str.format() backend
- cybersecsuite/_context.py: direct import or thin wrapper"

# After Phase 3
git add pyproject.toml uv.lock
git rm -r src/template_engine/
git commit -m "chore: Remove jinja2 dependency and template_engine module

- Remove jinja2>=3.1 from pyproject.toml
- Delete src/template_engine/ directory
- Update uv.lock"

# After Phase 4
git add tests/
git commit -m "test: Add post-removal validation tests

- Verify no ImportError on startup
- Test artifact rendering, MCP tools, skill discovery, SDK render
- Verify all modules functional post-removal"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| KeyError in str.format() | Add default values: `template.format_map({**ctx, 'missing_key': ''})` |
| Template file not found | Check path; use absolute or relative from correct dir |
| ImportError after deletion | Search for remaining imports; verify all refactors complete |
| Skill discovery fails | Verify REGISTERED_SKILLS dict populated or filesystem scan working |
| Tests fail | Run individual tests to isolate; check test setup |

---

## Status Summary

**Starting State:** 12 todos pending  
**Target:** 12 todos done  

Track progress:
```bash
# Check current status
sqlite3 ~/.copilot/session-state/e352def5-2e3c-46e8-bc54-d29b0148518d/session.db \
  "SELECT id, status FROM todos ORDER BY id;"
```

---

## Timeline

| Phase | Todos | Est. Time |
|-------|-------|-----------|
| Audit | 1 | 0.5-1 hr |
| Refactor | 6 | 2-3 hrs |
| Remove | 3 | 0.5 hr |
| Validate | 2 | 1-1.5 hrs |
| **Total** | **12** | **4-8 hrs** |

---

**Let's go! 🚀**

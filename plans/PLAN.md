# Jinja2 Removal Plan: Complete Implementation Guide

## Overview

This document is the **definitive implementation guide** for removing Jinja2 and template_engine from CyberSecSuite.

**Scope:** 6 affected modules, 12 todos, 4 phases  
**Effort:** 4-8 hours  
**Risk:** Medium (straightforward refactoring, well-scoped)  
**Drop & Reinit:** Yes (database can be reset)

---

## Why Remove Jinja2?

- **Heavy dependency** — Jinja2 is a full templating engine; overkill for CyberSecSuite use cases
- **Minimal usage** — Only 6 modules use it; mostly for simple variable substitution
- **Cleaner codebase** — Removing it simplifies dependencies and reduces attack surface
- **Lightweight alternative** — Python's str.format() / f-strings sufficient for current needs

---

## Phase 1: Audit (1 todo)

### Todo: audit-jinja2-templates

**Objective:** Understand what templates exist and how complex they are.

**Steps:**
```bash
# Find all template files
find /home/daen/Projects/cybersecsuite -name "*.jinja2" -o -name "*.j2" -o -name "*.jinja"

# Search for template usage in code
grep -r "\.render\|render_string\|template\|jinja" src/ --include="*.py" | grep -i jinja

# Check template_engine imports
grep -r "from template_engine\|import.*template_engine" src/ --include="*.py"
```

**Output:** Document any complex Jinja2 features:
- Loops (`{% for %}`)
- Conditionals (`{% if %}`)
- Filters (`{{ var|upper }}`)
- Template inheritance
- Custom tags

**Outcome:** Determine if simple str.format() is sufficient or if special handling needed.

**Estimated Time:** 30-60 minutes

---

## Phase 2: Refactor (6 todos)

These 6 todos can be done in **parallel** (no dependencies between them, only dependency is audit).

### Todo 1: refactor-artifact-renderer

**File:** `src/crypto/template_renderer.py`

**Current Implementation:**
```python
from template_engine import render_string

class ArtifactTemplateRenderer:
    def render(self, name, content, signature, **render_kwargs):
        template = ...
        rendered = render_string(self.template, ctx)
        return rendered
```

**Refactored Implementation:**
```python
# No more template_engine import

class ArtifactTemplateRenderer:
    def render(self, name, content, signature, **render_kwargs):
        template = ...
        # Use str.format() instead of render_string()
        rendered = template.format(**ctx)
        return rendered
```

**Key Changes:**
- Delete `from template_engine import render_string`
- Replace `render_string(template, ctx)` with `template.format(**ctx)`
- Handle missing keys gracefully (catch KeyError if needed)

**Testing:**
- Run existing artifact generation tests
- Verify rendered output is identical to before

**Estimated Time:** 30 minutes

---

### Todo 2: refactor-mcp-template-tool

**File:** `src/csmcp/cybersec/template.py`

**Current Implementation:**
```python
async def render_template(args):
    name = args["name"]
    extra_vars = args.get("extra_vars", {})
    
    from template_engine import render
    rendered = render(name, extra_vars)  # Uses Jinja2 discovery
    
    return sdk_result({"name": name, "rendered": rendered})
```

**Refactored Implementation:**
```python
async def render_template(args):
    name = args["name"]
    extra_vars = args.get("extra_vars", {})
    
    # Direct file load instead of template_engine discovery
    from pathlib import Path
    template_path = Path(f"./templates/{name}.txt")  # or .j2 → .txt
    
    if not template_path.exists():
        return sdk_result({"error": f"Template '{name}' not found"})
    
    template = template_path.read_text()
    rendered = template.format(**extra_vars)
    
    return sdk_result({"name": name, "rendered": rendered})
```

**Key Changes:**
- Delete `from template_engine import render`
- Load template as plain text file instead of using discovery
- Use str.format() for rendering
- Handle missing template gracefully

**Notes:**
- Templates may need renaming from `.j2` → `.txt`
- Or keep `.j2` extension; doesn't matter for str.format()

**Testing:**
- Test MCP tool with sample templates
- Verify error handling for missing templates

**Estimated Time:** 45 minutes

---

### Todo 3: refactor-skill-discovery

**File:** `src/csmcp/cybersec/skill_manager.py`

**Current Implementation:**
```python
from template_engine.discovery import discover_skills

class SkillManager:
    def __init__(self):
        self.skills = discover_skills()  # Searches templates dynamically
```

**Refactored Implementation (Option A: Config-Based):**
```python
# Create a static registry instead of dynamic discovery

# skills/registry.py
REGISTERED_SKILLS = {
    "skill_1": SkillClass1,
    "skill_2": SkillClass2,
    # ... all skills
}

# skill_manager.py
class SkillManager:
    def __init__(self):
        from csmcp.skills.registry import REGISTERED_SKILLS
        self.skills = REGISTERED_SKILLS
```

**Refactored Implementation (Option B: Filesystem Scan):**
```python
from pathlib import Path
import importlib

class SkillManager:
    def __init__(self):
        self.skills = self._discover_skills_static()
    
    def _discover_skills_static(self):
        skill_dir = Path("./src/csmcp/skills")
        skills = {}
        for skill_file in skill_dir.glob("*.py"):
            if skill_file.name.startswith("_"):
                continue
            module_name = skill_file.stem
            module = importlib.import_module(f"csmcp.skills.{module_name}")
            if hasattr(module, "SKILL_CLASS"):
                skills[module_name] = module.SKILL_CLASS
        return skills
```

**Key Changes:**
- Delete `from template_engine.discovery import discover_skills`
- Replace with config-based (REGISTERED_SKILLS) or simple filesystem scan
- Remove template discovery logic

**Notes:**
- Config-based is simpler and faster (no runtime filesystem scan)
- Filesystem scan is more flexible (auto-detect new skills)
- **Recommendation:** Use config-based for simplicity

**Testing:**
- Verify all skills still load
- Test skill registration
- Check no skills are lost

**Estimated Time:** 1 hour

---

### Todo 4: refactor-hook-context

**File:** `src/hooks/sdk_hooks.py`

**Current Implementation:**
```python
def setup_hooks(self):
    from template_engine.context import get_context
    self.ctx = get_context()  # Factory function
```

**Refactored Implementation:**
```python
def setup_hooks(self):
    from cybersecsuite.context import GlobalContext  # Direct import
    self.ctx = GlobalContext()  # Direct instantiation
```

**Key Changes:**
- Delete `from template_engine.context import get_context`
- Replace with direct `GlobalContext()` instantiation
- May need to create `cybersecsuite/context.py` if it doesn't exist

**Testing:**
- Verify hook setup still works
- Check context is correctly initialized

**Estimated Time:** 20 minutes

---

### Todo 5: refactor-sdk-render

**File:** `src/cybersecsuite/sdk.py`

**Current Implementation:**
```python
from template_engine.renderer import render as _render, render_string as _render_string

def render(name, vars):
    return _render(name, vars)

def render_string(template, vars):
    return _render_string(template, vars)

# Public SDK API
sdk.render = render
sdk.render_string = render_string
```

**Refactored Implementation:**
```python
# No more template_engine imports

def render(name, vars):
    """Load template file and render with vars. (Deprecated API)"""
    from pathlib import Path
    template_path = Path(f"./templates/{name}.txt")
    if not template_path.exists():
        raise FileNotFoundError(f"Template '{name}' not found")
    template = template_path.read_text()
    return template.format(**vars)

def render_string(template, vars):
    """Render template string with vars."""
    return template.format(**vars)

# Public SDK API (unchanged for backward compatibility)
sdk.render = render
sdk.render_string = render_string
```

**Key Changes:**
- Delete imports from template_engine
- Keep function signatures **unchanged** (backward compatibility)
- Use str.format() as backend
- Handle template loading manually

**Testing:**
- All SDK tests must pass
- Verify render_string() works with existing templates
- Check backward compatibility

**Estimated Time:** 30 minutes

---

### Todo 6: refactor-context-wrapper

**File:** `src/cybersecsuite/_context.py`

**Current Implementation:**
```python
"""Thin context wrapper — avoids circular imports."""
from template_engine.context import get_context as _get_context

def get_context(...):
    return _get_context(...)
```

**Refactored Implementation (Option A: Remove Wrapper):**
```python
# Delete _context.py entirely
# Update imports: from cybersecsuite._context import get_context
#              → from cybersecsuite.context import get_context
```

**Refactored Implementation (Option B: Keep Thin Wrapper):**
```python
"""Thin context wrapper — avoids circular imports."""
from cybersecsuite.context import GlobalContext

def get_context(...):
    """Get current execution context."""
    return GlobalContext(...)
```

**Key Changes:**
- Delete import from template_engine.context
- Either remove _context.py entirely OR keep as thin wrapper
- Update all imports if removing

**Recommendation:** **Remove _context.py** if it's pure routing. **Keep** if it handles complex logic.

**Testing:**
- Verify no circular import issues
- Test context resolution in all modules

**Estimated Time:** 20 minutes

---

## Phase 3: Remove (3 todos)

### Todo 7: remove-jinja2-pyproject

**File:** `pyproject.toml`

**Current:**
```toml
dependencies = [
    "jinja2>=3.1",
    # ... other deps
]
```

**After:**
```toml
dependencies = [
    # jinja2 removed
    # ... other deps
]
```

**Steps:**
```bash
cd /home/daen/Projects/cybersecsuite
# Edit pyproject.toml: remove jinja2>=3.1 line
# Update lock file
uv lock
```

**Verification:**
```bash
# Verify jinja2 removed from dependencies
grep -i jinja2 pyproject.toml  # Should find nothing
```

**Estimated Time:** 5 minutes

---

### Todo 8: delete-template-engine-module

**Directory:** `src/template_engine/`

**Files to Delete:**
- `src/template_engine/__init__.py`
- `src/template_engine/renderer.py`
- `src/template_engine/context.py`
- `src/template_engine/discovery.py`
- `src/template_engine/session_scope.py` (if exists)

**Steps:**
```bash
rm -rf /home/daen/Projects/cybersecsuite/src/template_engine/
```

**Verification:**
```bash
# Verify directory gone
ls -la /home/daen/Projects/cybersecsuite/src/template_engine/  # Should fail
```

**Estimated Time:** 2 minutes

---

### Todo 9: clean-import-statements

**Objective:** Verify NO remaining imports of template_engine or jinja2.

**Search:**
```bash
grep -r "from template_engine\|import template_engine\|import jinja2\|from jinja2" \
  /home/daen/Projects/cybersecsuite/src/ \
  --include="*.py"
```

**Expected Output:** Nothing (empty)

**If Anything Found:**
- Check each reference
- Update imports or delete code as needed
- Re-search to verify clean

**Estimated Time:** 15 minutes

---

## Phase 4: Validate (2 todos)

### Todo 10: test-no-import-errors

**Objective:** Verify app starts without ImportError.

**Test Script:**
```bash
cd /home/daen/Projects/cybersecsuite

# Test 1: Import main modules
python -c "from src.cybersecsuite.sdk import render, render_string; print('✓ SDK imports OK')"
python -c "from src.crypto.template_renderer import ArtifactTemplateRenderer; print('✓ Artifact renderer OK')"
python -c "from src.csmcp.cybersec.template import render_template; print('✓ MCP template OK')"
python -c "from src.csmcp.cybersec.skill_manager import SkillManager; print('✓ Skill manager OK')"
python -c "from src.hooks.sdk_hooks import setup_hooks; print('✓ SDK hooks OK')"

# Test 2: Full app startup
python -m pytest tests/test_sdk.py -v

# Test 3: Search for remaining imports
grep -r "template_engine\|jinja2" src/ --include="*.py" || echo "✓ No remaining imports"
```

**Expected Output:**
```
✓ SDK imports OK
✓ Artifact renderer OK
✓ MCP template OK
✓ Skill manager OK
✓ SDK hooks OK
✓ All tests passed
✓ No remaining imports
```

**Estimated Time:** 30 minutes

---

### Todo 11: integration-tests-render

**Objective:** Verify all rendering, discovery, and context functions work post-removal.

**Test Cases:**

1. **Artifact Rendering:**
   ```python
   from src.crypto.template_renderer import ArtifactTemplateRenderer
   renderer = ArtifactTemplateRenderer()
   result = renderer.render("test_artifact", "{name}", "sig", name="TestCase")
   assert "TestCase" in result
   ```

2. **MCP Template Tool:**
   ```python
   from src.csmcp.cybersec.template import render_template
   result = await render_template({"name": "test", "extra_vars": {"var": "value"}})
   assert "value" in result["rendered"]
   ```

3. **Skill Discovery:**
   ```python
   from src.csmcp.cybersec.skill_manager import SkillManager
   manager = SkillManager()
   assert len(manager.skills) > 0
   ```

4. **Hook Context:**
   ```python
   from src.hooks.sdk_hooks import setup_hooks
   hooks = setup_hooks()
   assert hooks.ctx is not None
   ```

5. **SDK Render:**
   ```python
   from src.cybersecsuite.sdk import render_string
   result = render_string("Hello {name}", {"name": "World"})
   assert result == "Hello World"
   ```

**Run All Tests:**
```bash
pytest tests/ -v -k "render or template or skill or context"
```

**Expected:** All tests pass, no errors.

**Estimated Time:** 1 hour

---

## Dependency Graph

```
audit-jinja2-templates (1 todo)
    ↓
    ├→ refactor-artifact-renderer
    ├→ refactor-mcp-template-tool
    ├→ refactor-skill-discovery
    ├→ refactor-hook-context
    ├→ refactor-sdk-render
    └→ refactor-context-wrapper
         ↓
         remove-jinja2-pyproject (all 6 must complete first)
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

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Templates use complex Jinja2 features | Audit in Phase 1; propose alternative if needed |
| Breaking SDK API | Keep render/render_string signatures identical |
| Skill discovery breaks | Test skill loading extensively |
| Circular imports | Test imports early; avoid mutual dependencies |
| Missing test coverage | Write tests for each refactored module |

---

## Rollback Plan

If something breaks:
1. **Git revert** last commit(s)
2. **Reset pyproject.toml** — re-add jinja2>=3.1
3. **Restore template_engine/** — from git history
4. **Run tests** — verify rollback successful

---

## Success Criteria

✅ All 12 todos completed and marked 'done'  
✅ jinja2 removed from pyproject.toml + uv lock updated  
✅ src/template_engine/ directory deleted  
✅ 0 remaining imports of jinja2 or template_engine  
✅ All existing tests pass  
✅ No ImportError on app startup  
✅ Artifact rendering works  
✅ MCP tools work  
✅ Skill discovery works  
✅ Hook context works  
✅ SDK render functions work  

---

## Git Commits

Suggested commit structure:
```
1. Refactor artifact renderer (#xyz)
2. Refactor MCP template tool (#xyz)
3. Refactor skill discovery (#xyz)
4. Refactor hook context (#xyz)
5. Refactor SDK render functions (#xyz)
6. Refactor context wrapper (#xyz)
7. Remove jinja2 dependency (#xyz)
8. Delete template_engine module (#xyz)
9. Clean up remaining imports (#xyz)
10. Add removal validation tests (#xyz)
```

Or one big commit:
```
chore: Remove jinja2 and template_engine module

- Refactor artifact rendering to use str.format()
- Replace MCP template tool with direct file loading
- Replace skill discovery with config-based registration
- Replace hook context with direct class instantiation
- Update SDK render functions to use str.format() backend
- Remove template_engine wrapper module
- Remove jinja2 from pyproject.toml
- Add validation tests for post-removal functionality
```

---

**Total Estimated Time: 4-8 hours**  
**Recommended Timeline: 1-2 sessions**  
**Difficulty: Medium**

Good luck! 🚀

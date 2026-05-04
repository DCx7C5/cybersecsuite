# Marketplace Cleanup: Steps 1-3

**Scope**: Clean up marketplace module types + base (audit → flatten → delete)  
**Status**: 📋 Plan  
**Updated**: 2026-05-04T10:14

---

## Step 1: Audit Current Usage (30 min)

### 1.1 Find all imports of marketplace/types.py

```bash
cd /home/daen/Projects/cybersecsuite

# Find files importing from marketplace.types
grep -r "from.*marketplace.*types import\|from css.modules.marketplace.types import" --include="*.py" src/

# Find files importing from marketplace.base
grep -r "from.*marketplace.*base import\|from css.modules.marketplace.base import" --include="*.py" src/
```

### 1.2 Check endpoints.py usage

```bash
# What's actually used in endpoints?
cat src/css/modules/marketplace/endpoints.py | grep -E "^from|^import|class |def " | head -30
```

### 1.3 Check __init__.py exports

```bash
cat src/css/modules/marketplace/__init__.py
```

### 1.4 Document findings

**Current imports tracking**:
- [ ] endpoints.py: uses `InstallRequest`, `ToggleRequest`, etc. (list all)
- [ ] __init__.py: re-exports (list what's exported)
- [ ] seeder.py: imports? (check)
- [ ] installer.py: imports? (check)
- [ ] registry.py: imports? (check)
- [ ] Any other files in marketplace/ import types.py? (check)

### 1.5 Result document

Create brief summary:
```
MARKETPLACE AUDIT RESULTS (2026-05-04)

Files importing marketplace/types.py:
- endpoints.py: InstallRequest, InstallResponse, ToggleRequest, ToggleResponse, ...
- __init__.py: re-exports (9 types)

Files importing marketplace/base.py:
- NONE (unused)

Inheritance in types.py:
- MarketplaceBase (shared Config)
  ├── MarketplaceMetaBase (extends with metadata fields)
  │   └── MarketplaceMetaResponse (adds id, status)
  └── MarketplaceItemBase (extends with item fields)
      ├── MarketplaceItemCreate (adds source_url)
      ├── MarketplaceItemUpdate (all optional)
      └── MarketplaceItemResponse (adds provider, chksum)

Cleanup action:
- Delete marketplace/base.py (confirmed zero imports)
- Flatten types.py to 5 explicit classes (no inheritance)
```

---

## Step 2: Flatten marketplace/types.py (1 hour)

### 2.1 Backup current file

```bash
cp src/css/modules/marketplace/types.py src/css/modules/marketplace/types.py.bak
```

### 2.2 Rewrite types.py

**Keep imports**:
```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .enums import MarketplaceItemType, MarketplaceItemStatus
```

**Remove**:
- ❌ `MarketplaceBase` (just use BaseModel)
- ❌ `MarketplaceMetaBase` (merge into Response)
- ❌ `MarketplaceItemBase` (split into List + Detail responses)
- ❌ `MarketplaceItemCreate` (use InstallRequest instead)
- ❌ `MarketplaceItemUpdate` (not used by API)

**Create new classes** (in order):

```python
# ── Marketplace Status ────────────────────────────────────────────

class MarketplaceMetaResponse(BaseModel):
    """Marketplace status response."""
    id: int
    name: str
    version: str
    update_available: bool
    last_index_check: Optional[datetime] = None


# ── Item List/Detail ──────────────────────────────────────────────

class ItemListResponse(BaseModel):
    """Item summary for list endpoints."""
    id: str
    name: str
    kind: MarketplaceItemType
    version: str
    installed: bool


class ItemDetailResponse(BaseModel):
    """Full item details."""
    id: str
    name: str
    description: str
    kind: MarketplaceItemType
    version: str
    status: MarketplaceItemStatus
    installed: bool
    installed_at: Optional[datetime] = None
    meta: dict = Field(default_factory=dict)


# ── Install/Uninstall ────────────────────────────────────────────

class InstallRequest(BaseModel):
    item_id: str = Field(..., description="Kebab-case item ID")
    source_url: Optional[str] = Field(default=None, description="Override source URL")


class InstallResponse(BaseModel):
    success: bool
    item_id: str
    message: str
    installed_path: Optional[str] = None
    error: Optional[str] = None


class UninstallRequest(BaseModel):
    item_id: str = Field(..., description="Kebab-case item ID")
    purge_config: bool = Field(default=False, description="Remove item configuration")


class UninstallResponse(BaseModel):
    success: bool
    item_id: str
    message: str
    error: Optional[str] = None


# ── Toggle Enable/Disable ────────────────────────────────────────

class ToggleRequest(BaseModel):
    item_id: str = Field(..., description="Kebab-case item ID")
    enabled: bool = Field(..., description="Enable (True) or disable (False)")


class ToggleResponse(BaseModel):
    success: bool
    item_id: str
    enabled: bool
    message: str
    error: Optional[str] = None


# ── Upgrade Version ──────────────────────────────────────────────

class UpgradeRequest(BaseModel):
    item_id: str = Field(..., description="Kebab-case item ID")
    target_version: Optional[str] = Field(
        default=None, description="Specific version to upgrade to"
    )
    backup: bool = Field(default=True, description="Create backup before upgrade")


class UpgradeResponse(BaseModel):
    success: bool
    item_id: str
    old_version: str
    new_version: str
    message: str
    backup_path: Optional[str] = None
    error: Optional[str] = None
```

### 2.3 Delete old __all__ at end of file

Remove entire `__all__ = [...]` block. (__all__ belongs in __init__.py only)

### 2.4 Verify file

```bash
# Check syntax
python3 -m py_compile src/css/modules/marketplace/types.py

# Line count
wc -l src/css/modules/marketplace/types.py src/css/modules/marketplace/types.py.bak
```

**Expected**:
- Before: 172 LOC
- After: ~100 LOC (no inheritance overhead)

---

## Step 3: Delete marketplace/base.py (15 min)

### 3.1 Verify no imports

```bash
# Check if ANYTHING imports marketplace/base.py
grep -r "from.*marketplace.*base import\|from.*\.base import" \
  src/css/ \
  --include="*.py" \
  --exclude-dir=__pycache__
```

**Expected result**: No matches (empty output)

### 3.2 Delete file

```bash
rm src/css/modules/marketplace/base.py
```

### 3.3 Verify deletion

```bash
ls -la src/css/modules/marketplace/base.py 2>&1
# Expected: No such file or directory
```

---

## Success Criteria

✅ **Step 1**: Audit complete, findings documented  
✅ **Step 2**: types.py flattened, no inheritance, ~100 LOC, syntax valid  
✅ **Step 3**: base.py deleted, no imports found, verified gone

---

## Next (Step 4-6)

After these 3 steps pass:
- Step 4: Update imports in endpoints.py + __init__.py
- Step 5: Remove __all__ from types.py (keep in __init__.py)
- Step 6: Lint + test

---

**Todos Involved**:
- cleanup-marketplace-audit-current-state
- cleanup-marketplace-flatten-types
- cleanup-marketplace-remove-base

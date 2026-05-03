# @scopes — Scope Management & Hierarchy

**Location**: `src/css/modules/scopes/`

**Responsibility**: Scope hierarchy management, scope resolution, and scope-based access control.

---

## Current State

🟡 **Skeleton** (method signatures with docstrings, bodies marked `pass`)

---

## Purpose

- Implement 5-level scope hierarchy (GLOBAL → APP → PROJECT → RUNTIME → SESSION)
- Resolve scope paths and access
- Manage scope configurations
- Handle scope inheritance and restriction
- Support scope-based permission checks

---

## Implementation Checklist

- [ ] Scope hierarchy definition
- [ ] Scope context class
- [ ] Scope configuration loading
- [ ] Scope path resolution
- [ ] Inheritance and restriction logic
- [ ] Add logger initialization in `__init__.py`

---

## Module Pattern

```python
# src/css/modules/scopes/__init__.py
"""Scope management and hierarchy."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .context import ScopeContext
from .manager import ScopeManager

__all__ = ['ScopeContext', 'ScopeManager']
```

---

**Status**: 🔴 Priority (High) | **Last Updated**: 2026-05-03
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: See .plan/modules/module-audit-matrix.md for full audit results.

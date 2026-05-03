# @scopes — Scope Management & Hierarchy

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

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

- [x] Scope hierarchy definition — HIERARCHY constant with all 5 levels
- [x] Scope context class — ScopeContext with validation
- [x] Scope configuration loading — Via ScopeContext parameters
- [x] Scope path resolution — resolve_scope_path() builds inheritance chain
- [x] Inheritance and restriction logic — Via ScopeManager._find_scope_at_level()
- [x] Add logger initialization in `__init__.py` — Full logging setup

**Completed (Phase 2 Foundation)**:
✅ ScopeLevel enum (GLOBAL, APP, PROJECT, RUNTIME, SESSION)
✅ ScopeRestriction enum (NONE, READ_ONLY, DENY, REQUIRE_AUTH, REQUIRE_ROLE)
✅ ScopeContext class with full validation
✅ ScopeManager: create, get, resolve, access control, delete, list
✅ Inheritance chain resolution via HIERARCHY
✅ Access control: can_access() with restriction-based checks
✅ Exception hierarchy (ScopeValidationError, ScopeResolutionError)
✅ Full module exports and logging

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

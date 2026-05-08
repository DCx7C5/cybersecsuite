# @accounts — Legacy Module Shim

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Ownership

`accounts` is a core-owned domain. The canonical ownership target is `src/css/core/accounts/`.

## Current State

This directory remains as a migration shim. Do not treat it as the source-of-truth ownership boundary.

## Local Rules

- ORM table models inherit `css.core.db.models.base.BaseModel`
- Module-owned `Enum` classes live in `enums.py`
- Module documentation in `src/css/modules/` uses the same-name file rule: `accounts/accounts.md`

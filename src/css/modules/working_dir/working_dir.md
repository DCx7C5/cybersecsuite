# @working_dir — Legacy Module Shim

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Ownership

`working_dir` is retired terminology. The canonical replacement is the general directory structure owned by `src/css/core/workspace/`.

## Current State

This directory exists only as a migration shim for legacy references and todo IDs.

## Local Rules

- ORM table models inherit `css.core.db.models.base.BaseModel`
- Module-owned `Enum` classes live in `enums.py`
- Module documentation in `src/css/modules/` uses the same-name file rule: `working_dir/working_dir.md`

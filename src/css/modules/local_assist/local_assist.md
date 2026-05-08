# @local_assist — Module Notes

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Reserved module slot for local assistance functionality.

## Current State

This directory is currently little more than a placeholder. The markdown stub exists to satisfy the module naming rule and to prevent the module from being undocumented.

## Local Rules

- ORM table models inherit `css.core.db.models.base.BaseModel`
- Module-owned `Enum` classes live in `enums.py`
- Module documentation in `src/css/modules/` uses the same-name file rule: `local_assist/local_assist.md`

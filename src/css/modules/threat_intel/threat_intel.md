# @threat_intel — Module Notes

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

IOC storage, threat feed ingestion, and threat-match tracking.

## Planned Architecture Role

- `modules/threat_intel/` remains the canonical relational/domain owner for threat-intel data.
- Graph-native entities and relationships should additionally project into `src/css/core/graph_rag/`.
- Typical graph projection targets: actors, malware, campaigns, tools, observables, CVEs, infrastructure, and feed-derived links.
- `core/vector_rag` consumes the graph retrieval path indirectly through `core/graph_rag` in `graph` and `hybrid` modes.

## Current State

Documentation stub created to satisfy the module markdown naming rule.

## Local Rules

- ORM table models inherit `css.core.db.models.base.BaseModel`
- Module-owned `Enum` classes live in `enums.py`
- Module documentation in `src/css/modules/` uses the same-name file rule: `threat_intel/threat_intel.md`

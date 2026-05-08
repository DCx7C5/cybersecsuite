# @mitre — MITRE ATT&CK Domain Plan

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Canonical MITRE ATT&CK domain ownership:
- tactics, techniques, sub-techniques
- groups, software, mitigations, procedures
- ATT&CK mappings used by incidents, scans, reports, and retrieval

## Planned Architecture Role

- `modules/mitre/` remains the canonical relational/domain owner for ATT&CK data.
- Graph-native ATT&CK entities and relationships should additionally project into `src/css/core/graph_rag/`.
- `core/vector_rag` consumes the resulting graph retrieval path indirectly through `graph` and `hybrid` modes.

## Key Planning Direction

- Keep ATT&CK import, normalization, and API semantics in this module.
- Project ATT&CK graph structure into Neo4j for GraphRAG retrieval.
- Do not treat Neo4j as the only source of truth for MITRE data.

## Local Rules

- ORM table models inherit `css.core.db.models.base.BaseModel`
- Module-owned `Enum` classes live in `enums.py`
- Module documentation in `src/css/modules/` uses the same-name file rule: `mitre/mitre.md`

# @threat_intel — Module Notes

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

IOC storage, threat feed ingestion, and threat-match tracking.

## Planned Architecture Role

- `modules/threat_intel/` remains the canonical relational/domain owner for threat-intel data.
- Graph-native entities and relationships should additionally project into `src/css/core/rag_graph/`.
- Typical graph projection targets: actors, malware, campaigns, tools, observables, CVEs, infrastructure, and feed-derived links.
- `core/rag_vector` consumes the graph retrieval path indirectly through `core/rag_graph` in `graph` and `hybrid` modes.

## Current State

Implemented threat-intel API and persistence for IOC and feed-backed enrichment data.

The module is mounted via `css.modules` entry points and is expected to remain the canonical relational owner before graph projection.

## Remaining Contract

| Work area | Required behavior |
|-----------|-------------------|
| Feed lifecycle | Normalize feed-supplied indicators into canonical IOC records with provenance and deduplication. |
| Retrieval projection | Emit stable actors, malware, campaigns, observables, CVEs, infrastructure, and relationships to `core/rag_graph`; relational records remain canonical. |
| Consumer bridge | Make IOC matches resolvable by incidents, reports, and SIEM analysis without duplicating source-of-truth storage. |

## Validation

- Test feed deduplication/provenance, IOC querying, and graph projection idempotence.

## Local Rules

- ORM table models inherit `css.core.db.models.base.BaseModel`
- Module-owned `Enum` classes live in `enums.py`
- Module documentation in `src/css/modules/` uses the same-name file rule: `threat_intel/threat_intel.md`

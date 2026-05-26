# @evidence — Module Notes

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Evidence collection, chain-of-custody tracking, and evidence tagging.

## Current State

Implemented HTTP API (`/api/evidence`) for:
- evidence collection and retrieval
- chain-of-custody history and event recording
- evidence tagging and tag listing

Authorization enforces org ownership via `X-Org-ID` header matching request `org_id`.

## Remaining Contract

| Gap | Required implementation |
|-----|-------------------------|
| Actor attribution | Replace placeholder `source_agent_id` and `actor_id` values with authenticated caller/agent context. |
| Chain integrity | Verify cryptographic signatures and hash continuity on retrieval; chain records are append-only. |
| Domain completion | Preserve evidence metadata, session/incident linkage, and safe retrieval/download behavior described by `domain-evidence`. |

## Validation

- Reject cross-organization retrieval and mutation.
- Detect altered chain entries/signatures.
- Verify the authenticated actor is persisted on collection and custody events.

## Local Rules

- ORM table models inherit `css.core.db.models.base.BaseModel`
- Module-owned `Enum` classes live in `enums.py`
- Module documentation in `src/css/modules/` uses the same-name file rule: `evidence/evidence.md`

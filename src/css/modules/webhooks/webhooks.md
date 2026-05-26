# @webhooks — Module Notes

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: Track todo state in `.plan/session.db`. Keep this file aligned with live work when touching this directory.

## Purpose

Outbound webhook endpoint configuration and delivery attempts.

## Current State

Implemented HTTP API (`/api/webhooks`) for:
- endpoint registration and listing
- event dispatch
- delivery history inspection

Deliveries are tracked as persisted records for operational observability.

## Implementation Contract

| Concern | Required behavior |
|---------|-------------------|
| Delivery security | Sign outbound payloads with HMAC-SHA256 using the endpoint secret and expose no raw secret in API responses or logs. |
| Reliability | Retry transient delivery failures with bounded backoff and persist each terminal delivery outcome. |
| Integration | Alert/notification fan-out may call this module; domain modules should emit events rather than duplicate webhook transmission. |

## Validation

- Verify signature generation, endpoint organization isolation, retry limits, and persisted failure/success history.

## Local Rules

- ORM table models inherit `css.core.db.models.base.BaseModel`
- Module-owned `Enum` classes live in `enums.py`
- Module documentation in `src/css/modules/` uses the same-name file rule: `webhooks/webhooks.md`

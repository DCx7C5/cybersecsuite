---
type: artifact
name: "${ARTIFACT_NAME}"
version: ${ARTIFACT_VERSION}
description: "${ARTIFACT_DESCRIPTION}"
created_at: "${CREATED_AT}"
created_by: "${CREATED_BY}"
alg: Ed25519
hash: blake2b
kid: "${KEY_ID}"
sig: "${SIGNATURE}"
---

# ${ARTIFACT_NAME}

## Content

```json
${ARTIFACT_CONTENT}
```

## Integrity

| Field           | Value              |
|-----------------|--------------------|
| Content Hash    | `${CONTENT_HASH}`  |
| Body Hash       | `${BODY_HASH}`     |
| Signature Valid | ${SIGNATURE_VALID} |
| Expires At      | ${EXPIRES_AT}      |

---

## Audit Trail

${SIGNATURE_LOG}

---
checksum: "${CHECKSUM}"
verified_at: "${VERIFIED_AT}"
---
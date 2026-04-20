---
type: artifact
name: "{{ artifact_name }}"
version: {{ artifact_version }}
description: "{{ artifact_description }}"
created_at: "{{ created_at }}"
created_by: "{{ created_by }}"
alg: Ed25519
hash: blake2b
kid: "{{ key_id }}"
sig: "{{ signature }}"
---

# {{ artifact_name }}

## Content

```json
{{ artifact_content }}
```

## Integrity

| Field           | Value              |
|-----------------|--------------------|
| Content Hash    | `{{ content_hash }}`  |
| Body Hash       | `{{ body_hash }}`     |
| Signature Valid | {{ signature_valid }} |
| Expires At      | {{ expires_at }}      |

---

## Audit Trail

{{ signature_log }}

---
checksum: "{{ checksum }}"
verified_at: "{{ verified_at }}"
---
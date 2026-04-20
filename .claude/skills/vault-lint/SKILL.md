---
name: vault-lint
description: >
  Lint and health-check the CyberSecSuite forensic vault. Finds orphan pages,
  missing indexes, stale hot cache, dead wikilinks.
  Triggers: "lint vault", "vault health", "check vault", "orphan pages".
allowed-tools: Read Glob Grep mcp__cybersec__vault_lint mcp__cybersec__vault_status
---

# vault-lint: Forensic Vault Health Check

---

## Lint Flow

1. Call `vault_lint` MCP tool — returns issues list, unreferenced pages, page count.
2. Call `vault_status` MCP tool — returns counts and hot cache age.
3. Report findings in a clean summary.
4. Offer to fix each category of issue.

---

## Issue Categories

| Issue | Fix |
|-------|-----|
| Missing wiki/hot.md | Run vault_scaffold |
| Missing index.md | Run vault_scaffold |
| Stale hot cache (>24h) | Update hot.md with recent context |
| Missing _index.md | Create sub-index for the domain |
| Unreferenced page | Add wikilink to index.md or parent |

---

## Report Format

```
## Vault Lint Report

**Status:** ✅ Healthy / ⚠️ Issues found

**Stats:**
- Pages: N
- Canvases: N
- Sources ingested: N
- Hot cache age: Xh Ym

**Issues:**
- [issue 1]
- [issue 2]

**Unreferenced pages (top 10):**
- wiki/entities/SomeEntity.md
- ...

**Recommended actions:**
1. [action]
```

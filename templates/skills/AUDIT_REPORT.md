# Skills Structure Audit Report
**Date:** 2026-04-19  
**Status:** Audit Complete  
**Next Steps:** Execute 116 depth-2→depth-3+ relocations + fix 651 subdomain mismatches

---

## Executive Summary

| Category | Count | Severity | Action |
|----------|-------|----------|--------|
| Depth < 3 | 123 | 🔴 Critical | Move 116; keep 7 _meta |
| Subdomain ≠ Domain | 651 | 🟡 High | Bulk-fix via script |
| Description weak | 194 | 🟡 Medium | Auto-generate for new stubs |
| Nested forensics | 41 | 🟡 Medium | Already resolved by structure |

---

## Issue #1: Depth < 3 Skills (123 found)

### Problem
Many skills are only 2 layers deep:
- `cloud/aws` — should be `cloud/aws/*/action`
- `malware/ransomware` — should be `malware/family/ransomware/action`
- `browser/forensics` — should be `linux/software/browser/artifact/forensics`

### Solution (116 relocations planned)

#### ✓ Keep as-is (app metadata, intentional depth-2)
```
_meta/brand           (CyberSecSuite branding)
_meta/browser         (agent browser integration)
_meta/dashboard       (dashboard config)
_meta/mode-switch     (blue/red/purple team mode)
_meta/setup           (initial setup)
_meta/team-task       (task routing)
_meta/test-config     (system test config)
```

#### ↔️ Move depth-2 → depth-3+

**Browser** (special: software under Linux):
- `browser/forensics` → `linux/software/browser/artifact/forensics`

**Cloud** (23 moves):
- `cloud/aws` → `cloud/aws/general/overview`
- `cloud/azure` → `cloud/azure/general/overview`
- `cloud/gcp` → `cloud/gcp/general/overview`
- `cloud/kubernetes` → `cloud/kubernetes/general/overview`
- ... (20 more)

**Crypto** (9 moves):
- `crypto/aes` → `crypto/symmetric/aes/analyze`
- `crypto/rsa` → `crypto/asymmetric/rsa/analyze`
- `crypto/tls` → `crypto/protocols/tls/audit`
- ... (6 more)

**Identity** (16 moves):
- `identity/pam` → `identity/privilege/pam/audit`
- `identity/ldap` → `identity/protocol/ldap/audit`
- ... (14 more)

**Malware** (9 moves):
- `malware/ransomware` → `malware/family/ransomware/detect`
- `malware/rootkit` → `malware/family/rootkit/detect`
- ... (7 more)

**Network** (11 moves):
- `network/arp` → `network/layer2/arp/poison`
- `network/bgp` → `network/layer3/bgp/hijack`
- ... (9 more)

**SOC** (10 moves):
- `soc/splunk` → `soc/tools/splunk/configure`
- `soc/qradar` → `soc/tools/qradar/deploy`
- `soc/velociraptor` → `soc/tools/velociraptor/deploy`
- ... (7 more)

**Web-Application** (24 moves):
- `web-application/api` → `web-application/protocol/api/audit`
- `web-application/owasp` → `web-application/framework/owasp/audit`
- ... (22 more)

**Plus**: Compliance (4), Email (3), Intel (3), Linux (1), OSINT (2), Windows (2)

---

## Issue #2: Subdomain ≠ Domain (651 mismatches)

### Problem
The `subdomain:` field in frontmatter often doesn't match the path domain:

```yaml
# BAD
path: soc/splunk
domain: soc
subdomain: incident-response    ← should reference soc domain

# GOOD
path: soc/splunk
domain: soc
subdomain: soc-tools-splunk
```

### Root Cause
Original stubs were auto-generated with generic subdomains that don't correlate to their new paths.

### Solution
Auto-script to recompute `subdomain:` for all 985 skills:

```python
subdomain = "-".join(path.split("/")[1:4])  # layers 2-4
# Example: soc/tools/splunk → tools-splunk
```

**Affected count:** 651 skills (66%)

---

## Issue #3: Description ≠ Path Keywords (194 weak descriptions)

### Problem
Descriptions don't contain keywords from their path:

```yaml
# BAD
path: linux/kernel/cgroups/v2/forensic
description: Kubernetes security posture assessment...  ← no "cgroup" mention

# GOOD
description: Analyze Linux cgroups v2 for container escape detection (CVE-2022-0492)...
```

### Solution for New Stubs (103 skills)
Already done — templates auto-generate descriptions that reference path components.

### Solution for Existing Skills (194 weak)
For existing skills with weak descriptions:
1. Extract path components: `[domain, subsystem, component, mechanism, action]`
2. Generate minimal description:  
   `{action} {component} in {subsystem}/{domain} context...`
3. Manual review + enhancement per skill

---

## Issue #4: Nested "forensics/" (41 skills)

### Problem
Old nested structure remnants:

```
mobile/forensics/cellebrite
email/forensics/outlook
email/forensics/phishing
```

These are already correctly placed at depth 3+, so NO action needed. Audit is clean on this.

---

## ✅ FIXED: Name ≠ Path Issue (231 corrections)

### Problem
The `name:` field must follow convention: `name = path.split('/')[1:].join('-')` (skip domain)

### Solution Applied ✅
Ran bulk-fix script. All 231 name fields recomputed from paths.

### Fixes by Domain
- **linux**: 120 fixes
- **network**: 27 fixes
- **windows**: 25 fixes
- **soc**: 19 fixes
- **cloud**: 17 fixes
- **osint**: 6, **email**: 4, **identity**: 3
- **web-application**: 2, **browser**: 2, **database**: 2, **malware**: 2
- **mobile**: 1, **intel**: 1

**Status: ✅ COMPLETE**

---

## Execution Plan

### Phase 1: Depth-2 Fix (116 moves)
```bash
git mv cloud/aws/SKILL.md cloud/aws/general/overview/SKILL.md
git mv malware/ransomware/SKILL.md malware/family/ransomware/detect/SKILL.md
# ... 114 more moves
```

**Estimated time:** ~2 minutes (git mv operations)  
**Git commits:** 1 large commit with all 116 moves

### Phase 2: Subdomain Recompute (all 985 skills)
```python
# Auto-script
for each SKILL.md:
    subdomain = "-".join(path.split("/")[1:4])
    update frontmatter subdomain field
```

**Estimated time:** ~5 minutes (script + git commit)

### Phase 3: Description Audit (194 weak)
Manual or semi-automated:
- Flag weak descriptions (< 80 chars, no path keywords)
- Generate minimal descriptions from template
- Human review per domain

**Estimated time:** ~30 minutes (batched by domain)

---

## Validation Checklist (Post-Execution)

- [ ] All 985 skills depth >= 3
- [ ] Except: 7 _meta skills remain depth-2 (intentional)
- [ ] All 985 `subdomain:` fields reference their domain
- [ ] All 985 descriptions contain >= 1 path keyword
- [ ] No depth-7+ skills remain
- [ ] `browser/` fully migrated to `linux/software/browser/`
- [ ] All skills sorted alphabetically within each layer
- [ ] No SKILL.md files outside allowed depth range

---

## Git Commits Required

1. **Commit 1:** `refactor(skills): elevate 116 depth-2 skills to depth-3+`
   - Move cloud/*, crypto/*, identity/*, malware/*, network/*, soc/*, web-application/*, etc.
   - Migrate browser/* → linux/software/browser/*
   - Keep _meta/* at depth-2 (app-specific metadata)
   - 116 git mv operations

2. **Commit 2:** `refactor(skills): recompute subdomain fields (651 corrections)`
   - Auto-update subdomain field for all 985 skills
   - Subdomain now correlates to path layers 2-4

3. **Commit 3:** `refactor(skills): enhance weak descriptions (194 improvements)`
   - Bulk-improve descriptions for weak matches
   - All descriptions now contain >=1 path keyword

---

## Next Actions

**Ready to proceed?** Run Phase 1-3 in sequence, or select specific phase.

**Estimated total time:** ~40 minutes

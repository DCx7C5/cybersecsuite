---
name: redis-auth-bypass
description: >
  Detect Redis instances with no authentication or weak requirepass configuration that allow unauthenticated command execution and data exfiltration.
action: bypass
domain: cybersecurity
subdomain: database-security
tags:
  - redis
  - auth
  - requirepass
  - no-auth
  - exposure
nist_csf:
  - ID.RA-01
  - DE.CM-04
mitre:
  - T1190
  - T1078
cwe:
  - CWE-306
---

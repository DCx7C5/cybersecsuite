---
name: permission-suid-enum
description: >
  Enumerate SUID/SGID binaries across the filesystem to identify privilege escalation vectors, unexpected setuid programs, and GTFOBins-exploitable executables.
action: enum
domain: cybersecurity
subdomain: filesystem-security
tags:
  - suid
  - sgid
  - privilege-escalation
  - gtfobins
  - find
  - linux-hardening
nist_csf:
  - ID.RA-01
  - PR.AC-04
mitre:
  - T1548.001
cwe:
  - CWE-250
capec: []
---

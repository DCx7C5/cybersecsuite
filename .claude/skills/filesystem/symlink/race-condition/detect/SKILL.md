---
name: symlink-race-condition-detect
description: >
  Detect symlink-following TOCTOU race conditions in SUID programs and system services that allow privilege escalation through controlled symlink redirection.
action: detect
domain: cybersecurity
subdomain: filesystem-security
tags:
  - symlink
  - toctou
  - race-condition
  - suid
  - privilege-escalation
nist_csf:
  - DE.CM-04
mitre:
  - T1548.001
cwe:
  - CWE-362
  - CWE-61
capec: []
---

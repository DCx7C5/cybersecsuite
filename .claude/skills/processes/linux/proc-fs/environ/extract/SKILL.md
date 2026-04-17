---
name: linux-proc-fs-environ-extract
description: >
  Extract process environment variables from /proc/<PID>/environ to recover secrets, tokens, credentials, and configuration injected at process launch.
action: extract
domain: cybersecurity
subdomain: process-forensics
tags:
  - proc-environ
  - environment-variable
  - secret
  - token
  - linux
  - process-forensics
nist_csf:
  - DE.CM-04
  - DE.AE-02
mitre:
  - T1552.007
  - T1057
cwe:
  - CWE-200
capec: []
---

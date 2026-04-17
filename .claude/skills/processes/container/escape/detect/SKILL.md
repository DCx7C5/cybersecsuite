---
name: container-escape-detect
description: >
  Detect container escape attempts exploiting privileged mode, dangerous capabilities, host path mounts, and runtime vulnerabilities in Docker, containerd, and runc.
action: detect
domain: cybersecurity
subdomain: process-forensics
tags:
  - container-escape
  - docker
  - privileged-container
  - cve-2019-5736
  - runc
  - runtime
nist_csf:
  - DE.CM-04
  - ID.RA-01
mitre:
  - T1611
  - T1068
cwe:
  - CWE-269
---

---
name: linux-proc-fs-maps-analyze
description: >
  Analyse /proc/<PID>/maps to identify memory regions, shared libraries, anonymous executable segments, and injected shellcode in running processes.
action: analyze
domain: cybersecurity
subdomain: process-forensics
tags:
  - proc-maps
  - memory-map
  - injection
  - shellcode
  - anonymous-exec
  - linux
nist_csf:
  - DE.CM-04
  - DE.AE-02
mitre:
  - T1055
  - T1620
---

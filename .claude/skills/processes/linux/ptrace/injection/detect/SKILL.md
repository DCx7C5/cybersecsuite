---
name: linux-ptrace-injection-detect
description: >
  Detect ptrace-based process injection by monitoring PTRACE_POKEDATA syscalls, /proc/<PID>/mem writes, and unusual parent-child ptrace relationships.
action: detect
domain: cybersecurity
subdomain: process-forensics
tags:
  - ptrace
  - injection
  - process-injection
  - syscall
  - ebpf
  - auditd
nist_csf:
  - DE.CM-04
  - DE.AE-02
mitre:
  - T1055.008
  - T1055
cwe:
  - CWE-732
capec: []
---

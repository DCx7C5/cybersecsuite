
---
name: kernel-syscall-userfaultfd-race-detect
description: Detect userfaultfd-based race condition exploits — identify processes using userfaultfd to slow kernel operations and win race conditions in privilege escalation.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- userfaultfd
- race-condition
- exploit
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []

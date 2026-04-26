
---
name: memory-heap-use-after-free-detect
description: Detect heap use-after-free vulnerabilities in userland applications — identify dangling pointer dereferences, double-free conditions, and heap metadata corruption.
domain: cybersecurity
subdomain: memory-security
tags:
- linux
- heap
- use-after-free
- uaf
- memory-corruption
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []


---
name: hardening-aslr-nx-configure-verify
description: Verify and configure ASLR and NX/DEP stack protection — check randomization level, verify NX bit on stack/heap, audit execstack binaries, and configure system-wide settings.
domain: cybersecurity
subdomain: hardening-assessment
tags:
- linux
- aslr
- nx
- dep
- harden
- verify
nist_csf:
- PR.DS-06
- ID.RA-05
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []


---
name: hardening-kernel-config-audit
description: Audit kernel build configuration for security settings — review /boot/config-*, check for missing hardening options (CFI, SMEP, SMAP, KASLR, KPTI) against security benchmarks.
domain: cybersecurity
subdomain: hardening-assessment
tags:
- linux
- kernel
- config
- audit
- harden
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
- T1600
capec: []

---
name: hardening-grsecurity-patch-assess-audit
description: Assess Grsecurity/PaX kernel hardening patch effectiveness — evaluate RBAC policy, UDEREF, SMEP/SMAP enforcement, and PAX_MEMORY_SANITIZE configuration.
domain: cybersecurity
subdomain: hardening-assessment
tags:
- linux
- grsecurity
- pax
- kernel
- hardening
nist_csf:
- ID.RA-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []

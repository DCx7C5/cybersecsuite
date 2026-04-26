
---
name: hardware-cpu-microcode-integrity-verify
description: Verify CPU microcode integrity and update status to ensure hardware-level mitigations are applied against known CPU vulnerabilities.
domain: cybersecurity
subdomain: hardware-security
tags:
- linux
- cpu
- microcode
- integrity
nist_csf:
- PR.DS-06
- ID.RA-05
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1600
capec: []

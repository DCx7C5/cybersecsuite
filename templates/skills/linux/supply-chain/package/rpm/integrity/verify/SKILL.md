
---
name: supply-chain-package-rpm-integrity-verify
description: Verify RPM package integrity — use rpm -V to check all installed file attributes, validate GPG signatures, and detect modified system binaries.
domain: cybersecurity
subdomain: supply-chain-security
tags:
- linux
- rpm
- redhat
- package
- integrity
- verify
nist_csf:
- PR.DS-06
- ID.RA-05
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1195.002
capec: []

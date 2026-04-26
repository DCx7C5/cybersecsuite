
---
name: identity-polkit-privilege-escalate-detect
description: Detect polkit privilege escalation (PwnKit CVE-2021-4034, CVE-2021-3560) — identify pkexec abuse, unauthorized polkit policy modifications, and privilege escalation via D-Bus.
domain: cybersecurity
subdomain: identity-security
tags:
- linux
- polkit
- pkexec
- privesc
- cve
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
- T1548
capec: []

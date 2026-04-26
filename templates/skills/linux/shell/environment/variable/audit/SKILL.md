
---
name: shell-environment-variable-audit
description: Audit shell environment variables across all running processes — identify sensitive data in environment, dangerous overrides, and variables used for privilege escalation.
domain: cybersecurity
subdomain: process-security
tags:
- linux
- environment
- variable
- audit
- security
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1078
- T1548
capec: []


---
name: containers-namespace-user-privesc-detect
description: Detect user namespace privilege escalation — identify unprivileged user namespace abuse, newuidmap/newgidmap exploitation, and namespace-based sandbox escape.
domain: cybersecurity
subdomain: container-security
tags:
- linux
- namespace
- user-namespace
- privesc
- container
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1611
- T1068
capec: []

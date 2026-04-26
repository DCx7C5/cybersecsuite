
---
name: containers-apparmor-profile-audit
description: Audit container AppArmor profiles — verify AppArmor confinement for container processes, identify containers with unconfined profiles, and audit policy effectiveness.
domain: cybersecurity
subdomain: container-security
tags:
- linux
- container
- apparmor
- docker
- kubernetes
- audit
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1611
capec: []

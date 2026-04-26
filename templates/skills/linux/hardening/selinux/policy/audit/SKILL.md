
---
name: hardening-selinux-policy-audit
description: Audit SELinux policy effectiveness — review policy modules, identify permissive domains, audit-allow rules, and detect policy weaknesses that allow privilege escalation.
domain: cybersecurity
subdomain: hardening-assessment
tags:
- linux
- selinux
- policy
- audit
- mac
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
- T1548
capec: []

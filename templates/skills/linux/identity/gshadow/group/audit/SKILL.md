
---
name: identity-gshadow-group-audit
description: Audit /etc/gshadow and group privilege assignments — identify groups with excessive members, sudo-equivalent groups (wheel, sudo, docker, disk), and shadow group misconfigurations.
domain: cybersecurity
subdomain: identity-security
tags:
- linux
- gshadow
- group
- privilege
- audit
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

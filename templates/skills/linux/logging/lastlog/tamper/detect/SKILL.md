
---
name: logging-lastlog-tamper-detect
description: Detect lastlog file tampering — identify modifications to /var/log/lastlog that erase attacker last-login timestamps, commonly done after initial compromise.
domain: cybersecurity
subdomain: logging-forensics
tags:
- linux
- lastlog
- login
- tamper
- anti-forensics
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1070.006
capec: []


---
name: logging-journald-binary-tamper-detect
description: Detect systemd journal log tampering — identify journal file corruption, log rotation abuse, unauthorized journal forwarding, and missing entries indicating attacker log removal.
domain: cybersecurity
subdomain: logging-forensics
tags:
- linux
- journald
- systemd
- log
- tamper
- anti-forensics
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1070.002
capec: []

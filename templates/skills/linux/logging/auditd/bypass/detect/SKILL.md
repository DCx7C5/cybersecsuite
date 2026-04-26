
---
name: logging-auditd-bypass-detect
description: Detect auditd bypass and evasion techniques — identify LD_PRELOAD hooking of audit libraries, auditd process termination, rule flooding, and buffer overflow evasion.
domain: cybersecurity
subdomain: logging-security
tags:
- linux
- auditd
- bypass
- evasion
- detect
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1562.001
- T1070
capec: []

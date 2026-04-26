
---
name: logging-utmp-wtmp-tamper-detect
description: Detect utmp/wtmp login record tampering — identify modifications to /var/run/utmp, /var/log/wtmp, /var/log/btmp used to erase attacker login history.
domain: cybersecurity
subdomain: logging-forensics
tags:
- linux
- utmp
- wtmp
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

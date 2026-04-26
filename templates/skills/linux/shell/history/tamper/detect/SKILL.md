
---
name: shell-history-tamper-detect
description: Detect shell history tampering — identify HISTFILE=/dev/null tricks, HISTSIZE=0, history deletion, and commands to disable history recording used to cover attacker tracks.
domain: cybersecurity
subdomain: forensic-detection
tags:
- linux
- shell
- history
- tamper
- anti-forensics
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1070.003
capec: []

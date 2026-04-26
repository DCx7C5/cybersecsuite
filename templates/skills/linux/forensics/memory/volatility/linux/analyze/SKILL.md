
---
name: forensics-memory-volatility-linux-analyze
description: Analyze Linux memory dumps with Volatility3 — enumerate processes, network connections, kernel modules, bash history from memory, and detect in-memory rootkits.
domain: cybersecurity
subdomain: forensic-analysis
tags:
- linux
- volatility
- memory
- forensics
- analyze
nist_csf:
- DE.AE-02
- RS.AN-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1057
- T1014
- T1083
capec: []


---
name: identity-shadow-file-tamper-detect
description: Detect /etc/shadow and /etc/passwd tampering — identify unauthorized modifications to credential stores, added backdoor accounts, and hash algorithm downgrades.
domain: cybersecurity
subdomain: identity-forensics
tags:
- linux
- shadow
- passwd
- tamper
- backdoor
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1003.008
- T1136.001
capec: []


---
name: filesystem-quota-abuse-detect
description: Detect disk quota abuse — identify quota bypass techniques, soft/hard limit manipulation, and quota exhaustion attacks used for denial of service.
domain: cybersecurity
subdomain: filesystem-security
tags:
- linux
- quota
- disk
- abuse
- dos
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1499
capec: []

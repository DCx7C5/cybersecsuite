
---
name: kernel-network-stack-tc-covert-channel-detect
description: Detect Traffic Control (tc) covert channels — identify malicious tc filters or qdiscs used to exfiltrate data or create timing-based covert communication.
domain: cybersecurity
subdomain: network-forensics
tags:
- linux
- tc
- traffic-control
- covert-channel
- exfil
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1071
- T1048
capec: []

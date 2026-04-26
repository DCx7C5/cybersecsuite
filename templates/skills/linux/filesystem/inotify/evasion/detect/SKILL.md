
---
name: filesystem-inotify-evasion-detect
description: Detect inotify watch evasion — identify techniques to bypass filesystem monitoring (rename tricks, O_CREAT patterns, FIFO bypass) used by malware to avoid detection.
domain: cybersecurity
subdomain: filesystem-security
tags:
- linux
- inotify
- evasion
- bypass
- monitoring
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1562
- T1036
capec: []

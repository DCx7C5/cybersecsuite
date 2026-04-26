
---
name: shell-alias-hijack-detect
description: Detect shell alias hijacking — identify malicious aliases overriding common commands (ls, ps, netstat, sudo) in .bashrc or /etc/profile.d/ used by rootkits to hide activity.
domain: cybersecurity
subdomain: persistence-detection
tags:
- linux
- shell
- alias
- hijack
- rootkit
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1574
- T1036
capec: []


---
name: services-rc-local-backdoor-detect
description: Detect rc.local and SysV init script backdoors — inspect /etc/rc.local, /etc/init.d/, and runlevel-specific directories for unauthorized startup scripts.
domain: cybersecurity
subdomain: persistence-detection
tags:
- linux
- rc-local
- sysv
- init
- backdoor
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1037.004
capec: []

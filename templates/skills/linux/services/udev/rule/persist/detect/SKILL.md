
---
name: services-udev-rule-persist-detect
description: Detect udev rule persistence — inspect /etc/udev/rules.d/ and /lib/udev/rules.d/ for unauthorized rules that execute commands on device events, commonly used for persistence.
domain: cybersecurity
subdomain: persistence-detection
tags:
- linux
- udev
- rule
- persistence
- device
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1543
- T1037
capec: []

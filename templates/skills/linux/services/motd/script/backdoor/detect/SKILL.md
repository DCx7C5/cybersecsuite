
---
name: services-motd-script-backdoor-detect
description: Detect /etc/update-motd.d/ script backdoors — identify unauthorized executable scripts in MOTD directories that execute as root on every SSH login for persistence or C2.
domain: cybersecurity
subdomain: persistence-detection
tags:
- linux
- motd
- update-motd
- backdoor
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1037
- T1543
capec: []

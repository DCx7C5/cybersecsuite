
---
name: services-systemd-timer-persist-detect
description: Detect systemd timer-based persistence — enumerate all .timer units, identify timers not associated with legitimate services, and detect cron replacement via systemd timers.
domain: cybersecurity
subdomain: persistence-detection
tags:
- linux
- systemd
- timer
- cron
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1053.006
capec: []


---
name: services-systemd-unit-persist-detect
description: Detect systemd service and unit file persistence — scan all unit directories for unauthorized services, check WantedBy/RequiredBy dependencies, and identify post-exploit persistence.
domain: cybersecurity
subdomain: persistence-detection
tags:
- linux
- systemd
- service
- persistence
- detect
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1543.002
- T1053
capec: []

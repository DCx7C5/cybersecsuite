
---
name: services-at-job-persist-detect
description: Detect at/batch job persistence — enumerate scheduled at jobs, identify unusual one-time execution jobs used for delayed payload execution or persistence.
domain: cybersecurity
subdomain: persistence-detection
tags:
- linux
- at
- batch
- persistence
- detect
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1053.002
capec: []

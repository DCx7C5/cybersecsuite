
---
name: filesystem-coredump-artifact-collect
description: Collect and analyze core dump artifacts — configure core dump destinations, extract credentials and sensitive data from process core dumps, detect malicious core dump triggers.
domain: cybersecurity
subdomain: filesystem-forensics
tags:
- linux
- coredump
- core-dump
- artifact
- forensics
nist_csf:
- RS.AN-01
- DE.CM-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1005
capec: []


---
name: kernel-memory-kpti-bypass-detect
description: Detect Kernel Page Table Isolation (KPTI/KAISER) bypass attempts — Meltdown exploitation indicators, kernel address leaks, and PTI disablement via cmdline.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- kpti
- meltdown
- kernel
- bypass
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
- T1600
capec: []

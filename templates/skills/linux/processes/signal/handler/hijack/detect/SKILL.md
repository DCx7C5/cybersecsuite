
---
name: processes-signal-handler-hijack-detect
description: Detect signal handler hijacking — identify processes registering unusual signal handlers (SIGSEGV, SIGILL) to gain code execution or persist through crashes.
domain: cybersecurity
subdomain: process-forensics
tags:
- linux
- signal
- handler
- hijack
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1055
- T1543
capec: []


---
name: memory-stack-canary-bypass-detect
description: Detect stack canary bypass techniques — identify stack smashing attempts, canary leak via format strings, and ret2libc/ROP chains in application crashes.
domain: cybersecurity
subdomain: memory-security
tags:
- linux
- stack
- canary
- bypass
- exploit
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []

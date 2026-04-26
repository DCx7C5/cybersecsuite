
---
name: kernel-memory-kaslr-bypass-detect
description: Detect KASLR (Kernel Address Space Layout Randomization) bypass attempts — side-channel leaks via /proc/kallsyms, timing attacks, and information disclosure vulnerabilities.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- kaslr
- kernel
- aslr
- bypass
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []

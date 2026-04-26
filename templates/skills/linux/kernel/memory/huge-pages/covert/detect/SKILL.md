
---
name: kernel-memory-huge-pages-covert-detect
description: Detect huge pages timing side-channel attacks — identify processes abusing huge pages for ASLR entropy reduction or cross-process memory probing.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- huge-pages
- side-channel
- aslr
- covert
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []


---
name: supply-chain-shared-library-preload-detect
description: Detect /etc/ld.so.preload backdoors and LD_PRELOAD injection — identify unauthorized entries forcing malicious shared libraries into every process's address space.
domain: cybersecurity
subdomain: supply-chain-security
tags:
- linux
- ld-so-preload
- shared-library
- rootkit
- hijack
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1574.006
- T1014
capec: []

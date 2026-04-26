
---
name: memory-nx-bypass-detect
description: Detect NX/DEP bypass techniques — identify ret2libc chains, JIT spraying, and return-oriented programming attacks that execute code from non-executable memory regions.
domain: cybersecurity
subdomain: memory-security
tags:
- linux
- nx
- dep
- rop
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

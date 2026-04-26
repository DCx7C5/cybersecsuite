
---
name: kernel-boot-secure-boot-bypass-detect
description: Detect Secure Boot bypass techniques — MOK (Machine Owner Key) abuse, shim loader manipulation, unsigned module loading, and UEFI variable tampering.
domain: cybersecurity
subdomain: kernel-forensics
tags:
- linux
- secure-boot
- shim
- mok
- bypass
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1542.001
capec: []

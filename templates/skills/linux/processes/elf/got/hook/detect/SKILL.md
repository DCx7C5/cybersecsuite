
---
name: processes-elf-got-hook-detect
description: Detect GOT (Global Offset Table) hooking in ELF binaries — identify runtime function pointer overwrites used by rootkits and malware to intercept shared library calls.
domain: cybersecurity
subdomain: process-forensics
tags:
- linux
- elf
- got
- hook
- rootkit
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1574.007
- T1014
capec: []

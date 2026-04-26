
---
name: processes-elf-plt-hook-detect
description: Detect PLT (Procedure Linkage Table) hooking — identify function interception via PLT/GOT manipulation in running processes or ELF binary patching.
domain: cybersecurity
subdomain: process-forensics
tags:
- linux
- elf
- plt
- hook
- interception
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1574.007
capec: []

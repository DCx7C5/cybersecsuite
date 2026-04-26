
---
name: kernel-syscall-ptrace-abuse-detect
description: Detect ptrace syscall abuse beyond process injection — unauthorized debugger attachment, credential scraping from traced processes, and ptrace-based sandbox escape.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- ptrace
- syscall
- abuse
- sandbox-escape
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1055
- T1003
capec: []


---
name: processes-proc-fs-mem-inject-detect
description: Detect /proc/pid/mem write injection — identify processes writing to other processes via the /proc filesystem mem file, a stealthy injection technique requiring only ptrace_attach.
domain: cybersecurity
subdomain: process-security
tags:
- linux
- proc
- mem
- injection
- ptrace
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1055
- T1083
capec: []


---
name: kernel-syscall-io-uring-abuse-detect
description: Detect io_uring syscall interface abuse — identify exploitation of io_uring vulnerabilities (CVE-2022-29582, CVE-2023-2598) and unauthorized use for sandboxed process escape.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- io-uring
- syscall
- exploit
- cve
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []

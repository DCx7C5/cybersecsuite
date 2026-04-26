
---
name: kernel-boot-kexec-abuse-detect
description: Detect kexec abuse — identify unauthorized kernel replacement via kexec_load syscall, which allows loading a new kernel without hardware reboot (bypasses Secure Boot).
domain: cybersecurity
subdomain: kernel-forensics
tags:
- linux
- kexec
- kernel
- bypass
- secure-boot
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1542
- T1068
capec: []

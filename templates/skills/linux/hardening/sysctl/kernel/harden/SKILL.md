
---
name: hardening-sysctl-kernel-harden
description: Harden Linux kernel via sysctl parameters — configure ASLR, kernel pointer hiding, TCP hardening, SYN cookies, ICMP restrictions, and core dump disabling.
domain: cybersecurity
subdomain: hardening-implementation
tags:
- linux
- sysctl
- kernel
- harden
- configuration
nist_csf:
- PR.IP-01
- PR.PT-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
- T1021
capec: []

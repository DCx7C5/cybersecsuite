
---
name: kernel-syscall-seccomp-filter-harden
description: Apply and audit seccomp-BPF filters to restrict syscall surface — create minimal syscall allowlists, verify filter inheritance, and test filter effectiveness.
domain: cybersecurity
subdomain: kernel-hardening
tags:
- linux
- seccomp
- syscall
- sandbox
- harden
nist_csf:
- PR.IP-01
- PR.PT-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []

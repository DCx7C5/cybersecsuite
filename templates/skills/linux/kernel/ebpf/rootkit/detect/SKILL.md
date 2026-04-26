
---
name: kernel-ebpf-rootkit-detect
description: Detect eBPF-based rootkits (Boopkit, bad-bpf) — identify unauthorized BPF programs hiding processes, files, or network connections via BPF map inspection and program enumeration.
domain: cybersecurity
subdomain: kernel-forensics
tags:
- linux
- ebpf
- bpf
- rootkit
- detect
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1014
- T1059.004
capec: []


---
name: kernel-ebpf-verifier-bypass-detect
description: Detect eBPF verifier bypass exploits — identify malformed BPF programs exploiting verifier bugs (CVE-2021-3490, CVE-2022-23222) to achieve kernel code execution.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- ebpf
- bpf
- verifier
- exploit
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []

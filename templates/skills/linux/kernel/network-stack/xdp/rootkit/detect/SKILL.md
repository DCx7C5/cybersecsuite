
---
name: kernel-network-stack-xdp-rootkit-detect
description: Detect XDP (eXpress Data Path) based rootkits — identify malicious XDP programs attached to network interfaces that silently drop or redirect traffic.
domain: cybersecurity
subdomain: kernel-forensics
tags:
- linux
- xdp
- ebpf
- rootkit
- network
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1014
- T1562.004
capec: []


---
name: kernel-ebpf-map-covert-channel-detect
description: Detect eBPF maps used as covert communication channels — identify BPF maps shared between processes for inter-process communication bypassing normal IPC auditing.
domain: cybersecurity
subdomain: kernel-forensics
tags:
- linux
- ebpf
- bpf
- map
- covert-channel
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1071
- T1014
capec: []

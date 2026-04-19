
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
---
# Kernel Ebpf Rootkit Detect
## Overview
This skill covers detection of rootkit security incidents and anomalies on Linux systems. Detect eBPF-based rootkits (Boopkit, bad-bpf) — identify unauthorized BPF programs hiding processes, files, or network connections via BPF map inspection and program enumeration.
## When to Use
- When investigating or working with rootkit in a kernel-level security investigation context
- When detecting rootkit compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: bpftool prog list, bpftool map, bpftrace, /sys/fs/bpf
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-ebpf-rootkit-detect
```
## Forensic Workflow
1. Identify scope — determine what rootkit elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| rootkit indicator | T1014 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-ebpf-rootkit-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist


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
---
# Kernel Network Stack Xdp Rootkit Detect
## Overview
This skill covers detection of rootkit security incidents and anomalies on Linux systems. Detect XDP (eXpress Data Path) based rootkits — identify malicious XDP programs attached to network interfaces that silently drop or redirect traffic.
## When to Use
- When investigating or working with rootkit in a kernel-level security investigation context
- When detecting rootkit compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: bpftool net, ip link, /sys/fs/bpf
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-network-stack-xdp-rootkit-detect
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
mcp__cybersec__case_open --title "kernel-network-stack-xdp-rootkit-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

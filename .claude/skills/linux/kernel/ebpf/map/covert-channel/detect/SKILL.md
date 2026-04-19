
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
---
# Kernel Ebpf Map Covert Channel Detect
## Overview
This skill covers detection of covert-channel security incidents and anomalies on Linux systems. Detect eBPF maps used as covert communication channels — identify BPF maps shared between processes for inter-process communication bypassing normal IPC auditing.
## When to Use
- When investigating or working with covert-channel in a kernel-level security investigation context
- When detecting covert-channel compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: bpftool map, bpftool prog, /sys/fs/bpf
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-ebpf-map-covert-channel-detect
```
## Forensic Workflow
1. Identify scope — determine what covert-channel elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| covert-channel indicator | T1071 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-ebpf-map-covert-channel-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

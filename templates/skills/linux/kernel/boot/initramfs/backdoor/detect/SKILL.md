
---
name: kernel-boot-initramfs-backdoor-detect
description: Detect malicious modifications to initramfs/initrd — unpack and inspect early userspace for backdoored binaries, added scripts, or unauthorized kernel modules.
domain: cybersecurity
subdomain: kernel-forensics
tags:
- linux
- initramfs
- initrd
- backdoor
- boot
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1542.003
- T1014
capec: []
---
# Kernel Boot Initramfs Backdoor Detect
## Overview
This skill covers detection of backdoor security incidents and anomalies on Linux systems. Detect malicious modifications to initramfs/initrd — unpack and inspect early userspace for backdoored binaries, added scripts, or unauthorized kernel modules.
## When to Use
- When investigating or working with backdoor in a kernel-level security investigation context
- When detecting backdoor compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: lsinitrd, unmkinitramfs, cpio, binwalk
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-boot-initramfs-backdoor-detect
```
## Forensic Workflow
1. Identify scope — determine what backdoor elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| backdoor indicator | T1542.003 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-boot-initramfs-backdoor-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

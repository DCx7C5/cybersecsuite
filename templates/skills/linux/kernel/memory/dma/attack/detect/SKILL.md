
---
name: kernel-memory-dma-attack-detect
description: Detect Direct Memory Access attacks targeting kernel memory — PCI device enumeration anomalies, IOMMU bypass attempts, and unauthorized DMA-capable device insertion.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- dma
- iommu
- memory
- hardware
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1200
capec: []
---
# Kernel Memory Dma Attack Detect
## Overview
This skill covers detection of attack security incidents and anomalies on Linux systems. Detect Direct Memory Access attacks targeting kernel memory — PCI device enumeration anomalies, IOMMU bypass attempts, and unauthorized DMA-capable device insertion.
## When to Use
- When investigating or working with attack in a kernel-level security investigation context
- When detecting attack compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /sys/bus/pci, iommu groups, /proc/iomem
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-memory-dma-attack-detect
```
## Forensic Workflow
1. Identify scope — determine what attack elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| attack indicator | T1200 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-memory-dma-attack-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

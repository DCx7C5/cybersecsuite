
---
name: supply-chain-shared-library-preload-detect
description: Detect /etc/ld.so.preload backdoors and LD_PRELOAD injection — identify unauthorized entries forcing malicious shared libraries into every process's address space.
domain: cybersecurity
subdomain: supply-chain-security
tags:
- linux
- ld-so-preload
- shared-library
- rootkit
- hijack
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1574.006
- T1014
capec: []
---
# Supply Chain Shared Library Preload Detect
## Overview
This skill covers detection of preload security incidents and anomalies on Linux systems. Detect /etc/ld.so.preload backdoors and LD_PRELOAD injection — identify unauthorized entries forcing malicious shared libraries into every process's address space.
## When to Use
- When investigating or working with preload in a software supply chain security context
- When detecting preload compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /etc/ld.so.preload, ldd, strace, LD_DEBUG=libs
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for supply-chain-shared-library-preload-detect
```
## Forensic Workflow
1. Identify scope — determine what preload elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| preload indicator | T1574.006 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "supply-chain-shared-library-preload-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

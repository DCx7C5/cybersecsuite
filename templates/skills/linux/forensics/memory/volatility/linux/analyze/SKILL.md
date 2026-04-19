
---
name: forensics-memory-volatility-linux-analyze
description: Analyze Linux memory dumps with Volatility3 — enumerate processes, network connections, kernel modules, bash history from memory, and detect in-memory rootkits.
domain: cybersecurity
subdomain: forensic-analysis
tags:
- linux
- volatility
- memory
- forensics
- analyze
nist_csf:
- DE.AE-02
- RS.AN-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1057
- T1014
- T1083
capec: []
---
# Forensics Memory Volatility Linux Analyze
## Overview
This skill provides deep technical analysis capabilities for linux on Linux. Analyze Linux memory dumps with Volatility3 — enumerate processes, network connections, kernel modules, bash history from memory, and detect in-memory rootkits.
## When to Use
- When investigating or working with linux in a Linux forensic investigation context
- When performing deep technical analysis of linux
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: vol3 -f mem.dump linux.pslist, linux.netstat, linux.lsmod, linux.bash
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for forensics-memory-volatility-linux-analyze
```
## Forensic Workflow
1. Identify scope — determine what linux elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| linux indicator | T1057 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "forensics-memory-volatility-linux-analyze" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

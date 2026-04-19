
---
name: supply-chain-package-hook-persist-detect
description: Detect persistence via package manager hooks — identify malicious dpkg/apt pre/post-install hooks, rpm scriptlets, and pacman hooks that execute attacker code on package operations.
domain: cybersecurity
subdomain: supply-chain-security
tags:
- linux
- apt
- dpkg
- rpm
- hook
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1195.002
- T1543
capec: []
---
# Supply Chain Package Hook Persist Detect
## Overview
This skill covers detection of persist security incidents and anomalies on Linux systems. Detect persistence via package manager hooks — identify malicious dpkg/apt pre/post-install hooks, rpm scriptlets, and pacman hooks that execute attacker code on package operations.
## When to Use
- When investigating or working with persist in a software supply chain security context
- When detecting persist compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /etc/apt/apt.conf.d/, /var/lib/dpkg/info/*.postinst, rpm -q --scripts
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for supply-chain-package-hook-persist-detect
```
## Forensic Workflow
1. Identify scope — determine what persist elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| persist indicator | T1195.002 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "supply-chain-package-hook-persist-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

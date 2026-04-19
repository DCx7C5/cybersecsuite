
---
name: supply-chain-package-apt-integrity-verify
description: Verify Debian/Ubuntu package integrity — use debsums to check installed file hashes, validate apt repository GPG signatures, and detect tampered packages.
domain: cybersecurity
subdomain: supply-chain-security
tags:
- linux
- apt
- debian
- package
- integrity
- verify
nist_csf:
- PR.DS-06
- ID.RA-05
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1195.002
capec: []
---
# Supply Chain Package Apt Integrity Verify
## Overview
This skill verifies the integrity and authenticity of integrity. Verify Debian/Ubuntu package integrity — use debsums to check installed file hashes, validate apt repository GPG signatures, and detect tampered packages.
## When to Use
- When investigating or working with integrity in a software supply chain security context
- When verifying integrity of integrity
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: debsums, apt-key, /etc/apt/trusted.gpg.d/, dpkg -V
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for supply-chain-package-apt-integrity-verify
```
## Forensic Workflow
1. Identify scope — determine what integrity elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| integrity indicator | T1195.002 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "supply-chain-package-apt-integrity-verify" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist


---
name: supply-chain-package-rpm-integrity-verify
description: Verify RPM package integrity — use rpm -V to check all installed file attributes, validate GPG signatures, and detect modified system binaries.
domain: cybersecurity
subdomain: supply-chain-security
tags:
- linux
- rpm
- redhat
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
# Supply Chain Package Rpm Integrity Verify
## Overview
This skill verifies the integrity and authenticity of integrity. Verify RPM package integrity — use rpm -V to check all installed file attributes, validate GPG signatures, and detect modified system binaries.
## When to Use
- When investigating or working with integrity in a software supply chain security context
- When verifying integrity of integrity
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: rpm -Va, rpm -K, /etc/pki/rpm-gpg/, rpmdb
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for supply-chain-package-rpm-integrity-verify
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
mcp__cybersec__case_open --title "supply-chain-package-rpm-integrity-verify" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

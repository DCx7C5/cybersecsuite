
---
name: supply-chain-binary-hash-verify
description: Verify system binary integrity via hash comparison — baseline critical binaries (ls, ps, netstat, sshd), detect replacements, and identify trojanized executables.
domain: cybersecurity
subdomain: supply-chain-security
tags:
- linux
- binary
- hash
- integrity
- trojan
- verify
nist_csf:
- PR.DS-06
- ID.RA-05
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1036
- T1195
capec: []
---
# Supply Chain Binary Hash Verify
## Overview
This skill verifies the integrity and authenticity of hash. Verify system binary integrity via hash comparison — baseline critical binaries (ls, ps, netstat, sshd), detect replacements, and identify trojanized executables.
## When to Use
- When investigating or working with hash in a software supply chain security context
- When verifying integrity of hash
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: sha256sum, debsums, rpm -V, aide, tripwire, /usr/bin
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for supply-chain-binary-hash-verify
```
## Forensic Workflow
1. Identify scope — determine what hash elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| hash indicator | T1036 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "supply-chain-binary-hash-verify" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

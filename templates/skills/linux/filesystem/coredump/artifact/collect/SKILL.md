
---
name: filesystem-coredump-artifact-collect
description: Collect and analyze core dump artifacts — configure core dump destinations, extract credentials and sensitive data from process core dumps, detect malicious core dump triggers.
domain: cybersecurity
subdomain: filesystem-forensics
tags:
- linux
- coredump
- core-dump
- artifact
- forensics
nist_csf:
- RS.AN-01
- DE.CM-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1005
capec: []
---
# Filesystem Coredump Artifact Collect
## Overview
This skill covers collection and preservation of artifact artifacts for forensic investigation. Collect and analyze core dump artifacts — configure core dump destinations, extract credentials and sensitive data from process core dumps, detect malicious core dump triggers.
## When to Use
- When investigating or working with artifact in a filesystem forensics context
- When collecting forensic artifacts from artifact
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /proc/sys/kernel/core_pattern, gdb, eu-unstrip, apport
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for filesystem-coredump-artifact-collect
```
## Forensic Workflow
1. Identify scope — determine what artifact elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| artifact indicator | T1005 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "filesystem-coredump-artifact-collect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist


---
name: kernel-modules-signing-verify
description: Verify kernel module signing — check module signatures against trusted keys, detect unsigned or invalidly-signed modules loaded into the kernel.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- lkm
- module
- signing
- integrity
nist_csf:
- PR.DS-06
- ID.RA-05
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1014
- T1195
capec: []
---
# Kernel Modules Signing Verify
## Overview
This skill verifies the integrity and authenticity of signing. Verify kernel module signing — check module signatures against trusted keys, detect unsigned or invalidly-signed modules loaded into the kernel.
## When to Use
- When investigating or working with signing in a kernel-level security investigation context
- When verifying integrity of signing
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: modinfo, /proc/sys/kernel/module_sig_enforce, keyctl
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-modules-signing-verify
```
## Forensic Workflow
1. Identify scope — determine what signing elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| signing indicator | T1014 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-modules-signing-verify" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

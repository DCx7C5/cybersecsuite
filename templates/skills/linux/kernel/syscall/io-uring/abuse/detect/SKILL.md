
---
name: kernel-syscall-io-uring-abuse-detect
description: Detect io_uring syscall interface abuse — identify exploitation of io_uring vulnerabilities (CVE-2022-29582, CVE-2023-2598) and unauthorized use for sandboxed process escape.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- io-uring
- syscall
- exploit
- cve
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []
---
# Kernel Syscall Io Uring Abuse Detect
## Overview
This skill covers detection of abuse security incidents and anomalies on Linux systems. Detect io_uring syscall interface abuse — identify exploitation of io_uring vulnerabilities (CVE-2022-29582, CVE-2023-2598) and unauthorized use for sandboxed process escape.
## When to Use
- When investigating or working with abuse in a kernel-level security investigation context
- When detecting abuse compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: auditd io_uring, seccomp io_uring block, /proc/*/fdinfo
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-syscall-io-uring-abuse-detect
```
## Forensic Workflow
1. Identify scope — determine what abuse elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| abuse indicator | T1068 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-syscall-io-uring-abuse-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

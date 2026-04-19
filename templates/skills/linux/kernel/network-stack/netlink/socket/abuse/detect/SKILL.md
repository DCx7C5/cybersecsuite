
---
name: kernel-network-stack-netlink-socket-abuse-detect
description: Detect Netlink socket privilege abuse — identify processes using Netlink to modify routing, firewall rules, or network interfaces without going through standard tools.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- netlink
- socket
- privilege
- abuse
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1562.004
- T1548
capec: []
---
# Kernel Network Stack Netlink Socket Abuse Detect
## Overview
This skill covers detection of abuse security incidents and anomalies on Linux systems. Detect Netlink socket privilege abuse — identify processes using Netlink to modify routing, firewall rules, or network interfaces without going through standard tools.
## When to Use
- When investigating or working with abuse in a kernel-level security investigation context
- When detecting abuse compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: ss -a, /proc/net/netlink, strace, auditd
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-network-stack-netlink-socket-abuse-detect
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
| abuse indicator | T1562.004 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-network-stack-netlink-socket-abuse-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

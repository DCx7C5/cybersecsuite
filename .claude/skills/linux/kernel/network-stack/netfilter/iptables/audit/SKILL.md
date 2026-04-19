
---
name: kernel-network-stack-netfilter-iptables-audit
description: Forensic audit of iptables rules — enumerate all tables/chains, detect firewall rule tampering, identify rules that allow unauthorized traffic or disable logging.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- iptables
- netfilter
- firewall
- audit
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1562.004
capec: []
---
# Kernel Network Stack Netfilter Iptables Audit
## Overview
This skill audits iptables configuration and security posture on Linux systems. Forensic audit of iptables rules — enumerate all tables/chains, detect firewall rule tampering, identify rules that allow unauthorized traffic or disable logging.
## When to Use
- When investigating or working with iptables in a kernel-level security investigation context
- When reviewing iptables configuration against security standards
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: iptables -L -n -v, iptables-save, auditd
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-network-stack-netfilter-iptables-audit
```
## Forensic Workflow
1. Identify scope — determine what iptables elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| iptables indicator | T1562.004 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-network-stack-netfilter-iptables-audit" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

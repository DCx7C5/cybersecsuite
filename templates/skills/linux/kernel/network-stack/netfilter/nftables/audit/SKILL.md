
---
name: kernel-network-stack-netfilter-nftables-audit
description: Forensic audit of nftables rules — enumerate nft tables/chains/rules, detect unauthorized modifications, and identify rules bypassing security controls.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- nftables
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
# Kernel Network Stack Netfilter Nftables Audit
## Overview
This skill audits nftables configuration and security posture on Linux systems. Forensic audit of nftables rules — enumerate nft tables/chains/rules, detect unauthorized modifications, and identify rules bypassing security controls.
## When to Use
- When investigating or working with nftables in a kernel-level security investigation context
- When reviewing nftables configuration against security standards
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: nft list ruleset, nft monitor, auditd
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-network-stack-netfilter-nftables-audit
```
## Forensic Workflow
1. Identify scope — determine what nftables elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| nftables indicator | T1562.004 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-network-stack-netfilter-nftables-audit" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

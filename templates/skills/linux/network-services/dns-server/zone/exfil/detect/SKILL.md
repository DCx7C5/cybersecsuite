
---
name: network-services-dns-server-zone-exfil-detect
description: Detect DNS zone transfer data exfiltration — identify unauthorized AXFR/IXFR requests, misconfigured BIND allow-transfer ACLs, and DNS zone data as exfiltration vector.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- dns
- bind
- zone-transfer
- exfil
- detect
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1048
- T1590.002
capec: []
---
# Network Services Dns Server Zone Exfil Detect
## Overview
This skill covers detection of exfil security incidents and anomalies on Linux systems. Detect DNS zone transfer data exfiltration — identify unauthorized AXFR/IXFR requests, misconfigured BIND allow-transfer ACLs, and DNS zone data as exfiltration vector.
## When to Use
- When investigating or working with exfil in a Linux network service security context
- When detecting exfil compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: dig AXFR, /etc/bind/named.conf, allow-transfer, tcpdump port 53
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for network-services-dns-server-zone-exfil-detect
```
## Forensic Workflow
1. Identify scope — determine what exfil elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| exfil indicator | T1048 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "network-services-dns-server-zone-exfil-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

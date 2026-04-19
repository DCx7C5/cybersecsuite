
---
name: network-services-apache-config-audit
description: Security audit of Apache httpd configuration — review ServerTokens, directory indexing, mod_status exposure, .htaccess risks, and SSL/TLS configuration weaknesses.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- apache
- httpd
- web
- configuration
- audit
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1190
- T1083
capec: []
---
# Network Services Apache Config Audit
## Overview
This skill audits config configuration and security posture on Linux systems. Security audit of Apache httpd configuration — review ServerTokens, directory indexing, mod_status exposure, .htaccess risks, and SSL/TLS configuration weaknesses.
## When to Use
- When investigating or working with config in a Linux network service security context
- When reviewing config configuration against security standards
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: apachectl -S, /etc/apache2/apache2.conf, ServerTokens, mod_status
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for network-services-apache-config-audit
```
## Forensic Workflow
1. Identify scope — determine what config elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| config indicator | T1190 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "network-services-apache-config-audit" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist

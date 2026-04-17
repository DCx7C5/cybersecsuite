---
name: performing-dns-enumeration-and-zone-transfer
description: "'Enumerates DNS records, attempts zone transfers, brute-forces subdomains, and maps DNS infrastructure during"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-dns-enumeration-and-zone-transfer/SKILL.md"
---
# Performing Dns Enumeration And Zone Transfer

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-dns-enumeration-and-zone-transfer/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-dns-enumeration-and-zone-transfer", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-dns-enumeration-and-zone-transfer")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@network-security-analyst` or `@cybersec-agent`

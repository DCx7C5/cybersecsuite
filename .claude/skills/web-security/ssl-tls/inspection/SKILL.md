---
name: performing-ssl-tls-inspection-configuration
description: "Configure SSL/TLS inspection on network security devices to decrypt, inspect, and re-encrypt HTTPS traffic for"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-ssl-tls-inspection-configuration/SKILL.md"
---
# Performing Ssl Tls Inspection Configuration

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-ssl-tls-inspection-configuration/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-ssl-tls-inspection-configuration", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-ssl-tls-inspection-configuration")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@network-security-analyst` or `@cybersec-agent`

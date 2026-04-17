---
name: performing-web-application-firewall-bypass
description: "Bypass Web Application Firewall protections using encoding techniques, HTTP method manipulation, parameter pollution,"
domain: cybersecurity
subdomain: web-application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-web-application-firewall-bypass/SKILL.md"
---
# Performing Web Application Firewall Bypass

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-web-application-firewall-bypass/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-web-application-firewall-bypass", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-web-application-firewall-bypass")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@web-application-security-analyst` or `@cybersec-agent`

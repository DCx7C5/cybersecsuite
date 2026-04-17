---
name: performing-subdomain-enumeration-with-subfinder
description: "Enumerate subdomains of target domains using ProjectDiscovery's Subfinder passive reconnaissance tool to map"
domain: cybersecurity
subdomain: web-application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-subdomain-enumeration-with-subfinder/SKILL.md"
---
# Performing Subdomain Enumeration With Subfinder

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-subdomain-enumeration-with-subfinder/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-subdomain-enumeration-with-subfinder", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-subdomain-enumeration-with-subfinder")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@web-application-security-analyst` or `@cybersec-agent`

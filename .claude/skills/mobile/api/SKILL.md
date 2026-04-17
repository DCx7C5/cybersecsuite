---
name: testing-mobile-api-authentication
description: "'Tests authentication and authorization mechanisms in mobile application APIs to identify broken authentication,"
domain: cybersecurity
subdomain: mobile-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-mobile-api-authentication/SKILL.md"
---
# Testing Mobile Api Authentication

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-mobile-api-authentication/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="testing-mobile-api-authentication", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="testing-mobile-api-authentication")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@mobile-security-analyst` or `@cybersec-agent`

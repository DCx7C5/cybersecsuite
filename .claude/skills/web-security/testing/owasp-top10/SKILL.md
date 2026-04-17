---
name: testing-api-security-with-owasp-top-10
description: "Systematically assessing REST and GraphQL API endpoints against the OWASP API Security Top 10 risks using automated"
domain: cybersecurity
subdomain: web-application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-api-security-with-owasp-top-10/SKILL.md"
---
# Testing Api Security With Owasp Top 10

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-api-security-with-owasp-top-10/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="testing-api-security-with-owasp-top-10", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="testing-api-security-with-owasp-top-10")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@web-application-security-analyst` or `@cybersec-agent`

---
name: testing-for-json-web-token-vulnerabilities
description: "Test JWT implementations for critical vulnerabilities including algorithm confusion, none algorithm bypass, kid"
domain: cybersecurity
subdomain: web-application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-for-json-web-token-vulnerabilities/SKILL.md"
---
# Testing For Json Web Token Vulnerabilities

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-for-json-web-token-vulnerabilities/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="testing-for-json-web-token-vulnerabilities", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="testing-for-json-web-token-vulnerabilities")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@web-application-security-analyst` or `@cybersec-agent`

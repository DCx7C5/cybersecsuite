---
name: testing-for-xxe-injection-vulnerabilities
description: "Discovering and exploiting XML External Entity injection vulnerabilities to read server files, perform SSRF,"
domain: cybersecurity
subdomain: web-application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-for-xxe-injection-vulnerabilities/SKILL.md"
---
# Testing For Xxe Injection Vulnerabilities

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-for-xxe-injection-vulnerabilities/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="testing-for-xxe-injection-vulnerabilities", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="testing-for-xxe-injection-vulnerabilities")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@web-application-security-analyst` or `@cybersec-agent`

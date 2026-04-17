---
name: testing-for-xss-vulnerabilities
description: "'Tests web applications for Cross-Site Scripting (XSS) vulnerabilities by injecting JavaScript payloads into"
domain: cybersecurity
subdomain: penetration-testing
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-for-xss-vulnerabilities/SKILL.md"
---
# Testing For Xss Vulnerabilities

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-for-xss-vulnerabilities/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="testing-for-xss-vulnerabilities", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="testing-for-xss-vulnerabilities")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@penetration-testing-analyst` or `@cybersec-agent`

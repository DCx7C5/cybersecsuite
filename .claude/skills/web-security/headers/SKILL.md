---
name: performing-security-headers-audit
description: "Auditing HTTP security headers including CSP, HSTS, X-Frame-Options, and cookie attributes to identify missing"
domain: cybersecurity
subdomain: web-application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-security-headers-audit/SKILL.md"
---
# Performing Security Headers Audit

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-security-headers-audit/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-security-headers-audit", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-security-headers-audit")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@web-application-security-analyst` or `@cybersec-agent`

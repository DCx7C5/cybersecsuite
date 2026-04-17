---
name: performing-paste-site-monitoring-for-credentials
description: "Monitor paste sites like Pastebin and GitHub Gists for leaked credentials, API keys, and sensitive data dumps"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-paste-site-monitoring-for-credentials/SKILL.md"
---
# Performing Paste Site Monitoring For Credentials

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-paste-site-monitoring-for-credentials/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-paste-site-monitoring-for-credentials", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-paste-site-monitoring-for-credentials")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@threat-intelligence-analyst` or `@cybersec-agent`

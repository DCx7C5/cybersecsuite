---
name: performing-web-cache-poisoning-attack
description: "Exploiting web cache mechanisms to serve malicious content to other users by poisoning cached responses through"
domain: cybersecurity
subdomain: web-application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-web-cache-poisoning-attack/SKILL.md"
---
# Performing Web Cache Poisoning Attack

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-web-cache-poisoning-attack/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-web-cache-poisoning-attack", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-web-cache-poisoning-attack")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@web-application-security-analyst` or `@cybersec-agent`

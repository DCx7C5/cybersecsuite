---
name: performing-jwt-none-algorithm-attack
description: "Execute and test the JWT none algorithm attack to bypass signature verification by manipulating the alg header"
domain: cybersecurity
subdomain: api-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-jwt-none-algorithm-attack/SKILL.md"
---
# Performing Jwt None Algorithm Attack

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-jwt-none-algorithm-attack/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-jwt-none-algorithm-attack", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-jwt-none-algorithm-attack")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@api-security-analyst` or `@cybersec-agent`

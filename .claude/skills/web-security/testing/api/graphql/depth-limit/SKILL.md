---
name: performing-graphql-depth-limit-attack
description: "Execute and test GraphQL depth limit attacks using deeply nested recursive queries to identify denial-of-service"
domain: cybersecurity
subdomain: api-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-graphql-depth-limit-attack/SKILL.md"
---
# Performing Graphql Depth Limit Attack

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-graphql-depth-limit-attack/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-graphql-depth-limit-attack", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-graphql-depth-limit-attack")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@api-security-analyst` or `@cybersec-agent`

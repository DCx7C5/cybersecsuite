---
name: deploying-palo-alto-prisma-access-zero-trust
description: "'Deploying Palo Alto Networks Prisma Access for SASE-based zero trust network access using GlobalProtect agents,"
domain: cybersecurity
subdomain: zero-trust-architecture
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-palo-alto-prisma-access-zero-trust/SKILL.md"
---
# Deploying Palo Alto Prisma Access Zero Trust

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-palo-alto-prisma-access-zero-trust/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="deploying-palo-alto-prisma-access-zero-trust", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="deploying-palo-alto-prisma-access-zero-trust")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@zero-trust-architecture-analyst` or `@cybersec-agent`

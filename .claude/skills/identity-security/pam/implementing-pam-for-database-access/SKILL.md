---
name: implementing-pam-for-database-access
description: "Deploy privileged access management for database systems including Oracle, SQL Server, PostgreSQL, and MySQL."
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-pam-for-database-access/SKILL.md"
---
# Implementing Pam For Database Access

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-pam-for-database-access/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-pam-for-database-access", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-pam-for-database-access")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

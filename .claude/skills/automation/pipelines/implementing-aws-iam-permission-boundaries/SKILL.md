---
name: implementing-aws-iam-permission-boundaries
description: "Configure IAM permission boundaries in AWS to delegate role creation to developers while enforcing maximum privilege"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-aws-iam-permission-boundaries/SKILL.md"
---
# Implementing Aws Iam Permission Boundaries

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-aws-iam-permission-boundaries/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-aws-iam-permission-boundaries", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-aws-iam-permission-boundaries")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

---
name: implementing-identity-governance-with-sailpoint
description: "Deploy SailPoint IdentityNow or IdentityIQ for identity governance and administration. Covers identity lifecycle"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-identity-governance-with-sailpoint/SKILL.md"
---
# Implementing Identity Governance With Sailpoint

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-identity-governance-with-sailpoint/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-identity-governance-with-sailpoint", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-identity-governance-with-sailpoint")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

---
name: performing-entitlement-review-with-sailpoint-iiq
description: "'Performs entitlement review and access certification campaigns using SailPoint IdentityIQ including manager"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-entitlement-review-with-sailpoint-iiq/SKILL.md"
---
# Performing Entitlement Review With Sailpoint Iiq

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-entitlement-review-with-sailpoint-iiq/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-entitlement-review-with-sailpoint-iiq", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-entitlement-review-with-sailpoint-iiq")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

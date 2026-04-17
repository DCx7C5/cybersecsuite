---
name: building-role-mining-for-rbac-optimization
description: "Apply bottom-up and top-down role mining techniques to discover optimal RBAC roles from existing user-permission"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-role-mining-for-rbac-optimization/SKILL.md"
---
# Building Role Mining For Rbac Optimization

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-role-mining-for-rbac-optimization/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="building-role-mining-for-rbac-optimization", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-role-mining-for-rbac-optimization")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

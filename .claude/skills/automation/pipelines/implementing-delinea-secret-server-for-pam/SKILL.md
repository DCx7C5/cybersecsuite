---
name: implementing-delinea-secret-server-for-pam
description: "'Implements Delinea Secret Server for privileged access management (PAM) including secret vault configuration,"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-delinea-secret-server-for-pam/SKILL.md"
---
# Implementing Delinea Secret Server For Pam

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-delinea-secret-server-for-pam/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-delinea-secret-server-for-pam", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-delinea-secret-server-for-pam")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

---
name: implementing-passwordless-auth-with-microsoft-entra
description: "'Implements passwordless authentication using Microsoft Entra ID with FIDO2 security keys, Windows Hello for"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-passwordless-auth-with-microsoft-entra/SKILL.md"
---
# Implementing Passwordless Auth With Microsoft Entra

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-passwordless-auth-with-microsoft-entra/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-passwordless-auth-with-microsoft-entra", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-passwordless-auth-with-microsoft-entra")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

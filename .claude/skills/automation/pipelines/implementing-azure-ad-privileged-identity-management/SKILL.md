---
name: implementing-azure-ad-privileged-identity-management
description: "Configure Microsoft Entra Privileged Identity Management to enforce just-in-time role activation, approval workflows,"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-azure-ad-privileged-identity-management/SKILL.md"
---
# Implementing Azure Ad Privileged Identity Management

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-azure-ad-privileged-identity-management/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-azure-ad-privileged-identity-management", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-azure-ad-privileged-identity-management")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

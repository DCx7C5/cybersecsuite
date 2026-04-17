---
name: implementing-privileged-access-workstation
description: "Design and implement Privileged Access Workstations (PAWs) with device hardening, just-in-time access, and integration"
domain: cybersecurity
subdomain: identity-and-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-privileged-access-workstation/SKILL.md"
---
# Implementing Privileged Access Workstation

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-privileged-access-workstation/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-privileged-access-workstation", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-privileged-access-workstation")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

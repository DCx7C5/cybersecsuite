---
name: securing-remote-access-to-ot-environment
description: "'This skill covers implementing secure remote access to OT/ICS environments for operators, engineers, and vendors"
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/securing-remote-access-to-ot-environment/SKILL.md"
---
# Securing Remote Access To Ot Environment

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/securing-remote-access-to-ot-environment/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="securing-remote-access-to-ot-environment", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="securing-remote-access-to-ot-environment")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

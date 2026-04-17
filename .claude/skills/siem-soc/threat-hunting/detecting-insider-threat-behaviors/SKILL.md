---
name: detecting-insider-threat-behaviors
description: "Detect insider threat behavioral indicators including unusual data access, off-hours activity, mass file downloads,"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-insider-threat-behaviors/SKILL.md"
---
# Detecting Insider Threat Behaviors

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-insider-threat-behaviors/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-insider-threat-behaviors", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-insider-threat-behaviors")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

---
name: hunting-for-persistence-via-wmi-subscriptions
description: "Hunt for adversary persistence through Windows Management Instrumentation event subscriptions by monitoring WMI"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hunting-for-persistence-via-wmi-subscriptions/SKILL.md"
---
# Hunting For Persistence Via Wmi Subscriptions

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hunting-for-persistence-via-wmi-subscriptions/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="hunting-for-persistence-via-wmi-subscriptions", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="hunting-for-persistence-via-wmi-subscriptions")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

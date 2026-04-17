---
name: detecting-wmi-persistence
description: "Detect WMI event subscription persistence by analyzing Sysmon Event IDs 19, 20, and 21 for malicious EventFilter,"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-wmi-persistence/SKILL.md"
---
# Detecting Wmi Persistence

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-wmi-persistence/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-wmi-persistence", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-wmi-persistence")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

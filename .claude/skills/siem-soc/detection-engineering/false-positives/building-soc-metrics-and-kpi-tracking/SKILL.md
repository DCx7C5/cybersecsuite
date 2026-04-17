---
name: building-soc-metrics-and-kpi-tracking
description: "'Builds SOC performance metrics and KPI tracking dashboards measuring Mean Time to Detect (MTTD), Mean Time to"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-soc-metrics-and-kpi-tracking/SKILL.md"
---
# Building Soc Metrics And Kpi Tracking

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-soc-metrics-and-kpi-tracking/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="building-soc-metrics-and-kpi-tracking", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-soc-metrics-and-kpi-tracking")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

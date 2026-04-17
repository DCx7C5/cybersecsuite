---
name: detecting-anomalies-in-industrial-control-systems
description: "'This skill covers deploying anomaly detection systems for industrial control environments using machine learning"
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-anomalies-in-industrial-control-systems/SKILL.md"
---
# Detecting Anomalies In Industrial Control Systems

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-anomalies-in-industrial-control-systems/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-anomalies-in-industrial-control-systems", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-anomalies-in-industrial-control-systems")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

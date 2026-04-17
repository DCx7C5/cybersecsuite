---
name: detecting-modbus-protocol-anomalies
description: "'This skill covers detecting anomalies in Modbus/TCP and Modbus RTU communications in industrial control systems."
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-modbus-protocol-anomalies/SKILL.md"
---
# Detecting Modbus Protocol Anomalies

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-modbus-protocol-anomalies/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-modbus-protocol-anomalies", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-modbus-protocol-anomalies")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

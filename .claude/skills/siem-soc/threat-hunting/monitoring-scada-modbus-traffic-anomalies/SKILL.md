---
name: monitoring-scada-modbus-traffic-anomalies
description: "'Monitors Modbus TCP traffic on SCADA and ICS networks to detect anomalous function code usage, unauthorized"
domain: cybersecurity
subdomain: ot-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/monitoring-scada-modbus-traffic-anomalies/SKILL.md"
---
# Monitoring Scada Modbus Traffic Anomalies

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/monitoring-scada-modbus-traffic-anomalies/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="monitoring-scada-modbus-traffic-anomalies", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="monitoring-scada-modbus-traffic-anomalies")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

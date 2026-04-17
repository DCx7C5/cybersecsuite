---
name: detecting-network-anomalies-with-zeek
description: "'Deploys and configures Zeek (formerly Bro) network security monitor to passively analyze network traffic, generate"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-network-anomalies-with-zeek/SKILL.md"
---
# Detecting Network Anomalies With Zeek

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-network-anomalies-with-zeek/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-network-anomalies-with-zeek", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-network-anomalies-with-zeek")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

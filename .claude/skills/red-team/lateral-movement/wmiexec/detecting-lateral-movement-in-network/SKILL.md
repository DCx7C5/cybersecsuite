---
name: detecting-lateral-movement-in-network
description: "'Identifies lateral movement techniques in enterprise networks by analyzing authentication logs, network flows,"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-lateral-movement-in-network/SKILL.md"
---
# Detecting Lateral Movement In Network

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-lateral-movement-in-network/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-lateral-movement-in-network", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-lateral-movement-in-network")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

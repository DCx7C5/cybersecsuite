---
name: detecting-lateral-movement-with-zeek
description: "'Detect lateral movement in network traffic using Zeek (formerly Bro) log analysis. Parses conn.log, smb_mapping.log,"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-lateral-movement-with-zeek/SKILL.md"
---
# Detecting Lateral Movement With Zeek

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-lateral-movement-with-zeek/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-lateral-movement-with-zeek", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-lateral-movement-with-zeek")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

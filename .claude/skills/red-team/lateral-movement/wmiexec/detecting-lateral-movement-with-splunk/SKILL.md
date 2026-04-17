---
name: detecting-lateral-movement-with-splunk
description: "Detect adversary lateral movement across networks using Splunk SPL queries against Windows authentication logs,"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-lateral-movement-with-splunk/SKILL.md"
---
# Detecting Lateral Movement With Splunk

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-lateral-movement-with-splunk/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-lateral-movement-with-splunk", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-lateral-movement-with-splunk")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

---
name: hunting-for-lolbins-execution-in-endpoint-logs
description: "Hunt for adversary abuse of Living Off the Land Binaries (LOLBins) by analyzing endpoint process creation logs"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hunting-for-lolbins-execution-in-endpoint-logs/SKILL.md"
---
# Hunting For Lolbins Execution In Endpoint Logs

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hunting-for-lolbins-execution-in-endpoint-logs/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="hunting-for-lolbins-execution-in-endpoint-logs", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="hunting-for-lolbins-execution-in-endpoint-logs")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

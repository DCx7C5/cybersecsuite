---
name: detecting-evasion-techniques-in-endpoint-logs
description: "'Detects defense evasion techniques used by adversaries in endpoint logs including log tampering, timestomping,"
domain: cybersecurity
subdomain: endpoint-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-evasion-techniques-in-endpoint-logs/SKILL.md"
---
# Detecting Evasion Techniques In Endpoint Logs

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-evasion-techniques-in-endpoint-logs/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-evasion-techniques-in-endpoint-logs", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-evasion-techniques-in-endpoint-logs")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

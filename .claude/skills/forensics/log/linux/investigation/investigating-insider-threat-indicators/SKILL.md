---
name: investigating-insider-threat-indicators
description: "'Investigates insider threat indicators including data exfiltration attempts, unauthorized access patterns, policy"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/investigating-insider-threat-indicators/SKILL.md"
---
# Investigating Insider Threat Indicators

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/investigating-insider-threat-indicators/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="investigating-insider-threat-indicators", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="investigating-insider-threat-indicators")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

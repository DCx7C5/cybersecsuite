---
name: detecting-stuxnet-style-attacks
description: "'This skill covers detecting sophisticated cyber-physical attacks that follow the Stuxnet attack pattern of modifying"
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-stuxnet-style-attacks/SKILL.md"
---
# Detecting Stuxnet Style Attacks

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-stuxnet-style-attacks/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-stuxnet-style-attacks", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-stuxnet-style-attacks")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

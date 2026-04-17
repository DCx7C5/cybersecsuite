---
name: detecting-privilege-escalation-attempts
description: "Detect privilege escalation attempts including token manipulation, UAC bypass, unquoted service paths, kernel"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-privilege-escalation-attempts/SKILL.md"
---
# Detecting Privilege Escalation Attempts

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-privilege-escalation-attempts/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-privilege-escalation-attempts", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-privilege-escalation-attempts")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

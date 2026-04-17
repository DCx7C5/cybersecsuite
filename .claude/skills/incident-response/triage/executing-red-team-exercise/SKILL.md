---
name: executing-red-team-exercise
description: "'Executes comprehensive red team exercises that simulate real-world adversary operations against an organization''s"
domain: cybersecurity
subdomain: penetration-testing
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/executing-red-team-exercise/SKILL.md"
---
# Executing Red Team Exercise

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/executing-red-team-exercise/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="executing-red-team-exercise", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="executing-red-team-exercise")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

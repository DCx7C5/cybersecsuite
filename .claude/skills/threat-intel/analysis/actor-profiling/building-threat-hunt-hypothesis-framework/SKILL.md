---
name: building-threat-hunt-hypothesis-framework
description: "Build a systematic threat hunt hypothesis framework that transforms threat intelligence, attack patterns, and"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-threat-hunt-hypothesis-framework/SKILL.md"
---
# Building Threat Hunt Hypothesis Framework

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-threat-hunt-hypothesis-framework/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="building-threat-hunt-hypothesis-framework", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-threat-hunt-hypothesis-framework")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

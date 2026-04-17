---
name: building-soc-escalation-matrix
description: "Build a structured SOC escalation matrix defining severity tiers, response SLAs, escalation paths, and notification"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-soc-escalation-matrix/SKILL.md"
---
# Building Soc Escalation Matrix

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-soc-escalation-matrix/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="building-soc-escalation-matrix", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-soc-escalation-matrix")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

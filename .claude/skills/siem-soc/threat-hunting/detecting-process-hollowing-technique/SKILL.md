---
name: detecting-process-hollowing-technique
description: "Detect process hollowing (T1055.012) by analyzing memory-mapped sections, hollowed process indicators, and parent-child"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-process-hollowing-technique/SKILL.md"
---
# Detecting Process Hollowing Technique

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-process-hollowing-technique/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-process-hollowing-technique", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-process-hollowing-technique")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

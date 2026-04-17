---
name: implementing-threat-intelligence-lifecycle-management
description: "Implement a structured threat intelligence lifecycle encompassing planning, collection, processing, analysis,"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-threat-intelligence-lifecycle-management/SKILL.md"
---
# Implementing Threat Intelligence Lifecycle Management

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-threat-intelligence-lifecycle-management/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-threat-intelligence-lifecycle-management", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-threat-intelligence-lifecycle-management")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

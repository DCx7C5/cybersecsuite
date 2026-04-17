---
name: building-threat-intelligence-platform
description: "Building a Threat Intelligence Platform (TIP) involves deploying and integrating multiple CTI tools into a unified"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-threat-intelligence-platform/SKILL.md"
---
# Building Threat Intelligence Platform

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-threat-intelligence-platform/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="building-threat-intelligence-platform", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-threat-intelligence-platform")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

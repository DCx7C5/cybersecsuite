---
name: evaluating-threat-intelligence-platforms
description: "'Evaluates and selects Threat Intelligence Platform (TIP) products based on organizational requirements including"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/evaluating-threat-intelligence-platforms/SKILL.md"
---
# Evaluating Threat Intelligence Platforms

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/evaluating-threat-intelligence-platforms/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="evaluating-threat-intelligence-platforms", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="evaluating-threat-intelligence-platforms")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

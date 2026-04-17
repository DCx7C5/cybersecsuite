---
name: implementing-diamond-model-analysis
description: "The Diamond Model of Intrusion Analysis provides a structured framework for analyzing cyber intrusions by examining"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-diamond-model-analysis/SKILL.md"
---
# Implementing Diamond Model Analysis

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-diamond-model-analysis/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-diamond-model-analysis", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-diamond-model-analysis")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

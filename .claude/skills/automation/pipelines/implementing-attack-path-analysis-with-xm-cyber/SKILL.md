---
name: implementing-attack-path-analysis-with-xm-cyber
description: "Deploy XM Cyber's continuous exposure management platform to map attack paths, identify choke points, and prioritize"
domain: cybersecurity
subdomain: vulnerability-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-attack-path-analysis-with-xm-cyber/SKILL.md"
---
# Implementing Attack Path Analysis With Xm Cyber

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-attack-path-analysis-with-xm-cyber/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-attack-path-analysis-with-xm-cyber", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-attack-path-analysis-with-xm-cyber")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

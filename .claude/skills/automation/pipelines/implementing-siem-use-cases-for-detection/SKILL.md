---
name: implementing-siem-use-cases-for-detection
description: "'Implements SIEM detection use cases by designing correlation rules, threshold alerts, and behavioral analytics"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-siem-use-cases-for-detection/SKILL.md"
---
# Implementing Siem Use Cases For Detection

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-siem-use-cases-for-detection/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-siem-use-cases-for-detection", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-siem-use-cases-for-detection")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

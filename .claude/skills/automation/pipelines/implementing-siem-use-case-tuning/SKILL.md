---
name: implementing-siem-use-case-tuning
description: "Tune SIEM detection rules to reduce false positives by analyzing alert volumes, creating whitelists, adjusting"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-siem-use-case-tuning/SKILL.md"
---
# Implementing Siem Use Case Tuning

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-siem-use-case-tuning/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-siem-use-case-tuning", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-siem-use-case-tuning")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

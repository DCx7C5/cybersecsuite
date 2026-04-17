---
name: detecting-spearphishing-with-email-gateway
description: "Spearphishing targets specific individuals using personalized, researched content that bypasses generic spam"
domain: cybersecurity
subdomain: phishing-defense
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-spearphishing-with-email-gateway/SKILL.md"
---
# Detecting Spearphishing With Email Gateway

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-spearphishing-with-email-gateway/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-spearphishing-with-email-gateway", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-spearphishing-with-email-gateway")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

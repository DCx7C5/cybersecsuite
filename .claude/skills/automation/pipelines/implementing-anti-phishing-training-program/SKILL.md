---
name: implementing-anti-phishing-training-program
description: "Security awareness training is the human layer of phishing defense. An effective anti-phishing training program"
domain: cybersecurity
subdomain: phishing-defense
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-anti-phishing-training-program/SKILL.md"
---
# Implementing Anti Phishing Training Program

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-anti-phishing-training-program/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-anti-phishing-training-program", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-anti-phishing-training-program")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

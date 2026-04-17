---
name: implementing-gdpr-data-protection-controls
description: "The General Data Protection Regulation (EU) 2016/679 (GDPR) is the EU's comprehensive data protection law governing"
domain: cybersecurity
subdomain: compliance-governance
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-gdpr-data-protection-controls/SKILL.md"
---
# Implementing Gdpr Data Protection Controls

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-gdpr-data-protection-controls/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-gdpr-data-protection-controls", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-gdpr-data-protection-controls")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

---
name: building-phishing-reporting-button-workflow
description: "Implement a phishing report button in email clients with automated triage workflow that analyzes user-reported"
domain: cybersecurity
subdomain: phishing-defense
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-phishing-reporting-button-workflow/SKILL.md"
---
# Building Phishing Reporting Button Workflow

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-phishing-reporting-button-workflow/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="building-phishing-reporting-button-workflow", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-phishing-reporting-button-workflow")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

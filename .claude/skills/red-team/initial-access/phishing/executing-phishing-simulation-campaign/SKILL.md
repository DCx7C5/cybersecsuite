---
name: executing-phishing-simulation-campaign
description: "'Executes authorized phishing simulation campaigns to assess an organization''s susceptibility to email-based"
domain: cybersecurity
subdomain: penetration-testing
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/executing-phishing-simulation-campaign/SKILL.md"
---
# Executing Phishing Simulation Campaign

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/executing-phishing-simulation-campaign/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="executing-phishing-simulation-campaign", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="executing-phishing-simulation-campaign")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

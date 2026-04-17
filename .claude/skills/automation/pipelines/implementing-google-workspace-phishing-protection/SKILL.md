---
name: implementing-google-workspace-phishing-protection
description: "Configure Google Workspace advanced phishing and malware protection settings including pre-delivery scanning,"
domain: cybersecurity
subdomain: phishing-defense
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-google-workspace-phishing-protection/SKILL.md"
---
# Implementing Google Workspace Phishing Protection

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-google-workspace-phishing-protection/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-google-workspace-phishing-protection", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-google-workspace-phishing-protection")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

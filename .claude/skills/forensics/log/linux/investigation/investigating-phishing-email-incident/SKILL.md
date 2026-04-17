---
name: investigating-phishing-email-incident
description: "'Investigates phishing email incidents from initial user report through header analysis, URL/attachment detonation,"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/investigating-phishing-email-incident/SKILL.md"
---
# Investigating Phishing Email Incident

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/investigating-phishing-email-incident/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="investigating-phishing-email-incident", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="investigating-phishing-email-incident")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

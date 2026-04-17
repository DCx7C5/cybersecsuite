---
name: performing-alert-triage-with-elastic-siem
description: "Perform systematic alert triage in Elastic Security SIEM to rapidly classify, prioritize, and investigate security"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-alert-triage-with-elastic-siem/SKILL.md"
---
# Performing Alert Triage With Elastic Siem

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-alert-triage-with-elastic-siem/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-alert-triage-with-elastic-siem", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-alert-triage-with-elastic-siem")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

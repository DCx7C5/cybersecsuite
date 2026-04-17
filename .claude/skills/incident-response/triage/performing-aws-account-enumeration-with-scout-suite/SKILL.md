---
name: performing-aws-account-enumeration-with-scout-suite
description: "Perform comprehensive security posture assessment of AWS accounts using ScoutSuite to enumerate resources, identify"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-aws-account-enumeration-with-scout-suite/SKILL.md"
---
# Performing Aws Account Enumeration With Scout Suite

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-aws-account-enumeration-with-scout-suite/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-aws-account-enumeration-with-scout-suite", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-aws-account-enumeration-with-scout-suite")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

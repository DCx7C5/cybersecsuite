---
name: detecting-compromised-cloud-credentials
description: "'Detecting compromised cloud credentials across AWS, Azure, and GCP by analyzing anomalous API activity, impossible"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-compromised-cloud-credentials/SKILL.md"
---
# Detecting Compromised Cloud Credentials

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-compromised-cloud-credentials/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-compromised-cloud-credentials", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-compromised-cloud-credentials")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

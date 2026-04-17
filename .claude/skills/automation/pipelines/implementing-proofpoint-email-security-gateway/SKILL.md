---
name: implementing-proofpoint-email-security-gateway
description: "Deploy and configure Proofpoint Email Protection as a secure email gateway to detect and block phishing, malware,"
domain: cybersecurity
subdomain: phishing-defense
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-proofpoint-email-security-gateway/SKILL.md"
---
# Implementing Proofpoint Email Security Gateway

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-proofpoint-email-security-gateway/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-proofpoint-email-security-gateway", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-proofpoint-email-security-gateway")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

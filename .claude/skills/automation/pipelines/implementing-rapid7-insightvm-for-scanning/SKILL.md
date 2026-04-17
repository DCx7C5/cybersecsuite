---
name: implementing-rapid7-insightvm-for-scanning
description: "Deploy and configure Rapid7 InsightVM Security Console and Scan Engines for authenticated and unauthenticated"
domain: cybersecurity
subdomain: vulnerability-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-rapid7-insightvm-for-scanning/SKILL.md"
---
# Implementing Rapid7 Insightvm For Scanning

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-rapid7-insightvm-for-scanning/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-rapid7-insightvm-for-scanning", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-rapid7-insightvm-for-scanning")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

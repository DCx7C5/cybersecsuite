---
name: implementing-api-abuse-detection-with-rate-limiting
description: "Implement API abuse detection using token bucket, sliding window, and adaptive rate limiting algorithms to prevent"
domain: cybersecurity
subdomain: api-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-api-abuse-detection-with-rate-limiting/SKILL.md"
---
# Implementing Api Abuse Detection With Rate Limiting

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-api-abuse-detection-with-rate-limiting/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-api-abuse-detection-with-rate-limiting", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-api-abuse-detection-with-rate-limiting")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

---
name: implementing-api-rate-limiting-and-throttling
description: "'Implements API rate limiting and throttling controls using token bucket, sliding window, and fixed window algorithms"
domain: cybersecurity
subdomain: api-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-api-rate-limiting-and-throttling/SKILL.md"
---
# Implementing Api Rate Limiting And Throttling

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-api-rate-limiting-and-throttling/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-api-rate-limiting-and-throttling", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-api-rate-limiting-and-throttling")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

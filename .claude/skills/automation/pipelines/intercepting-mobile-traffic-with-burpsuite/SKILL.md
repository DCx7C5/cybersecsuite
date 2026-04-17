---
name: intercepting-mobile-traffic-with-burpsuite
description: "'Intercepts and analyzes HTTP/HTTPS traffic from mobile applications using Burp Suite proxy to identify insecure"
domain: cybersecurity
subdomain: mobile-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/intercepting-mobile-traffic-with-burpsuite/SKILL.md"
---
# Intercepting Mobile Traffic With Burpsuite

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/intercepting-mobile-traffic-with-burpsuite/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="intercepting-mobile-traffic-with-burpsuite", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="intercepting-mobile-traffic-with-burpsuite")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

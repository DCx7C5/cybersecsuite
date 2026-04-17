---
name: implementing-deception-based-detection-with-canarytoken
description: "Deploy and monitor Canary Tokens via the Thinkst Canary API for deception-based breach detection using web bug"
domain: cybersecurity
subdomain: deception-technology
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-deception-based-detection-with-canarytoken/SKILL.md"
---
# Implementing Deception Based Detection With Canarytoken

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-deception-based-detection-with-canarytoken/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-deception-based-detection-with-canarytoken", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-deception-based-detection-with-canarytoken")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

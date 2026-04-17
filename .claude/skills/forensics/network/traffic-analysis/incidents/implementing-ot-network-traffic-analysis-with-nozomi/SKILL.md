---
name: implementing-ot-network-traffic-analysis-with-nozomi
description: "'Deploy Nozomi Networks Guardian sensors for passive OT network traffic analysis to achieve comprehensive asset"
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-ot-network-traffic-analysis-with-nozomi/SKILL.md"
---
# Implementing Ot Network Traffic Analysis With Nozomi

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-ot-network-traffic-analysis-with-nozomi/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-ot-network-traffic-analysis-with-nozomi", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-ot-network-traffic-analysis-with-nozomi")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

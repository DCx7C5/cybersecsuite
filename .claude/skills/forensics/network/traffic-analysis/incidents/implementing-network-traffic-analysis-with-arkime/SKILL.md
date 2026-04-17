---
name: implementing-network-traffic-analysis-with-arkime
description: "Deploy and query Arkime (formerly Moloch) for full packet capture network traffic analysis. Uses the Arkime API"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-network-traffic-analysis-with-arkime/SKILL.md"
---
# Implementing Network Traffic Analysis With Arkime

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-network-traffic-analysis-with-arkime/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-network-traffic-analysis-with-arkime", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-network-traffic-analysis-with-arkime")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

---
name: implementing-network-deception-with-honeypots
description: "Deploy and manage network honeypots using OpenCanary, T-Pot, or Cowrie to detect unauthorized access, lateral"
domain: cybersecurity
subdomain: deception-technology
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-network-deception-with-honeypots/SKILL.md"
---
# Implementing Network Deception With Honeypots

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-network-deception-with-honeypots/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-network-deception-with-honeypots", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-network-deception-with-honeypots")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

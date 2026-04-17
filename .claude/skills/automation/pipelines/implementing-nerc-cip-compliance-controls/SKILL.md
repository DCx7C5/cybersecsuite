---
name: implementing-nerc-cip-compliance-controls
description: "'This skill covers implementing North American Electric Reliability Corporation Critical Infrastructure Protection"
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-nerc-cip-compliance-controls/SKILL.md"
---
# Implementing Nerc Cip Compliance Controls

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-nerc-cip-compliance-controls/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-nerc-cip-compliance-controls", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-nerc-cip-compliance-controls")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

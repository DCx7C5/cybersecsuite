---
name: implementing-ics-firewall-with-tofino
description: "'Deploy and configure Tofino industrial firewalls from Belden/Hirschmann to protect SCADA systems and PLCs using"
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-ics-firewall-with-tofino/SKILL.md"
---
# Implementing Ics Firewall With Tofino

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-ics-firewall-with-tofino/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-ics-firewall-with-tofino", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-ics-firewall-with-tofino")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

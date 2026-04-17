---
name: implementing-ot-incident-response-playbook
description: "'Develop and implement OT-specific incident response playbooks aligned with SANS PICERL framework, IEC 62443,"
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-ot-incident-response-playbook/SKILL.md"
---
# Implementing Ot Incident Response Playbook

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-ot-incident-response-playbook/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-ot-incident-response-playbook", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-ot-incident-response-playbook")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

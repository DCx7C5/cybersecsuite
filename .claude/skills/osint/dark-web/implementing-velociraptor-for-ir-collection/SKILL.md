---
name: implementing-velociraptor-for-ir-collection
description: "Deploy and configure Velociraptor for scalable endpoint forensic artifact collection during incident response"
domain: cybersecurity
subdomain: incident-response
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-velociraptor-for-ir-collection/SKILL.md"
---
# Implementing Velociraptor For Ir Collection

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-velociraptor-for-ir-collection/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-velociraptor-for-ir-collection", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-velociraptor-for-ir-collection")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

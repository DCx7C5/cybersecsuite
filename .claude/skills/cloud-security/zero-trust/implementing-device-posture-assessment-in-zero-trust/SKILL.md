---
name: implementing-device-posture-assessment-in-zero-trust
description: "'Implementing device posture assessment as a zero trust access control by integrating endpoint health signals"
domain: cybersecurity
subdomain: zero-trust-architecture
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-device-posture-assessment-in-zero-trust/SKILL.md"
---
# Implementing Device Posture Assessment In Zero Trust

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-device-posture-assessment-in-zero-trust/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-device-posture-assessment-in-zero-trust", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-device-posture-assessment-in-zero-trust")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

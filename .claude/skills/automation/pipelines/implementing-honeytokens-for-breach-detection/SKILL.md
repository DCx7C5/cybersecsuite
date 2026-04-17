---
name: implementing-honeytokens-for-breach-detection
description: "'Deploys canary tokens and honeytokens (fake AWS credentials, DNS canaries, document beacons, database records)"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-honeytokens-for-breach-detection/SKILL.md"
---
# Implementing Honeytokens For Breach Detection

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-honeytokens-for-breach-detection/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-honeytokens-for-breach-detection", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-honeytokens-for-breach-detection")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

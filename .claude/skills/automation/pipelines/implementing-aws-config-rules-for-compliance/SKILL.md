---
name: implementing-aws-config-rules-for-compliance
description: "'Implementing AWS Config rules for continuous compliance monitoring of AWS resources, deploying managed and custom"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-aws-config-rules-for-compliance/SKILL.md"
---
# Implementing Aws Config Rules For Compliance

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-aws-config-rules-for-compliance/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-aws-config-rules-for-compliance", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-aws-config-rules-for-compliance")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

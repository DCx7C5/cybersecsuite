---
name: performing-aws-privilege-escalation-assessment
description: "'Performing authorized privilege escalation assessments in AWS environments to identify IAM misconfigurations"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-aws-privilege-escalation-assessment/SKILL.md"
---
# Performing Aws Privilege Escalation Assessment

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-aws-privilege-escalation-assessment/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-aws-privilege-escalation-assessment", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-aws-privilege-escalation-assessment")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

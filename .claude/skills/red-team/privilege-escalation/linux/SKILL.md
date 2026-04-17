---
name: performing-privilege-escalation-on-linux
description: "Linux privilege escalation involves elevating from a low-privilege user account to root access on a compromised"
domain: cybersecurity
subdomain: red-teaming
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-privilege-escalation-on-linux/SKILL.md"
---
# Performing Privilege Escalation On Linux

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-privilege-escalation-on-linux/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-privilege-escalation-on-linux", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-privilege-escalation-on-linux")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@red-teaming-analyst` or `@cybersec-agent`

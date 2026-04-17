---
name: performing-initial-access-with-evilginx3
description: "Perform authorized initial access using EvilGinx3 adversary-in-the-middle phishing framework to capture session"
domain: cybersecurity
subdomain: red-teaming
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-initial-access-with-evilginx3/SKILL.md"
---
# Performing Initial Access With Evilginx3

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-initial-access-with-evilginx3/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-initial-access-with-evilginx3", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-initial-access-with-evilginx3")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@red-teaming-analyst` or `@cybersec-agent`

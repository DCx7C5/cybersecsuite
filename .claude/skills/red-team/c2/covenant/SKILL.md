---
name: performing-red-team-with-covenant
description: "Conduct red team operations using the Covenant C2 framework for authorized adversary simulation, including listener"
domain: cybersecurity
subdomain: red-team
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-red-team-with-covenant/SKILL.md"
---
# Performing Red Team With Covenant

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-red-team-with-covenant/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-red-team-with-covenant", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-red-team-with-covenant")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@red-team-analyst` or `@cybersec-agent`

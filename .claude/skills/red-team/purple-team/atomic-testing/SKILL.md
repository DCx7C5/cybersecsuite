---
name: performing-purple-team-atomic-testing
description: "'Executes Atomic Red Team tests mapped to MITRE ATT&CK techniques, performs coverage gap analysis across the"
domain: cybersecurity
subdomain: purple-team
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-purple-team-atomic-testing/SKILL.md"
---
# Performing Purple Team Atomic Testing

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-purple-team-atomic-testing/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-purple-team-atomic-testing", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-purple-team-atomic-testing")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@purple-team-analyst` or `@cybersec-agent`

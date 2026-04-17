---
name: conducting-external-reconnaissance-with-osint
description: "'Conducts external reconnaissance using Open Source Intelligence (OSINT) techniques to map an organization''s"
domain: cybersecurity
subdomain: penetration-testing
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-external-reconnaissance-with-osint/SKILL.md"
---
# Conducting External Reconnaissance With Osint

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-external-reconnaissance-with-osint/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="conducting-external-reconnaissance-with-osint", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="conducting-external-reconnaissance-with-osint")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@penetration-testing-analyst` or `@cybersec-agent`

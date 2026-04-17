---
name: performing-ot-network-security-assessment
description: "'This skill covers conducting comprehensive security assessments of Operational Technology (OT) networks including"
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-ot-network-security-assessment/SKILL.md"
---
# Performing Ot Network Security Assessment

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-ot-network-security-assessment/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-ot-network-security-assessment", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-ot-network-security-assessment")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@ot-ics-security-analyst` or `@cybersec-agent`

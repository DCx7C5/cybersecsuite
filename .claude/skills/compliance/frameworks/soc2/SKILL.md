---
name: performing-soc2-type2-audit-preparation
description: "'Automates SOC 2 Type II audit preparation including gap assessment against AICPA Trust Services Criteria (CC1-CC9),"
domain: cybersecurity
subdomain: governance-risk-compliance
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-soc2-type2-audit-preparation/SKILL.md"
---
# Performing Soc2 Type2 Audit Preparation

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-soc2-type2-audit-preparation/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-soc2-type2-audit-preparation", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-soc2-type2-audit-preparation")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@governance-risk-compliance-analyst` or `@cybersec-agent`

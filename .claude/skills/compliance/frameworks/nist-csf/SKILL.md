---
name: performing-nist-csf-maturity-assessment
description: ">-"
domain: cybersecurity
subdomain: compliance-governance
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: [GV.OC-01, GV.RM-01, GV.PO-01, ID.RA-01, GV.OV-01]
tags: [compliance, governance, nist, csf, maturity-assessment, risk-management]
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-nist-csf-maturity-assessment/SKILL.md"
---
# Performing Nist Csf Maturity Assessment

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-nist-csf-maturity-assessment/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-nist-csf-maturity-assessment", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-nist-csf-maturity-assessment")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@compliance-governance-analyst` or `@cybersec-agent`

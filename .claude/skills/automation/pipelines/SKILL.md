---
name: building-automated-malware-submission-pipeline
description: "'Builds an automated malware submission and analysis pipeline that collects suspicious files from endpoints and"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-automated-malware-submission-pipeline/SKILL.md"
---
# Building Automated Malware Submission Pipeline

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-automated-malware-submission-pipeline/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="building-automated-malware-submission-pipeline", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-automated-malware-submission-pipeline")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@soc-operations-analyst` or `@cybersec-agent`

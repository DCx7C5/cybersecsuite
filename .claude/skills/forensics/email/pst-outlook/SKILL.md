---
name: analyzing-outlook-pst-for-email-forensics
description: "Analyze Microsoft Outlook PST and OST files for email forensic evidence including message content, headers, attachments,"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-outlook-pst-for-email-forensics/SKILL.md"
---
# Analyzing Outlook Pst For Email Forensics

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-outlook-pst-for-email-forensics/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-outlook-pst-for-email-forensics", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-outlook-pst-for-email-forensics")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@digital-forensics-analyst` or `@cybersec-agent`

---
name: triaging-vulnerabilities-with-ssvc-framework
description: "Triage and prioritize vulnerabilities using CISA's Stakeholder-Specific Vulnerability Categorization (SSVC) decision"
domain: cybersecurity
subdomain: vulnerability-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/triaging-vulnerabilities-with-ssvc-framework/SKILL.md"
---
# Triaging Vulnerabilities With Ssvc Framework

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/triaging-vulnerabilities-with-ssvc-framework/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="triaging-vulnerabilities-with-ssvc-framework", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="triaging-vulnerabilities-with-ssvc-framework")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@vulnerability-management-analyst` or `@cybersec-agent`

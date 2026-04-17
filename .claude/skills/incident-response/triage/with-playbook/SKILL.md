---
name: triaging-security-incident-with-ir-playbook
description: "Classify and prioritize security incidents using structured IR playbooks to determine severity, assign response"
domain: cybersecurity
subdomain: incident-response
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/triaging-security-incident-with-ir-playbook/SKILL.md"
---
# Triaging Security Incident With Ir Playbook

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/triaging-security-incident-with-ir-playbook/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="triaging-security-incident-with-ir-playbook", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=)

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="triaging-security-incident-with-ir-playbook")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@incident-response-analyst` or `@cybersec-agent`

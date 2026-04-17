---
name: testing-android-intents-for-vulnerabilities
description: "'Tests Android inter-process communication (IPC) through intents for vulnerabilities including intent injection,"
domain: cybersecurity
subdomain: mobile-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-android-intents-for-vulnerabilities/SKILL.md"
---
# Testing Android Intents For Vulnerabilities

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-android-intents-for-vulnerabilities/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="testing-android-intents-for-vulnerabilities", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="testing-android-intents-for-vulnerabilities")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@mobile-security-analyst` or `@cybersec-agent`

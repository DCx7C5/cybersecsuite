---
name: performing-ios-app-security-assessment
description: "'Performs comprehensive iOS application security assessments using Frida for dynamic instrumentation, Objection"
domain: cybersecurity
subdomain: mobile-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-ios-app-security-assessment/SKILL.md"
---
# Performing Ios App Security Assessment

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-ios-app-security-assessment/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-ios-app-security-assessment", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-ios-app-security-assessment")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@mobile-security-analyst` or `@cybersec-agent`

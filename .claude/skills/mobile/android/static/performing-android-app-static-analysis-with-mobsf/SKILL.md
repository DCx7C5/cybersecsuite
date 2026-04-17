---
name: performing-android-app-static-analysis-with-mobsf
description: "'Performs automated static analysis of Android applications using Mobile Security Framework (MobSF) to identify"
domain: cybersecurity
subdomain: mobile-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-android-app-static-analysis-with-mobsf/SKILL.md"
---
# Performing Android App Static Analysis With Mobsf

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-android-app-static-analysis-with-mobsf/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-android-app-static-analysis-with-mobsf", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-android-app-static-analysis-with-mobsf")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

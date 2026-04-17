---
name: performing-iot-security-assessment
description: "'Performs comprehensive security assessments of IoT devices and their ecosystems by testing hardware interfaces,"
domain: cybersecurity
subdomain: penetration-testing
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-iot-security-assessment/SKILL.md"
---
# Performing Iot Security Assessment

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-iot-security-assessment/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-iot-security-assessment", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-iot-security-assessment")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

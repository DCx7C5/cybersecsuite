---
name: performing-oil-gas-cybersecurity-assessment
description: "'This skill covers conducting cybersecurity assessments specific to oil and gas facilities including upstream"
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-oil-gas-cybersecurity-assessment/SKILL.md"
---
# Performing Oil Gas Cybersecurity Assessment

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-oil-gas-cybersecurity-assessment/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-oil-gas-cybersecurity-assessment", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-oil-gas-cybersecurity-assessment")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

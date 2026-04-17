---
name: performing-power-grid-cybersecurity-assessment
description: "'This skill covers conducting cybersecurity assessments of electric power grid infrastructure including generation"
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-power-grid-cybersecurity-assessment/SKILL.md"
---
# Performing Power Grid Cybersecurity Assessment

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-power-grid-cybersecurity-assessment/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-power-grid-cybersecurity-assessment", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-power-grid-cybersecurity-assessment")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

---
name: performing-windows-artifact-analysis-with-eric-zimmerman-tools
description: "Perform comprehensive Windows forensic artifact analysis using Eric Zimmerman's open-source EZ Tools suite including"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-windows-artifact-analysis-with-eric-zimmerman-tools/SKILL.md"
---
# Performing Windows Artifact Analysis With Eric Zimmerman Tools

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-windows-artifact-analysis-with-eric-zimmerman-tools/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-windows-artifact-analysis-with-eric-zimmerman-tools", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-windows-artifact-analysis-with-eric-zimmerman-tools")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

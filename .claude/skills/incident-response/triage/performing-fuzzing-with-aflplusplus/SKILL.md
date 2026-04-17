---
name: performing-fuzzing-with-aflplusplus
description: "'Perform coverage-guided fuzzing of compiled binaries using AFL++ (American Fuzzy Lop Plus Plus) to discover"
domain: cybersecurity
subdomain: application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-fuzzing-with-aflplusplus/SKILL.md"
---
# Performing Fuzzing With Aflplusplus

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-fuzzing-with-aflplusplus/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-fuzzing-with-aflplusplus", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-fuzzing-with-aflplusplus")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

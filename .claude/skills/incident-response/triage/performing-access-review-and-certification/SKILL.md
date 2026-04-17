---
name: performing-access-review-and-certification
description: "Conduct systematic access reviews and certifications to ensure users have appropriate access rights aligned with"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-access-review-and-certification/SKILL.md"
---
# Performing Access Review And Certification

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-access-review-and-certification/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-access-review-and-certification", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-access-review-and-certification")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

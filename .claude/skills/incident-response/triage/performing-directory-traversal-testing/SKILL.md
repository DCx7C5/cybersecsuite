---
name: performing-directory-traversal-testing
description: "Testing web applications for path traversal vulnerabilities that allow reading or writing arbitrary files on"
domain: cybersecurity
subdomain: web-application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-directory-traversal-testing/SKILL.md"
---
# Performing Directory Traversal Testing

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-directory-traversal-testing/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-directory-traversal-testing", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-directory-traversal-testing")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

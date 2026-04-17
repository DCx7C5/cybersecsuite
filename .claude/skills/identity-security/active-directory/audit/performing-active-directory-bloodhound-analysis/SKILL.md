---
name: performing-active-directory-bloodhound-analysis
description: "Use BloodHound and SharpHound to enumerate Active Directory relationships and identify attack paths from compromised"
domain: cybersecurity
subdomain: red-teaming
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-active-directory-bloodhound-analysis/SKILL.md"
---
# Performing Active Directory Bloodhound Analysis

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-active-directory-bloodhound-analysis/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-active-directory-bloodhound-analysis", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-active-directory-bloodhound-analysis")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

---
name: performing-authenticated-scan-with-openvas
description: "Configure and execute authenticated vulnerability scans using OpenVAS/Greenbone Vulnerability Management with"
domain: cybersecurity
subdomain: vulnerability-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-authenticated-scan-with-openvas/SKILL.md"
---
# Performing Authenticated Scan With Openvas

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-authenticated-scan-with-openvas/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-authenticated-scan-with-openvas", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-authenticated-scan-with-openvas")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

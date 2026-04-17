---
name: performing-ssrf-vulnerability-exploitation
description: "Test for Server-Side Request Forgery vulnerabilities by probing cloud metadata endpoints, internal network services,"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-ssrf-vulnerability-exploitation/SKILL.md"
---
# Performing Ssrf Vulnerability Exploitation

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-ssrf-vulnerability-exploitation/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-ssrf-vulnerability-exploitation", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-ssrf-vulnerability-exploitation")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@security-operations-analyst` or `@cybersec-agent`

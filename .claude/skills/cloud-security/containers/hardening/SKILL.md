---
name: performing-container-image-hardening
description: "'This skill covers hardening container images by minimizing attack surface, removing unnecessary packages, implementing"
domain: cybersecurity
subdomain: devsecops
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-container-image-hardening/SKILL.md"
---
# Performing Container Image Hardening

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-container-image-hardening/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-container-image-hardening", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-container-image-hardening")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@devsecops-analyst` or `@cybersec-agent`

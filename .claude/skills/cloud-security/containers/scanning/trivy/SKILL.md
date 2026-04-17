---
name: performing-container-security-scanning-with-trivy
description: "Scan container images, filesystems, and Kubernetes manifests for vulnerabilities, misconfigurations, exposed"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-container-security-scanning-with-trivy/SKILL.md"
---
# Performing Container Security Scanning With Trivy

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-container-security-scanning-with-trivy/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-container-security-scanning-with-trivy", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-container-security-scanning-with-trivy")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@container-security-analyst` or `@cybersec-agent`

---
name: scanning-container-images-with-grype
description: "Scan container images for known vulnerabilities using Anchore Grype with SBOM-based matching and configurable"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/scanning-container-images-with-grype/SKILL.md"
---
# Scanning Container Images With Grype

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/scanning-container-images-with-grype/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="scanning-container-images-with-grype", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="scanning-container-images-with-grype")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@container-security-analyst` or `@cybersec-agent`

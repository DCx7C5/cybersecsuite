---
name: performing-cloud-native-forensics-with-falco
description: "'Uses Falco YAML rules for runtime threat detection in containers and Kubernetes, monitoring syscalls for shell"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-cloud-native-forensics-with-falco/SKILL.md"
---
# Performing Cloud Native Forensics With Falco

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-cloud-native-forensics-with-falco/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-cloud-native-forensics-with-falco", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-cloud-native-forensics-with-falco")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@cloud-security-analyst` or `@cybersec-agent`

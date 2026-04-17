---
name: deploying-edr-agent-with-crowdstrike
description: "'Deploys and configures CrowdStrike Falcon EDR agents across enterprise endpoints to enable real-time threat"
domain: cybersecurity
subdomain: endpoint-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-edr-agent-with-crowdstrike/SKILL.md"
---
# Deploying Edr Agent With Crowdstrike

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-edr-agent-with-crowdstrike/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="deploying-edr-agent-with-crowdstrike", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="deploying-edr-agent-with-crowdstrike")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@endpoint-security-analyst` or `@cybersec-agent`

---
name: detecting-azure-storage-account-misconfigurations
description: "Audit Azure Blob and ADLS storage accounts for public access exposure, weak or long-lived SAS tokens, missing"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-azure-storage-account-misconfigurations/SKILL.md"
---
# Detecting Azure Storage Account Misconfigurations

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-azure-storage-account-misconfigurations/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-azure-storage-account-misconfigurations", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-azure-storage-account-misconfigurations")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

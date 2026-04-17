---
name: implementing-endpoint-detection-with-wazuh
description: "Deploy and configure Wazuh SIEM/XDR for endpoint detection including agent management, custom decoder and rule"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-endpoint-detection-with-wazuh/SKILL.md"
---
# Implementing Endpoint Detection With Wazuh

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-endpoint-detection-with-wazuh/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-endpoint-detection-with-wazuh", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-endpoint-detection-with-wazuh")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

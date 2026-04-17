---
name: implementing-iso-27001-information-security-management
description: "ISO/IEC 27001:2022 is the international standard for establishing, implementing, maintaining, and continually improving an Information Security Management System (ISMS). This skill covers the complete"
domain: cybersecurity
subdomain: compliance-governance
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: [GV.OC-01, GV.RM-01, GV.PO-01, ID.RA-01, PR.DS-01]
tags: [compliance, governance, iso27001, isms, risk-management, certification]
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-iso-27001-information-security-management/SKILL.md"
---
# Implementing Iso 27001 Information Security Management

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-iso-27001-information-security-management/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-iso-27001-information-security-management", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-iso-27001-information-security-management")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

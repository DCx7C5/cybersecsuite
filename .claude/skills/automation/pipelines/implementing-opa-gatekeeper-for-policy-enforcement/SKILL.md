---
name: implementing-opa-gatekeeper-for-policy-enforcement
description: "Enforce Kubernetes admission policies using OPA Gatekeeper with ConstraintTemplates, Rego rules, and the Gatekeeper"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-opa-gatekeeper-for-policy-enforcement/SKILL.md"
---
# Implementing Opa Gatekeeper For Policy Enforcement

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-opa-gatekeeper-for-policy-enforcement/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-opa-gatekeeper-for-policy-enforcement", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-opa-gatekeeper-for-policy-enforcement")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

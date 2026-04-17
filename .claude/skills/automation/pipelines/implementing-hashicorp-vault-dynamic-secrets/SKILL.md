---
name: implementing-hashicorp-vault-dynamic-secrets
description: "'Implements HashiCorp Vault dynamic secrets engines for database credentials, AWS IAM keys, and PKI certificates"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-hashicorp-vault-dynamic-secrets/SKILL.md"
---
# Implementing Hashicorp Vault Dynamic Secrets

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-hashicorp-vault-dynamic-secrets/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-hashicorp-vault-dynamic-secrets", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-hashicorp-vault-dynamic-secrets")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.

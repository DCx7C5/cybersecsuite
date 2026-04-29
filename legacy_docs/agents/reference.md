# Agents Reference

Agent definitions for CyberSecSuite, their models, triggers, and team compositions.

Agent files live in `.claude/agents/` (active agents for Claude Code) and `templates/agents/` (base templates).

---

## Active Agent Files

### `.claude/agents/` (root)

| File                     | Description                                                         |
|--------------------------|---------------------------------------------------------------------|
| `AGENT_FACTORY.md`       | Meta-agent: creates new production-grade specialist agents          |
| `DEV_SUB_AGENTS.md`      | Developer sub-agent definitions (python, code-review, frontend, db) |
| `encoding-specialist.md` | Encoding/decoding analysis and anomaly detection                    |

### `.claude/agents/sub_agents/` (12 specialists)

| Agent                  | Model  | Primary Trigger / Role                                       |
|------------------------|--------|--------------------------------------------------------------|
| `cybersec-agent`       | Sonnet | Central orchestrator for APT/rootkit investigations          |
| `code-reviewer`        | Sonnet | Pull request review, code feedback, security scanning        |
| `frontend-design`      | Sonnet | Web components, landing pages, dashboards, React             |
| `firmware-analyst`     | Opus   | UEFI implants, boot anomalies, SPI flash                     |
| `logfile-analyst`      | Sonnet | Auth failures, log gaps, attacker timeline analysis          |
| `postgres-db-engineer` | Sonnet | PostgreSQL optimization, JSONB, advanced queries             |
| `python-code-reviewer` | Sonnet | Python code review: async, Pydantic, crypto patterns         |
| `python-developer`     | Sonnet | Python code, FastAPI, Tortoise ORM, tests                    |
| `reverse-engineer`     | Opus   | ELF/PE/Mach-O binaries, shellcode, deobfuscation             |
| `settings-analyst`     | Sonnet | Config compliance, privilege escalation via misconfiguration |
| `token-optimizer`      | Haiku  | Token budget management, context compression, caching        |
| `watchdog`             | Haiku  | SSL keylog files, cert stores, private key locations         |

### `.claude/agents/teams/` (3 team modes)

| Team         | File              | Composition                                          |
|--------------|-------------------|------------------------------------------------------|
| Blue Team    | `blue-team.md`    | Defensive — forensics analysts, detection, response  |
| Red Team     | `red-team.md`     | Offensive simulation — exploitation, persistence, C2 |
| Purple Team  | `purple-team.md`  | Combined — simultaneous offense + defense            |

---

## Full Specialist Roster (from `agents.md` spec)

The following agents are defined in templates and available via A2A routing, even if not all have active `.claude/agents/` files:

### Forensics

| Agent                 | Model  | Trigger                                                           |
|-----------------------|--------|-------------------------------------------------------------------|
| `filesystem-analyst`  | Sonnet | Hidden files, SUID binaries, timestamp anomalies                  |
| `kernel-analyst`      | Sonnet | LKM, eBPF, firmware, kernel rootkit, /proc anomalies              |
| `memory-analyst`      | Sonnet | Suspicious process, memory anomaly, injection indicator           |
| `persistence-analyst` | Sonnet | New service, cron anomaly, kernel module, startup persistence     |
| `process-analyst`     | Sonnet | Abnormal resource usage, process-based persistence                |
| `logfile-analyst`     | Sonnet | Auth failures, log gaps, unexpected service behavior              |
| `firmware-analyst`    | Opus   | UEFI implants, boot anomalies, SPI flash, initramfs tampering     |
| `reverse-engineer`    | Opus   | ELF/PE/Mach-O binaries, shellcode, unpacking, deobfuscation       |

### Network & Protocol

| Agent               | Model  | Trigger                                                          |
|---------------------|--------|------------------------------------------------------------------|
| `network-analyst`   | Sonnet | Network IOC, C2 pattern, beaconing, packet captures              |
| `layer2-specialist` | Sonnet | ARP table anomalies, MAC flooding, VLAN integrity                |
| `layer3-specialist` | Sonnet | Routing anomalies, ICMP flood, fragmentation                     |
| `layer4-specialist` | Sonnet | TCP anomalies, UDP amplification, port scan                      |
| `layer5-specialist` | Sonnet | Session token anomalies, RPC abuse, SIP irregularities           |
| `layer6-specialist` | Sonnet | Encoding anomalies, TLS downgrade, deserialization gadget chains |
| `layer7-specialist` | Sonnet | Web app anomalies, API abuse, authentication bypass              |

### Security Analysis

| Agent                    | Model  | Trigger                                                      |
|--------------------------|--------|--------------------------------------------------------------|
| `cybersec-analyst`       | Sonnet | CVE-YYYY-NNNNN, IOC discovery, MITRE technique T1xxx         |
| `certificate-analyst`    | Sonnet | TLS anomalies, unexpected issuer, self-signed certs          |
| `encoding-specialist`    | Sonnet | Suspicious encoded strings, obfuscated payloads              |
| `settings-analyst`       | Sonnet | Config compliance, privilege escalation via misconfiguration |
| `steganography-analyst`  | Sonnet | Suspicious media files, LSB embedding, hidden payloads       |
| `vuln-scanner`           | Sonnet | OWASP 2025, supply chain, attack surface mapping             |
| `threat-modeler`         | Sonnet | Threat model, attack surface, STRIDE, risk scoring           |
| `audiovideo-analyst`     | Sonnet | Media metadata, deepfake indicators, AV integrity checks     |
| `watchdog`               | Haiku  | SSL keylog files, cert stores, private key locations         |
| `command-verifier`       | Haiku  | Command safety review, destructive command gating            |

### Developers

| Agent                  | Model  | Trigger                                                |
|------------------------|--------|--------------------------------------------------------|
| `python-developer`     | Sonnet | Python code, FastAPI, ORM models, async/await          |
| `cpp-developer`        | Sonnet | ELF binary, kernel module, eBPF C, exploit             |
| `postgres-db-engineer` | Sonnet | PostgreSQL optimization, JSONB, advanced queries       |
| `code-reviewer`        | Sonnet | Pull request review, code feedback, security scanning  |

### Frontend

| Agent             | Model  | Trigger                                             |
|-------------------|--------|-----------------------------------------------------|
| `frontend-design` | Sonnet | Web components, landing pages, dashboards, HTML/CSS |
| `senior-frontend` | Sonnet | ReactJS, NextJS, TypeScript, Tailwind               |

### Meta / Utility

| Agent             | Model | Description                                                          |
|-------------------|-------|----------------------------------------------------------------------|
| `agent-factory`   | Opus  | Creates new agents from description. 9-chapter blueprint generation. |
| `token-optimizer` | Haiku | Token budget management, context compression, caching strategies     |

---

## Agent Frontmatter Schema

```yaml
---
name: agent-name          # matches filename (kebab-case)
description: "..."        # single-line trigger description for routing
model: sonnet             # haiku | sonnet | opus | deepseek-v3 | gemini-2.0-flash | ...
maxTurns: 30              # conversation turn limit
tools:                    # tools this agent may use
  - Read
  - Bash
disallowedTools:          # optional — read-only analysts
  - Write
  - Edit
---
```

Model can be any provider-specific model ID (routed through AI Proxy). See [sdk-integration.md](sdk-integration.md) for model routing details.

---

## A2A Invocation

```bash
# Route to specific agent
@cybersec-analyst CVE-2024-1234

# Route to orchestrator (auto-routes to best specialist)
investigate this IOC: 192.168.1.100

# List all agents
list agents
```

See [../api/a2a-protocol.md](../api/a2a-protocol.md) for full A2A protocol reference.

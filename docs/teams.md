# Team Mode

CyberSecSuite supports experimental multi-agent team compositions via Claude Code's team mode feature.

---

## Feature Flag

Team mode is enabled in `.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Setting `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` activates Claude Code's experimental agent teams support, which allows team definition files in `.claude/agents/teams/` to be loaded alongside individual agent definitions.

---

## Team Files

Three team compositions are defined in `.claude/agents/teams/`:

| File | Alias | Default | Description |
|------|-------|---------|-------------|
| `blue-team.md` | `blue` | ✅ yes | Defensive forensics and incident response |
| `red-team.md` | `red` | no | Offensive simulation and penetration testing |
| `purple-team.md` | `purple` | no | Combined attack + defense (depends on blue + red) |

Each team file uses a `role: team-mode` frontmatter field and is loaded by the `hunter` orchestrator at startup.

---

## Team Responsibilities

### 🔵 Blue Team — Defensive Mode

The default team. Operates as a methodical, evidence-driven forensic investigator.

**Focus areas:**
- Rapid recon and baseline comparison against known-good state
- Rootkit, kernel module, eBPF, and firmware implant analysis
- Persistence hunting across all layers (userland → kernel → firmware)
- Memory forensics, network anomalies, and process inspection
- IOC validation and correlation against MITRE ATT&CK
- BLAKE2b integrity verification of all collected evidence
- Hardening recommendations, compliance, and audit readiness

**Constraints:** Non-destructive and read-only by default. Every finding cross-validated with ≥2 independent sources.

---

### 🔴 Red Team — Offensive Mode

Emulates a skilled adversary (nation-state to advanced criminal group) using living-off-the-land techniques.

**Focus areas:**
- Initial access, execution, and multi-layer persistence
- Privilege escalation, defense evasion, and anti-forensics
- Credential access, lateral movement, C2, and exfiltration simulation
- eBPF injection, kernel module loading, firmware implant emulation
- Supply chain and configuration abuse scenarios

**Constraints:** All actions require `AgentRootPermission` check + user approval for root/sudo. TTPs mapped to MITRE ATT&CK. Real data is never exfiltrated — test artifacts only.

---

### 🟣 Purple Team — Hybrid Mode

Combines attacker and defender mindsets simultaneously to improve security posture. Depends on both blue-team and red-team definitions.

**Focus areas:**
- Simulating realistic attack chains while documenting detection gaps
- Improving detection rules and baselines while actively testing them
- Providing both exploit PoC (Red) and hardening recommendation (Blue) for every finding
- Mapping each attack path: `attack vector → detection opportunity → mitigation`

**Output format** for every finding:
```
ATTACK PATH: [technique]
DETECTION GAP: [what monitoring misses this]
HARDENING: [specific control to close the gap]
MITRE: [T-code]
```

---

## Using Teams

Invoke a specific team mode via the `cybersec-agent` orchestrator:

```bash
# Blue team (default — defensive investigation)
@cybersec-agent blue

# Red team (offensive simulation)
@cybersec-agent red

# Purple team (simultaneous attack + defense)
@cybersec-agent purple
```

The orchestrator routes the investigation to the appropriate team context, which shapes how specialist sub-agents are delegated to and what constraints apply.

---

## Team Task Command

A `.claude/commands/team-task.md` slash command will be added to provide a quick shorthand for switching team modes and launching a task in one step:

```
/team-task blue  investigate persistence on host web-prod-01
/team-task red   simulate lateral movement from compromised workstation
/team-task purple test T1055 process injection and verify detection coverage
```

> **Note:** The `team-task` slash command is planned — add it as `.claude/commands/team-task.md` when implementing.

---

## Crypto Integrity (All Teams)

All teams share the same artifact integrity guarantees:

- **BLAKE2b-256** — integrity hashing for all collected evidence
- **Ed25519** — frontmatter signatures on all submitted artifacts

Both are enforced via the `src/crypto/` module and the `mcp__dystopian__sign_artifact` / `mcp__dystopian__verify_artifact` MCP tools.

---

## See Also

- [agents.md](agents.md) — full list of 33 specialist agents
- [configuration.md](configuration.md) — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` setting
- [architecture.md](architecture.md) — system design and agent tiers

# Action Vocabulary — CyberSecSuite Skills

> **Rule:** The last path segment before `SKILL.md` MUST be one of these 22 verbs.
> No exceptions without a team decision.

---

## Why Standardize Actions?

Skills are discovered, filtered, and routed by agents using path patterns.
Consistent action verbs make it possible to:
- Find all `detect` skills across all domains: `**/detect/SKILL.md`
- Find all Linux red-team actions: `linux/**/{exploit,bypass,extract,enum}/SKILL.md`
- Build SOC playbooks that auto-select the right skill by action type

---

## Blue Team — Defensive Actions

### `detect`
**What:** Identify malicious or anomalous activity, either in real-time or from logs/artifacts.
**When:** The skill's primary value is *recognising* that something bad happened or is happening.
**Examples:**
- `linux/kernel/ebpf/rootkit/detect`
- `linux/services/cron/job/backdoor/detect`
- `network/layer7/dns/tunneling/detect`

**Do NOT use detect when:** The skill is primarily about *collecting* data for later analysis
(use `collect` or `forensic`) or about *continuously watching* a system (use `monitor`).

---

### `analyze`
**What:** Deep technical examination of an artifact, binary, or behavior to understand it.
**When:** The skill produces insight by dissecting something — parsing, reversing, correlating.
**Examples:**
- `linux/filesystem/ext4/inode/analyze`
- `linux/processes/proc-fs/maps/analyze`
- `malware/dynamic/sandbox/cuckoo/analyze`

**Distinction from `forensic`:** `analyze` is targeted (one artifact, one question).
`forensic` is a full post-incident workflow (collect → preserve → analyze → report).

---

### `audit`
**What:** Review a configuration, policy, or system state against a security standard.
**When:** The skill checks compliance, misconfigurations, or security posture — not incidents.
**Examples:**
- `linux/kernel/network-stack/netfilter/iptables/audit`
- `linux/identity/gshadow/group/audit`
- `linux/hardening/selinux/policy/audit`

**Distinction from `harden`:** `audit` = *read-only* review. `harden` = *apply* controls.

---

### `monitor`
**What:** Continuous, ongoing observation of system state or events.
**When:** The skill sets up persistent observation (dashboards, agents, rules) rather than
investigating a specific incident.
**Examples:**
- `linux/kernel/ebpf/tracepoint/deploy` (setup) → then `monitor`
- `linux/logging/auditd/syscall/monitor`
- `soc/siem/sigma-rules/monitor`

---

### `hunt`
**What:** Proactive, hypothesis-driven search for threats that haven't triggered alerts.
**When:** The skill starts from a threat hypothesis (e.g., "assume Cobalt Strike is present")
and searches for indicators — not triggered by an alert.
**Examples:**
- `soc/hunting/lolbins/hunt`
- `linux/processes/elf/got/hook/hunt`
- `malware/c2/beacon/pattern/hunt`

**Distinction from `detect`:** `detect` = reactive (something triggered). `hunt` = proactive.

---

### `forensic`
**What:** Post-incident workflow — collect, preserve, analyze, and document artifacts
with chain of custody for legal/investigative purposes.
**When:** The skill covers a full investigative procedure, not just one artifact.
**Examples:**
- `linux/forensics/timeline/plaso/forensic`
- `linux/hardware/storage/nvme/forensic`
- `linux/kernel/modules/lkm/forensic`

---

### `harden`
**What:** Apply security controls that reduce attack surface or enforce policy.
**When:** The skill *changes* system configuration to make it more secure.
**Examples:**
- `linux/hardening/apparmor/profile/harden`
- `linux/identity/ssh/config/harden`
- `linux/hardening/sysctl/kernel/harden`

**Do NOT use:** `configure` for security hardening. Reserve `configure` for neutral setup.

---

### `recover`
**What:** Restore data, access, or system state after damage or incident.
**When:** The skill undoes damage — deleted file recovery, decryption, backup restoration.
**Examples:**
- `linux/filesystem/ext4/deleted-file/recover`
- `linux/forensics/artifact/bash-history/recover`
- `malware/ransomware/encrypted-data/recover`

---

### `respond`
**What:** Structured incident response steps — contain, eradicate, remediate.
**When:** The skill is a response playbook or containment procedure.
**Examples:**
- `soc/playbooks/ransomware/respond`
- `soc/containment/active-threat/respond`
- `email/phishing/business-email-compromise/respond`

---

### `verify`
**What:** Validate integrity, authenticity, or correctness of an artifact or claim.
**When:** The skill checks that something IS what it claims to be (hash, signature, cert).
**Examples:**
- `linux/supply-chain/package/apt/integrity/verify`
- `linux/hardware/tpm/pcr/attestation/verify`
- `crypto/certificates/chain/trust/verify`

---

### `parse`
**What:** Decode or extract structured data from a binary or encoded format.
**When:** The skill's primary value is transforming raw bytes/logs into readable structure.
**Examples:**
- `linux/filesystem/ntfs/mft/parse`
- `linux/logging/journald/binary/parse`
- `malware/pdf/structure/pdfid/parse`

---

### `collect`
**What:** Gather artifacts from a live or dead system for preservation.
**When:** The skill focuses on artifact acquisition — before analysis happens.
**Examples:**
- `linux/forensics/artifact/bash-history/collect`
- `linux/filesystem/tmpfs/artifact/collect`
- `linux/hardware/memory/cold-boot/artifact/collect`

---

## Red Team — Offensive Actions

### `exploit`
**What:** Actively exploit a vulnerability to achieve code execution, privilege, or access.
**When:** The skill demonstrates or executes an attack path.
**Examples:**
- `linux/kernel/syscall/io-uring/abuse/exploit`
- `linux/services/logrotate/race/exploit`
- `database/postgres/copy-program/exploit`

---

### `bypass`
**What:** Circumvent a security control without exploiting a specific CVE.
**When:** The skill defeats a defensive measure (auth bypass, WAF bypass, AV evasion).
**Examples:**
- `linux/kernel/boot/secure-boot/bypass`
- `linux/identity/pam/stack/bypass`
- `linux/kernel/memory/kaslr/bypass`

---

### `extract`
**What:** Pull credentials, secrets, keys, or sensitive data from a system.
**When:** The skill's goal is data exfiltration or credential harvesting.
**Examples:**
- `linux/identity/shadow/file/extract`
- `browser/chrome/password/extract`
- `windows/identity/lsass/credential/extract`

---

### `enum`
**What:** Enumerate targets, services, users, permissions, or configurations.
**When:** Reconnaissance — building a picture of what exists before attacking.
**Examples:**
- `linux/kernel/capabilities/enum`
- `network/scanning/port/service/enum`
- `identity/ad/bloodhound/recon/enum`

**Standardization note:** Always `enum`, never `enumerate` or `enumeration`.

---

### `inject`
**What:** Insert malicious code or payload into a running process or data stream.
**When:** The skill achieves code execution by injecting into an existing process.
**Examples:**
- `linux/processes/proc-fs/mem/inject`
- `linux/processes/ptrace/injection/inject`
- `windows/processes/thread/injection/inject`

---

### `persist`
**What:** Establish a persistence mechanism that survives reboots or logouts.
**When:** The skill installs or demonstrates a persistence technique.
**Examples:**
- `linux/services/systemd/unit/persist`
- `linux/shell/profile/backdoor/persist`
- `malware/persistence/linux/persist`

---

### `escalate`
**What:** Gain higher privileges than currently held.
**When:** The skill moves from lower to higher privilege (user → root, container → host).
**Examples:**
- `linux/identity/polkit/privilege/escalate`
- `linux/kernel/privesc/exploit/escalate`
- `cloud/kubernetes/privesc/escalate`

---

### `pivot`
**What:** Move laterally from one system to another using gained access.
**When:** The skill uses a compromised host as a stepping stone to reach others.
**Examples:**
- `network/tunnel/ssh-reverse/pivot`
- `network/proxy/socks5/tunnel/pivot`
- `identity/ad/lateral-movement/pivot`

---

### `intercept`
**What:** Capture, modify, or relay traffic between two parties (MITM).
**When:** The skill positions the attacker between communicating parties.
**Examples:**
- `network/layer2/arp/poison/intercept`
- `network-filesystem/cifs/credential/intercept`
- `network/layer7/http/proxy/intercept`

---

### `simulate`
**What:** Run a controlled simulation, tabletop, or emulation exercise.
**When:** The skill is a structured exercise, not a real attack or investigation.
**Examples:**
- `soc/tabletop/ransomware/simulate`
- `red-team/engagement/plan/simulate`
- `identity/ad/adsimulation/simulate`

---

## Neutral Actions

### `configure`
**What:** Set up a tool or service for neutral operational use (not security hardening).
**When:** The skill installs and configures a component for functionality.
**Examples:**
- `network/vpn/wireguard/server/configure`
- `network/ids/suricata/rule/configure`

**Do NOT use for security hardening** — use `harden` instead.

---

### `deploy`
**What:** Deploy a tool, agent, or infrastructure component into an environment.
**When:** The skill sets up monitoring infrastructure, sensors, or agents.
**Examples:**
- `soc/edr/wazuh/agent/deploy`
- `network/ids/suricata/ids/deploy`
- `cloud/kubernetes/falco/runtime/deploy`

---

## Anti-Patterns (Never Use as Action)

| Bad             | Correct alternative                    |
|-----------------|----------------------------------------|
| `pentest`       | `exploit` / `enum` / `bypass`          |
| `assess`        | `audit` (config) or `enum` (recon)     |
| `investigation` | `forensic`                             |
| `implement`     | `configure` or `harden`                |
| `install`       | `deploy`                               |
| `scan`          | `enum` (active) or `detect` (passive)  |
| Tool names      | Tool name goes in layer 3, not action  |
| Nouns (`yara`)  | `create` for rule creation, `analyze` for use |
| `execute`       | `exploit` (offensive) or `deploy` (ops)|
| `create`        | `harden` (policy) or `configure` (setup)|
| `map`           | `analyze` or `audit`                   |

---

## Quick Reference Card

```
DEFENSIVE (blue):         OFFENSIVE (red):          NEUTRAL (ops):
  detect                    exploit                    configure
  analyze                   bypass                     deploy
  audit                     extract
  monitor                   enum
  hunt                      inject
  forensic                  persist
  harden                    escalate
  recover                   pivot
  respond                   intercept
  verify                    simulate
  parse
  collect
```

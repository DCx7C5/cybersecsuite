# Skill Taxonomy — CyberSecSuite

> **Version:** 2.0 — Component-First Restructure (2026-04)
> **Convention:** `domain / subsystem / component / mechanism / ACTION`

---

## Design Principles

1. **Component-first, not activity-first.** The first layers describe *what the thing is*
   (OS, protocol, platform). The last segment describes *what you do with it* (the action).

2. **Minimum depth: 3. Standard depth: 5. Maximum depth: 6.**
   Never use a single generic word like `dns/` or `malware/` as a standalone folder at
   depth 2 or 3 without further qualification.

3. **Actions are always one of 22 canonical verbs.** No tool names, no nouns, no adjectives
   as the last segment. See `ACTIONS.md` for the full vocabulary.

4. **One skill = one action.** If a skill does both `detect` and `exploit`, split it.

5. **Tool names belong at layer 3 (component), not layer 5 (action).**
   Example: `network/capture/pcap/wireshark/analyze` — wireshark is the component.

---

## Layer Semantics

| Layer | Role            | Examples                              |
|-------|-----------------|---------------------------------------|
| 1     | Domain          | `linux`, `network`, `cloud`, `malware`|
| 2     | Subsystem       | `kernel`, `filesystem`, `identity`    |
| 3     | Component       | `cgroups`, `ext4`, `pam`, `ebpf`      |
| 4     | Mechanism/Spec  | `v2`, `release-agent`, `bypass`, `rule`|
| 5     | **Action**      | `detect`, `analyze`, `harden`, `enum` |
| 6     | Refinement      | Only when spec has a meaningful sub-variant (IEC-62443, etc.) |

---

## Domain Catalog (Layer 1)

### System Domains — OS stacks
| Domain     | Contents                                                  |
|------------|-----------------------------------------------------------|
| `linux/`   | Kernel, filesystem, processes, memory, identity, services,|
|            | logging, hardening, shell, supply-chain, containers,      |
|            | network-services, hardware, forensics                     |
| `windows/` | Kernel, registry, processes, filesystem, identity,        |
|            | services, logging, hardening, lolbins                     |

### Platform Domains
| Domain           | Contents                                              |
|------------------|-------------------------------------------------------|
| `cloud/`         | AWS, Azure, GCP, Kubernetes, containers, devsecops,   |
|                  | serverless, zerotrust, secrets, IR                    |
| `network/`       | Layer2–7 protocol stack (OS-agnostic), wireless,      |
|                  | capture, scanning, VPN, tunnels                       |
| `web-application/`| HTTP, APIs, auth, injection, OWASP, WAF              |
| `database/`      | PostgreSQL, MySQL, MSSQL, MongoDB, Redis, SQLite       |
| `industrial/`    | ICS, SCADA, OT, IEC-62443, sector-specific            |
| `mobile/`        | Android, iOS forensics and security                   |
| `browser/`       | Chrome, Firefox, Brave, extensions, forensics         |

### Discipline Domains
| Domain       | Contents                                                |
|--------------|---------------------------------------------------------|
| `malware/`   | Static analysis, dynamic analysis, reversing, families, |
|              | C2, ransomware, rootkits, stego, supply chain           |
| `identity/`  | AD, Kerberos, LDAP, OAuth, SAML, PAM, RBAC, MFA        |
| `intel/`     | Threat feeds, MISP, OpenCTI, IOCs, MITRE, analysis      |
| `soc/`       | SIEM, playbooks, hunting, triage, IR, EDR, monitoring   |
| `crypto/`    | TLS, PKI, certificates, AES, RSA, post-quantum          |
| `osint/`     | Open-source recon, dark web, Shodan, spiderfoot         |
| `red-team/`  | Social engineering, physical, engagement execution      |
| `email/`     | Phishing, IR, DMARC, forensics                         |
| `compliance/`| CIS, NIST, PCI, ISO, GDPR, SOC2                        |

### Meta Domain
| Domain    | Contents                                                   |
|-----------|------------------------------------------------------------|
| `_meta/`  | Agent mode, scope, session config — NOT security skills    |

---

## Subsystem Map: linux/

```
linux/
  hardware/         Physical layer: CPU, memory, storage, USB, firmware
  kernel/           Kernel space: cgroups, capabilities, eBPF, LKM, syscalls,
                    memory, boot, network-stack, modules
  filesystem/       VFS + specific FSes: ext4, btrfs, xfs, lvm, luks,
                    procfs, sysfs, tmpfs, overlayfs, squashfs
  processes/        Userland process management: ptrace, ld-preload,
                    namespaces, ELF internals, proc-fs, signals
  memory/           Userland memory: stack, heap, ASLR, NX, ROP, shellcode
  identity/         Linux auth: PAM, sudo, capabilities, SSH, shadow, polkit
  services/         Init + daemons: systemd, cron, at, dbus, udev
  shell/            Shell environment: .bashrc, aliases, history, env vars
  logging/          Linux logging: auditd, syslog, journald, utmp/wtmp
  hardening/        Security controls: SELinux, AppArmor, sysctl, seccomp
  supply-chain/     Package integrity: apt, rpm, binary hashes, ld.so.preload
  containers/       Container primitives: cgroup escape, user-ns, seccomp
  network-services/ Running services: SSH, nginx, apache, cups, docker-socket
  forensics/        Linux-specific forensic artifacts: bash-history, Plaso
  network/          Linux network stack: netfilter, tc, resolver, raw sockets
```

---

## Naming Convention for `name:` field in SKILL.md frontmatter

The `name:` field is derived by joining layer-2 onwards with `-`:

```
linux/kernel/cgroups/v2/forensic  →  name: kernel-cgroups-v2-forensic
linux/identity/pam/bypass/detect  →  name: identity-pam-bypass-detect
network/layer7/dns/tunneling/detect → name: layer7-dns-tunneling-detect
```

Rule: Skip layer-1 (domain). Join remaining path segments with `-`.

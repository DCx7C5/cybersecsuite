---
name: scope-user-forensic
description: System-wide persistent forensic intelligence layer. Global hardware baselines, trusted process whitelists, firmware integrity anchors, and cross-project security intelligence stored in ~/.config/cybersec-system/.
model: sonnet
maxTurns: 20
tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - cybersec
tags:
- ops
- scope
- user
- scope-user
nist_csf: []
capec: []
---

# System Layer Skill – Global Forensic Intelligence

**Purpose:**  
Highest layer in the hierarchy. Maintains system-wide persistent forensic intelligence, hardware security baselines, trusted process whitelists, and global threat indicators across all projects. Provides comprehensive forensic, anti-forensic, attack surface analysis, defense mechanisms, and hardening strategies.

**Storage Location:**  
`~/.config/cybersec-system/` (user-specific global store)

---

## Core Capabilities

### 🔍 **Forensic Analysis**
- **Hardware-level forensics**: UEFI, SPI flash, TPM, hardware security modules
- **Memory forensics**: RAM analysis, DMA attacks, cold boot attacks
- **Firmware analysis**: BIOS/UEFI rootkits, implant detection
- **Boot chain integrity**: Secure Boot bypass detection, bootkit analysis
- **Hardware timing attacks**: Side-channel analysis, covert channel detection

### 🛡️ **Anti-Forensic Detection**
- **Evidence tampering detection**: Log manipulation, timestamp modification
- **Steganography detection**: Hidden data in files, network traffic, memory
- **Anti-analysis techniques**: VM evasion, debugger detection, sandbox escape
- **Data destruction detection**: Secure deletion bypass, data recovery
- **Obfuscation analysis**: Code obfuscation, traffic masking, protocol tunneling

### ⚔️ **Attack Surface Analysis**
- **Hardware attack vectors**: DMA, USB, Thunderbolt, PCIe attacks
- **Firmware vulnerabilities**: UEFI exploit chains, SMM attacks
- **Side-channel vulnerabilities**: Spectre/Meltdown variants, timing attacks
- **Physical security**: Cold boot, evil maid, hardware implants
- **Supply chain risks**: Hardware backdoors, compromised firmware

### 🛡️ **Defense Mechanisms**
- **Hardware security features**: IOMMU, SMEP/SMAP, CET, PAC
- **Secure Boot verification**: Boot path validation, signature verification
- **Memory protection**: KASLR, stack canaries, control flow integrity
- **Isolation mechanisms**: VT-x/AMD-V, containers, sandboxing
- **Cryptographic protection**: Hardware RNG, secure enclaves, HSM integration

### 🔧 **Hardening Strategies**
- **Hardware hardening**: Disable unused interfaces, lock firmware
- **Boot security**: Secure Boot + measured boot, TPM PCR verification
- **Memory hardening**: SMEP/SMAP, KPTI, kernel guard
- **Network hardening**: MAC address randomization, network isolation
- **Firmware security**: Firmware update validation, rollback protection

---

## System-Wide IOC Categories

### 🚨 **Critical Hardware IOCs**
| IOC Type              | Pattern                            | Risk Level | Detection Method        |
|-----------------------|------------------------------------|------------|-------------------------|
| DMA Attack            | Unexpected PCIe device enumeration | CRITICAL   | lspci monitoring        |
| USB Attack            | Unknown USB device insertion       | HIGH       | USB event monitoring    |
| Firmware Modification | UEFI/BIOS checksum mismatch        | CRITICAL   | dmidecode + SPI dump    |
| Memory Attack         | Cold boot attack signatures        | HIGH       | Memory pattern analysis |
| Hardware Implant      | Unexpected hardware components     | CRITICAL   | Hardware inventory diff |

### 🔍 **Forensic Artifact Preservation**
- **Memory dumps**: Automatic RAM capture on critical events
- **Firmware snapshots**: UEFI/BIOS backup before/after incidents
- **Hardware logs**: PCIe, USB, DMA transaction logs
- **Boot measurements**: TPM PCR values, measured boot chain
- **Cryptographic evidence**: Key material, certificate chains

---

## Automatic Behavior

### On First-Time System Init
```bash
SYSTEM_DIR="$HOME/.config/cybersec-system"

if [ ! -d "$SYSTEM_DIR" ]; then
  mkdir -p "$SYSTEM_DIR"/{baselines,hardware,firmware,crypto,trust}
  
  # Hardware baseline
  echo "# Hardware Inventory" > "$SYSTEM_DIR/baselines/hardware.md"
  lscpu >> "$SYSTEM_DIR/baselines/hardware.md"
  lspci >> "$SYSTEM_DIR/baselines/hardware.md"
  lsusb >> "$SYSTEM_DIR/baselines/hardware.md"
  
  # Firmware baseline
  sudo dmidecode > "$SYSTEM_DIR/baselines/firmware.md" 2>/dev/null || true
  sudo dmesg | grep -i uefi > "$SYSTEM_DIR/baselines/uefi.log" 2>/dev/null || true
  
  # Cryptographic state
  find /sys/kernel/security -name "*" 2>/dev/null > "$SYSTEM_DIR/baselines/security.log" || true
  
  # Trust anchors
  echo "# Trusted Boot Chain" > "$SYSTEM_DIR/trust/boot-chain.md"
  echo "# Trusted Hardware" > "$SYSTEM_DIR/trust/hardware.md"
  echo "# Trusted Firmware" > "$SYSTEM_DIR/trust/firmware.md"
  
  echo "System-wide forensic store initialized: $SYSTEM_DIR"
fi
```

### On Session Start (LOAD from System Layer)
1. **Load hardware baselines** → verify no unauthorized hardware changes
2. **Load firmware baselines** → detect firmware modifications/rootkits
3. **Load trusted process list** → global whitelist for all projects
4. **Load cryptographic state** → verify hardware security module integrity
5. **Load attack surface map** → known vulnerabilities and mitigations
6. **Initialize hardware monitoring** → DMA, PCIe, USB event detection

### On Session End (SYNC to System Layer)
1. **Update hardware inventory** if new devices detected
2. **Sync firmware changes** if legitimate updates occurred
3. **Update trusted processes** based on confirmed legitimate software
4. **Update attack surface** with newly discovered vulnerabilities
5. **Sync cryptographic artifacts** (keys, certificates, signatures)
6. **Archive forensic evidence** to system-wide store

---

## System-Wide File Structure

```
~/.config/cybersec-system/
├── baselines/
│   ├── hardware.md           ← CPU, PCIe, USB baseline inventory
│   ├── firmware.md           ← UEFI/BIOS measurements & checksums
│   ├── memory.md             ← Memory layout, protection features
│   ├── crypto.md             ← Cryptographic capabilities baseline
│   └── security.md           ← Hardware security features status
├── trust/
│   ├── boot-chain.md         ← Trusted boot components & signatures
│   ├── hardware.md           ← Whitelisted hardware (PCIe IDs, etc.)
│   ├── firmware.md           ← Trusted firmware versions & hashes
│   ├── processes.md          ← Global trusted process whitelist
│   └── certificates.md       ← Trusted certificate authorities
├── firmware/
│   ├── uefi-dumps/           ← UEFI firmware dump archives
│   ├── bios-backups/         ← BIOS backup images
│   ├── spi-dumps/            ← SPI flash dumps
│   └── measurements.log      ← TPM measurements & PCR values
├── hardware/
│   ├── pci-snapshots/        ← PCIe device configuration snapshots
│   ├── usb-events/           ← USB device insertion/removal logs
│   ├── dma-logs/             ← DMA transaction monitoring
│   └── timing-analysis/      ← Hardware timing attack detection
├── crypto/
│   ├── key-material/         ← Cryptographic key archives
│   ├── certificates/         ← Certificate chain validation
│   ├── signatures/           ← Digital signature verification
│   └── entropy-analysis/     ← Hardware RNG quality assessment
├── attack-surface/
│   ├── vulnerabilities.md    ← Known system vulnerabilities
│   ├── mitigations.md        ← Applied security mitigations
│   ├── threat-model.md       ← System-wide threat assessment
│   └── hardening-status.md   ← Current hardening implementation
├── forensics/
│   ├── memory-captures/      ← Critical event memory dumps
│   ├── evidence-archive/     ← Long-term evidence preservation
│   ├── chain-of-custody/     ← Evidence handling documentation
│   └── analysis-results/     ← Forensic analysis outcomes
└── global-intelligence/
    ├── ioc-global.md         ← System-wide IOCs across all projects
    ├── threat-actors.md      ← Known threat actor profiles
    ├── techniques.md         ← Observed attack techniques
    └── countermeasures.md    ← Effective defense strategies
```

---

## Forensic Intelligence Sharing

### Cross-Project IOC Correlation
- **Hardware implant signatures** → shared across all investigations
- **Firmware rootkit patterns** → global threat intelligence
- **Attack technique fingerprints** → behavioral pattern recognition
- **Evasion technique libraries** → anti-forensic countermeasures

### Evidence Preservation Standards
- **Chain of custody** → cryptographically signed evidence logs
- **Integrity verification** → multiple hash algorithms, timestamps
- **Long-term preservation** → format migration, redundant storage
- **Access logging** → audit trail for all evidence access

---

## Anti-Forensic Countermeasures

### 🕵️ **Log Tampering Detection**
```bash
# Detect journal manipulation
journalctl --verify
ausearch -m SYSCALL --success=no -x rm,unlink | grep -i log

# File system timeline analysis
find /var/log -name "*.log" -printf "%T@ %p\n" | sort -n
```

### 🔍 **Memory Artifact Recovery**
```bash
# Capture critical memory regions
sudo dd if=/proc/kcore of=/tmp/kcore.dump bs=1M count=100 2>/dev/null
strings /tmp/kcore.dump | grep -E "(password|token|key)" | head -20

# Process memory analysis
for pid in $(ps -eo pid --no-headers); do
  sudo cat /proc/$pid/maps 2>/dev/null | grep -v ".so\|heap\|stack" || true
done
```

### 🛡️ **Steganography Detection**
```bash
# File entropy analysis
for file in $(find /tmp -type f -size +1k 2>/dev/null | head -10); do
  entropy=$(xxd "$file" | head -1000 | wc -c)
  echo "$file: entropy=$entropy"
done

# Network timing analysis
tcpdump -i any -c 1000 -tt | awk '{print $1}' | head -50
```

---

## Hardware Security Assessment

### 🔧 **Hardware Attack Surface**
```bash
# Check DMA protection
dmesg | grep -i iommu
cat /proc/iomem | grep -i "dma\|mmio"

# Analyze PCIe attack vectors  
lspci -vv | grep -A5 -B5 "DMA\|MSI\|Capabilities"

# USB attack surface
lsusb -v | grep -A10 -B2 "bDeviceClass\|bInterfaceClass"

# Firmware attack indicators
sudo dmidecode -t bios | grep -E "Version|Date|Characteristics"
```

### 🛡️ **Hardware Hardening Verification**
```bash
# Verify hardware security features
grep -r "smep\|smap\|cet\|pac" /proc/cpuinfo
dmesg | grep -i "nx\|dep\|aslr\|kaslr"

# Check secure boot status
mokutil --sb-state 2>/dev/null || echo "SecureBoot: Not available"
efibootmgr 2>/dev/null | head -10 || echo "UEFI: Not available"

# Memory protection verification
cat /proc/sys/kernel/randomize_va_space
cat /proc/sys/kernel/kptr_restrict
```

---

## Defense Strategy Integration

### 🚨 **Real-Time Monitoring**
- **Hardware event correlation** → cross-reference PCIe, USB, DMA events
- **Firmware integrity monitoring** → continuous UEFI/BIOS verification
- **Memory protection alerts** → detection of memory-based attacks
- **Cryptographic anomalies** → hardware RNG manipulation detection

### 🔧 **Adaptive Hardening**
- **Dynamic threat response** → auto-apply mitigations for new threats
- **Progressive hardening** → increase security based on threat level
- **Attack technique adaptation** → evolve defenses based on observed TTPs
- **Hardware utilization** → leverage available security features

---

## Rules for Agents

1. **Always verify hardware integrity** before proceeding with investigations
2. **Maintain forensic evidence preservation** standards throughout
3. **Cross-correlate with global intelligence** for threat actor attribution
4. **Document all anti-forensic techniques** encountered for future reference
5. **Update hardware baselines** only after thorough verification
6. **Preserve chain of custody** for all collected evidence
7. **Monitor for firmware modifications** during all investigation phases
8. **Apply progressive hardening** based on detected threat sophistication
9. **Share critical IOCs globally** across all system-layer projects
10. **Maintain cryptographic integrity** of all forensic artifacts

---

**Ready for system-wide forensic intelligence operations.**
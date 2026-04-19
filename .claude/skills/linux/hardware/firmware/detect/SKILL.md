---
name: hardware-firmware-detect
description: Firmware and bootloader forensic reconnaissance. UEFI/BIOS integrity, Secure Boot key chain, TPM PCR state, initramfs inspection, GRUB configuration, ACPI table analysis, and firmware rootkit/implant detection.
model: opus
maxTurns: 30
tools:
  - Read
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
skills:
  - shared-memory
  - threats/mitre-attack-mapper
tags:
- kernel
- firmware
- firmware-recon
mitre_attack:
- T1014
- T1059
- T1195
- T1547
- T1595
nist_csf: []
capec: []
---

# Firmware Recon

**Purpose:** Boot and firmware-focused reconnaissance for high-impact persistence vectors. Detects UEFI/BIOS rootkits, Secure Boot bypass, initramfs tampering, and supply-chain firmware implants.

---

## Core Focus Areas

- **UEFI/BIOS integrity**: Version fingerprinting, checksum baseline, SPI flash dump comparison
- **Secure Boot chain**: PK/KEK/db/dbx key inventory, MOK analysis, boot entry manipulation
- **TPM 2.0 state**: PCR values, EK certificate, NV index inventory, sealed key audit
- **initramfs analysis**: Embedded scripts, unexpected binaries, hook injection
- **GRUB configuration**: Custom commands, modules, password bypass indicators
- **ACPI tables**: DSDT/SSDT injection for persistent code execution
- **Firmware update history**: fwupd logs, version rollbacks, unauthorized updates
- **Hardware implant indicators**: Unexpected PCIe devices, DMA anomalies, USB implants

---

## Key Techniques & Tools

### UEFI/BIOS Fingerprinting
```bash
# BIOS version, date, vendor
sudo dmidecode -t bios 2>/dev/null | grep -E "(Vendor|Version|Release|Revision|Char)"

# Full DMI table
sudo dmidecode 2>/dev/null | head -80

# UEFI variable listing
efivar --list 2>/dev/null | head -30
efibootmgr -v 2>/dev/null

# UEFI boot order and entries
efibootmgr --unicode 2>/dev/null

# Check for rogue UEFI boot entries (not in expected list)
efibootmgr -v 2>/dev/null | grep -v "^Boot000[0-9]" | grep -E "^Boot[0-9]{4}"
```

### Secure Boot Key Chain
```bash
# Secure Boot status
mokutil --sb-state 2>/dev/null

# Platform Key (PK)
mokutil --pk 2>/dev/null | openssl x509 -noout -text 2>/dev/null | \
  grep -E "(Subject|Issuer|Not After)"

# Key Exchange Keys (KEK)
mokutil --kek 2>/dev/null | grep -E "(Subject|Issuer|CN=)"

# Authorized (db) and revoked (dbx)
mokutil --db 2>/dev/null | grep -E "(Subject|Issuer|SHA)"
mokutil --dbx 2>/dev/null | head -10

# MOK (Machine Owner Keys) — user-enrolled keys
mokutil --list-enrolled 2>/dev/null | grep -E "(Subject|SHA|Finger)"

# All UEFI signature lists
for db in PK KEK db dbx; do
  echo "=== $db ==="
  efi-readvar -v "$db" 2>/dev/null | head -10
done
```

### TPM 2.0 Analysis
```bash
# TPM device info
cat /sys/class/tpm/tpm0/tpm_version_major 2>/dev/null
cat /sys/class/tpm/tpm0/description 2>/dev/null

# PCR values — PCR[0-7] cover firmware and boot path
tpm2_pcrread sha256:0,1,2,3,4,5,6,7 2>/dev/null

# Expected PCR values vs baseline
tpm2_pcrread sha256 2>/dev/null | diff - ./cybersec-shared/baselines/tpm_pcr_baseline.txt 2>/dev/null || \
  echo "No baseline available — document current values"

# EK (Endorsement Key) certificate
tpm2_getekcertificate -o /tmp/ek_cert.pem 2>/dev/null && \
  openssl x509 -in /tmp/ek_cert.pem -noout -text 2>/dev/null | \
  grep -E "(Subject|Issuer|Not After|Serial)"

# Persistent TPM handles (sealed secrets, bound keys)
tpm2_getcap handles-persistent 2>/dev/null

# NV indexes (EK cert locations)
tpm2_getcap handles-nv-index 2>/dev/null

# TPM audit log
tpm2_eventlog /sys/kernel/security/tpm0/binary_bios_measurements 2>/dev/null | head -40
```

### initramfs Inspection
```bash
# Extract and inspect initramfs content
INITRAMFS=$(ls /boot/initramfs-linux*.img 2>/dev/null | head -1)
[ -z "$INITRAMFS" ] && INITRAMFS=$(ls /boot/initrd*.img 2>/dev/null | head -1)

# lsinitcpio (Arch/Garuda)
lsinitcpio -l "$INITRAMFS" 2>/dev/null | head -50

# Analyze hooks in initramfs
lsinitcpio -a "$INITRAMFS" 2>/dev/null | head -20

# Extract to temp dir and inspect
mkdir -p /tmp/initramfs_extract
lsinitcpio -x "$INITRAMFS" -d /tmp/initramfs_extract/ 2>/dev/null || \
  (cd /tmp/initramfs_extract && zcat "$INITRAMFS" | cpio -i 2>/dev/null)

# Look for unexpected executables in initramfs
find /tmp/initramfs_extract -type f -executable 2>/dev/null | head -20
find /tmp/initramfs_extract -name "*.sh" 2>/dev/null | xargs grep -l "curl\|wget\|nc\|ncat" 2>/dev/null

# Checksum comparison
sha256sum "$INITRAMFS" 2>/dev/null
```

### GRUB Analysis
```bash
# GRUB configuration
cat /boot/grub/grub.cfg 2>/dev/null | grep -E "(menuentry|set|linux|initrd|password)" | head -30

# GRUB environment block
grub-editenv list 2>/dev/null

# Unexpected GRUB modules loaded
ls /boot/grub/$(uname -m)-efi/ 2>/dev/null | grep -v "^normal\|^boot\|^linux\|^chain"

# Check GRUB password protection
grep -i "password" /boot/grub/grub.cfg 2>/dev/null | head -5

# GRUB2 superuser check
grep "set superusers\|password_pbkdf2" /boot/grub/grub.cfg 2>/dev/null
```

### ACPI Table Analysis
```bash
# Dump ACPI tables
acpidump -o /tmp/acpi_tables.dat 2>/dev/null
acpixtract -a /tmp/acpi_tables.dat 2>/dev/null

# Decompile DSDT (primary ACPI definition table)
iasl -d /tmp/dsdt.dat 2>/dev/null
grep -iE "(Execute|Load|Store|_INI|_PTS)" /tmp/dsdt.dsl 2>/dev/null | head -20

# Check for SSDT overlays (common injection technique)
ls /tmp/ssdt*.dat 2>/dev/null | wc -l
cat /sys/firmware/acpi/tables/SSDT* 2>/dev/null | strings | head -20
```

### Firmware Update History
```bash
# fwupd history — check for unauthorized updates or version rollbacks
fwupdmgr get-history 2>/dev/null | head -30

# Currently installed firmware versions
fwupdmgr get-devices 2>/dev/null | head -40

# Check for pending or available updates
fwupdmgr get-updates 2>/dev/null | head -20

# fwupd daemon logs
journalctl -u fwupd --since "30 days ago" 2>/dev/null | \
  grep -E "(install|downgrade|update|error)" | head -20
```

### Hardware Implant Indicators
```bash
# PCIe device inventory — compare against baseline
lspci -vv 2>/dev/null | grep -E "(VendorID|DeviceID|SubVendorID|^[0-9])" | head -30
lspci -mm 2>/dev/null > /tmp/pci_live.txt

# DMA protection status
dmesg | grep -iE "(iommu|dmar|vt-d|amd-vi)" | head -10
cat /proc/iomem | grep -i "reserved\|unusable" | head -10

# USB device inventory
lsusb -v 2>/dev/null | grep -E "(idVendor|idProduct|iManufacturer|iProduct|bDeviceClass)" | head -30

# Unexpected USB devices (compare against baseline)
lsusb 2>/dev/null | sort > /tmp/usb_live.txt
diff ./cybersec-shared/baselines/usb_devices.txt /tmp/usb_live.txt 2>/dev/null | head -10
```

---

## MITRE ATT&CK Mapping

| Finding | Technique |
|---------|-----------|
| UEFI/BIOS modification | T1542.001 – System Firmware |
| Secure Boot bypass / rogue key | T1542.003 – Bootkit |
| MOK enrollment of attacker key | T1553.004 – Install Root Certificate |
| initramfs backdoor | T1542.004 – ROMMONkit (equiv.) |
| ACPI table injection | T1542 – Pre-OS Boot |
| Unauthorized firmware downgrade | T1195.003 – Compromise Hardware Supply Chain |
| PCIe/USB hardware implant | T1200 – Hardware Additions |

---

## Rules for Agents

1. TPM PCR value changes vs baseline = **CRITICAL** — escalate to CYBERSEC-AGENT immediately
2. Rogue UEFI boot entry not in baseline = **CRITICAL**
3. Unexpected MOK enrolled key = **HIGH**
4. initramfs with network tools (curl/wget/nc) = **HIGH**
5. Unauthorized firmware downgrade in fwupd history = **HIGH**
6. Always baseline PCR values and UEFI boot entries at session start
7. Sync all firmware IOCs to shared memory at session end

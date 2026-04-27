# IOC Database — Project-Level
> Last updated: {{TIMESTAMP}}  
> Total IOCs: {{IOC_COUNT}}  
> Sessions contributing: {{SESSION_COUNT}}

> Structured around `Forensic IOCEntry`; may also be cross-linked to canonical `IOCDatabaseEntry` records.

---

## Confidence Auto-Escalation
| Sightings   | Minimum Confidence |
|-------------|--------------------|
| 1 session   | Keep original      |
| 2 sessions  | → `High`           |
| 3+ sessions | → `Confirmed`      |

## Status Values
- `active` — currently observed / actionable
- `watching` — under monitoring, not yet fully confirmed
- `cleared` — confirmed benign / false positive (also in `cleared.md`)
- `expired` — retained for history but no longer operationally relevant

---

## Network IOCs
| IOC ID | Type | Value | Context | First Session | Last Session | Sightings | Confidence | Severity | Status | Source | TLP |
|--------|------|-------|---------|---------------|--------------|-----------|------------|----------|--------|--------|-----|
{{NETWORK_IOCS}}

## File IOCs
| IOC ID | Type | Value | Path / Location | First Session | Last Session | Sightings | Confidence | Severity | Status | Source | TLP |
|--------|------|-------|-----------------|---------------|--------------|-----------|------------|----------|--------|--------|-----|
{{FILE_IOCS}}

## Process IOCs
| IOC ID | Type | Value | Context | First Session | Last Session | Sightings | Confidence | Severity | Status | Source | TLP |
|--------|------|-------|---------|---------------|--------------|-----------|------------|----------|--------|--------|-----|
{{PROCESS_IOCS}}

## Persistence IOCs
| IOC ID | Type | Value | Context | First Session | Last Session | Sightings | Confidence | Severity | Status | Source | TLP |
|--------|------|-------|---------|---------------|--------------|-----------|------------|----------|--------|--------|-----|
{{PERSISTENCE_IOCS}}

## eBPF IOCs
| IOC ID | Type | Value | Context | First Session | Last Session | Sightings | Confidence | Severity | Status | Source | TLP |
|--------|------|-------|---------|---------------|--------------|-----------|------------|----------|--------|--------|-----|
{{EBPF_IOCS}}

## Memory IOCs
| IOC ID | Type | Value | Context | First Session | Last Session | Sightings | Confidence | Severity | Status | Source | TLP |
|--------|------|-------|---------|---------------|--------------|-----------|------------|----------|--------|--------|-----|
{{MEMORY_IOCS}}

## Firmware / Boot IOCs
| IOC ID | Type | Value | Context | First Session | Last Session | Sightings | Confidence | Severity | Status | Source | TLP |
|--------|------|-------|---------|---------------|--------------|-----------|------------|----------|--------|--------|-----|
{{FIRMWARE_IOCS}}

## Log / Event IOCs
| IOC ID | Type | Value | Context | First Session | Last Session | Sightings | Confidence | Severity | Status | Source | TLP |
|--------|------|-------|---------|---------------|--------------|-----------|------------|----------|--------|--------|-----|
{{LOG_IOCS}}

## Account / Credential IOCs
| IOC ID | Type | Value | Context | First Session | Last Session | Sightings | Confidence | Severity | Status | Source | TLP |
|--------|------|-------|---------|---------------|--------------|-----------|------------|----------|--------|--------|-----|
{{CREDENTIAL_IOCS}}

---

## Merge Rules
- ID format: `IOC-NNNN` (sequential, never reused)
- **New IOC:** assign next ID, set `Sightings=1`, copy confidence from session
- **Existing IOC (same Value):** increment `Sightings`, update `Last Session`, apply auto-escalation, merge context
- **Never downgrade** confidence — only escalate or keep
- **Never delete** — only change status to `cleared` or `expired`

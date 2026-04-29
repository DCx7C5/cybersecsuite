# Kernel Baseline
> Captured: {{TIMESTAMP}}  
> Session: {{SESSION_ID}}

> Structured around `KernelBaseline`.

| Field | Value |
|-------|-------|
| Snapshot Hash | `{{SNAPSHOT_HASH}}` |
| Confirmed Clean | {{CONFIRMED_CLEAN}} |

## Kernel Version
`{{KERNEL_VERSION}}`

## Boot Parameters
`{{KERNEL_CMDLINE}}`

## Expected Taint Value
`{{TAINT_VALUE}}` — Reason: {{TAINT_REASON}}

## eBPF Programs (expected)
| ID | Type | Name | Attached To | Owner UID |
|----|------|------|-------------|-----------|
{{EBPF_PROGRAMS}}

## eBPF Maps (expected)
| ID | Type | Name | Key Size | Value Size | Max Entries |
|----|------|------|----------|------------|-------------|
{{EBPF_MAPS}}

## Security Settings (`security_settings` JSON)
| Key | Expected Value | Notes |
|-----|----------------|-------|
{{SECURITY_SETTINGS}}

## Linux Security Module (LSM)
`{{LSM_STATUS}}` <!-- e.g., "apparmor", "selinux (enforcing)", "none" -->

## Notes
{{NOTES}}


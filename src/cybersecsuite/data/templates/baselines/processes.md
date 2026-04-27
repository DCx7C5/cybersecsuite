# Process Baseline
> Captured: {{TIMESTAMP}}  
> Session: {{SESSION_ID}}

> Structured around `ProcessBaseline`.

| Field | Value |
|-------|-------|
| Snapshot Hash | `{{SNAPSHOT_HASH}}` |
| Confirmed Clean | {{CONFIRMED_CLEAN}} |

## Process Count (cross-check)
| Source         | Count                              |
|----------------|------------------------------------|
| `ps aux`       | {{PS_COUNT}}                       |
| `/proc/[0-9]*` | {{PROC_COUNT}}                     |
| **Delta**      | **{{DELTA}}** (>5 = rootkit alert) |

## Running Processes (known-good snapshot)
| PID | User | Process | Cmdline | Notes |
|-----|------|---------|---------|-------|
{{RUNNING_PROCESSES}}

## Running Deleted Executables (expected: none)
| PID | EXE (deleted) | Cmdline | Notes |
|-----|---------------|---------|-------|
{{DELETED_EXES}}

## Known-Good Services
| Service | Expected Owner | Binary Path | Binary SHA-256 | Notes |
|---------|----------------|-------------|----------------|-------|
{{SERVICES}}

## Known-Good Kernel Modules
| Module | Size | Used By | Notes |
|--------|------|---------|-------|
{{KERNEL_MODULES}}

## Module Count (cross-check)
| Source        | Count                                           |
|---------------|-------------------------------------------------|
| lsmod         | {{LSMOD_COUNT}}                                 |
| /proc/modules | {{PROC_MODULES_COUNT}}                          |
| **Delta**     | **{{MODULE_DELTA}}** (>0 = hidden module alert) |

## Notes
{{NOTES}}


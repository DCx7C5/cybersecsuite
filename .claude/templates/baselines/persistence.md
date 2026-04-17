# Persistence Baseline
> Captured: {{TIMESTAMP}}  
> Session: {{SESSION_ID}}

> Structured around `PersistenceBaseline`.

| Field | Value |
|-------|-------|
| Snapshot Hash | `{{SNAPSHOT_HASH}}` |
| Confirmed Clean | {{CONFIRMED_CLEAN}} |

## Enabled Systemd Units (system)
| Unit | Status | Binary Path | Notes |
|------|--------|-------------|-------|
{{SYSTEMD_SYSTEM_UNITS}}

## Enabled Systemd Units (user)
| Unit | Status | Binary Path | Notes |
|------|--------|-------------|-------|
{{SYSTEMD_USER_UNITS}}

## Package Manager Hooks
| Hook | Package/Manager | Owned | Notes |
|------|-----------------|-------|-------|
{{PACKAGE_HOOKS}}

## Shell Config Hashes
| File | SHA-256 | Notes |
|------|---------|-------|
{{SHELL_CONFIGS}}

## XDG Autostart Entries
| Desktop File | Exec | Owned By Pkg | Notes |
|--------------|------|-------------|-------|
{{AUTOSTART_ENTRIES}}

## Cron / Timers
| Entry | Schedule | Owner | Notes |
|-------|----------|-------|-------|
{{CRON_ENTRIES}}

## udev Rules (non-default)
| Rule File | Content Summary | Owned By Pkg | Notes |
|-----------|-----------------|-------------|-------|
{{UDEV_RULES}}

## Notes
{{NOTES}}


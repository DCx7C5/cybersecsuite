# Network Baseline
> Captured: {{TIMESTAMP}}  
> Session: {{SESSION_ID}}

> Structured around `NetworkBaseline`.

| Field | Value |
|-------|-------|
| Snapshot Hash | `{{SNAPSHOT_HASH}}` |
| Confirmed Clean | {{CONFIRMED_CLEAN}} |

## Interfaces
| Interface | MAC | IP | State | Flags | Notes |
|-----------|-----|-----|-------|-------|-------|
{{INTERFACES}}

## ARP Table (known-good)
| IP | MAC | Interface | State | Notes |
|----|-----|-----------|-------|-------|
{{ARP_TABLE}}

## Listening Ports (expected)
| Port | Proto | Process | PID | Bind Address | Notes |
|------|-------|---------|-----|-------------|-------|
{{LISTENING_PORTS}}

## Established Connections (baseline snapshot)
| Local | Remote | Process | PID | Notes |
|-------|--------|---------|-----|-------|
{{ESTABLISHED_CONNECTIONS}}

## Routes (expected)
| Destination | Gateway | Interface | Metric | Notes |
|-------------|---------|-----------|--------|-------|
{{ROUTES}}

## Firewall Rules Hash
`{{FIREWALL_RULES_HASH}}`

## Notes
{{NOTES}}

# Timeline — {{DATE}}
> Session: {{SESSION_ID}}

> Structured around `Timeline` entries.

| Timestamp      | Phase | Event                                                                       | Severity | IOC Ref | Artifact Ref | Command Ref |
|----------------|-------|-----------------------------------------------------------------------------|----------|---------|--------------|-------------|
| {{START_TIME}} | init  | Session created                                                             | info     | —       | —            | —           |
| {{START_TIME}} | init  | Shared memory loaded ({{IOCS_LOADED}} IOCs, {{WATCHLIST_LOADED}} watchlist) | info     | —       | shared-memory | —          |
{{TIMELINE_ENTRIES}}

<!-- Append a row for every: phase change, finding, IOC discovery, command with significant output, escalation -->
<!-- IOC Ref maps to Timeline.ioc_reference; Artifact Ref maps to artifact_reference; Command Ref maps to command_reference -->

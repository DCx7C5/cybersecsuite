# Session Index
> Last updated: {{TIMESTAMP}}  
> Total sessions: {{TOTAL_SESSIONS}}

> Structured around `ForensicSession`.

| Session ID | Start | End | Investigator | Agent | Phase | Status | Duration | Findings | IOCs | New IOCs | Severity Summary | Verdict | Storage Path |
|------------|-------|-----|--------------|-------|-------|--------|----------|----------|------|----------|------------------|---------|--------------|
{{SESSION_ENTRIES}}

## Statistics
| Metric                          | Value                 |
|---------------------------------|-----------------------|
| Total sessions                  | {{TOTAL_SESSIONS}}    |
| Total unique IOCs               | {{TOTAL_UNIQUE_IOCS}} |
| Sessions with critical findings | {{CRITICAL_SESSIONS}} |
| Most recent verdict             | {{LATEST_VERDICT}}    |

## Rules
- Append one row per completed session
- `New IOCs` = IOCs not previously in `ioc-db.md` (delta count)
- `Severity Summary` = serialized `severity_summary` from the session manifest (e.g., `critical=2,high=3,medium=5,low=1`)
- `Verdict` = `verdict` from the session manifest / `ForensicSession`
- `Duration` = `end_time - start_time` from session manifest

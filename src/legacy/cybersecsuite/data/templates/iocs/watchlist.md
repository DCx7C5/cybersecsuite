# Watchlist — Active Monitoring Targets
> Last updated: {{TIMESTAMP}}  
> Active items: {{WATCHLIST_COUNT}}

> Structured around `ForensicWatchlistItem`.

| Watchlist ID | Type | Value | Pattern | Reason | Added By Session | Priority | Clean Checks | Last Checked | Status | Escalated IOC | Expires At |
|--------------|------|-------|---------|--------|------------------|----------|--------------|--------------|--------|---------------|------------|
{{WATCHLIST_ENTRIES}}

## Priority Levels
- **Critical**: MUST check every session — potential active compromise indicator
- **High**: MUST check every session — suspicious but unconfirmed
- **Medium**: Check if relevant to current investigation phase
- **Low**: Check opportunistically

## Status Values
- `watching` — actively being tracked
- `cleared` — moved to `cleared.md` (confirmed benign)
- `expired` — no longer worth active monitoring

> Promotion to `ioc-db.md` is represented by `Escalated IOC`, not by a separate status enum.

## Rules
- Every new session MUST re-check all `Critical` and `High` watchlist items
- Update `Last Checked` with session ID after each re-check
- Increment `Clean Checks` for each session where the item was not observed
- Reset `Clean Checks` to 0 if the item reappears
- Move to `cleared.md` (status → `cleared`) after `Clean Checks` ≥ 3
- If confirmed malicious, keep `status=watching`, set `Escalated IOC`, and link the promoted `IOC ID`

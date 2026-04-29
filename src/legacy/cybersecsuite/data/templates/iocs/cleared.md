# Cleared Items — Confirmed False Positives
> Last updated: {{TIMESTAMP}}  
> Total cleared: {{CLEARED_COUNT}}

> Structured around `ClearedItem`.

| Cleared ID | Type | Value | Reason Cleared | Cleared By Session | Cleared By Investigator | Date Cleared | Clean Checks Before Clearing | Review Date | Recheck If |
|------------|------|-------|----------------|--------------------|-------------------------|--------------|------------------------------|-------------|------------|
{{CLEARED_ENTRIES}}

## Rules
- **Never re-flag** a cleared item unless the `Recheck If` condition is met
- `Recheck If` describes what would invalidate the clearance (e.g., "file hash changes", "service config modified", "new user added")
- An item can be un-cleared by explicitly removing it and documenting why
- `Clean Checks Before Clearing` tracks how many consecutive sessions verified this as benign before it was cleared
- When un-clearing: move back to `watchlist.md` with priority `High` and document the reason

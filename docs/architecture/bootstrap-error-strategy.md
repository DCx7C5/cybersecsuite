# Bootstrap Error Handling Strategy

## Philosophy: Graceful Degradation

If `OnFirstSetupEvent` encounters errors during marketplace item installation, **bootstrap completes partially** rather than failing entirely. This allows the system to start and retry later.

## Error Handling by Phase

### Phase 1: Read Global Settings
**Action**: Fail hard (no globals = data corruption)
```
Status: reading_globals
If error: mark_failed("Failed to read ~/.claude/settings.json")
         → User must manually investigate
         → Exit with clear error message
```

### Phase 2: Download Index + SHA512 Check
**Action**: Fail hard (cannot trust index without SHA verification)
```
Status: checking_sha512
If error: mark_failed("Failed to verify index.json SHA512")
         → Potentially malicious index
         → Exit with security warning
         → User can manually retry
```

### Phase 3: Seed MarketplaceRegistry from Index
**Action**: Fail soft (registry can be empty, user adds items manually)
```
Status: seeding_db
If error: log warning, continue to Phase 4
         → System starts with empty registry
         → User can install items from dashboard later
```

### Phase 4: Download Core Marketplace Items
**Action**: Fail soft per-item (record failures, continue others)
```
Status: downloading_items
For each core item:
  - Try install via PackageInstaller
  - Success: record_installed(item_id)
  - Failure: record_failed(item_id, reason)
            → Log warning, show in dashboard
            → Continue with next item
            → Do NOT block bootstrap
After all items:
  - If any succeeded: mark bootstrap as partially_complete
  - If all failed: mark as failed with summary
  - User can retry via dashboard "Retry Failed Installations" button
```

## BootstrapStatus Integration

```python
# In OnFirstSetupEvent
status = BootstrapStatus.load() or BootstrapStatus()

try:
    status.advance_phase("reading_globals")
    globals = read_globals()
    
    status.advance_phase("checking_sha512")
    verify_sha512()
    
    status.advance_phase("seeding_db")
    try:
        seed_marketplace_registry(index)
    except Exception as e:
        log.warning(f"Registry seed failed: {e}")
    
    status.advance_phase("downloading_items")
    for item in core_items:
        try:
            installer.install(item)
            status.record_installed(item["id"])
        except Exception as e:
            log.warning(f"Failed to install {item['id']}: {e}")
            status.record_failed(item["id"], str(e))
    
    # Mark complete even if some items failed
    status.mark_complete()
    
except CriticalError as e:
    status.mark_failed(str(e))
    raise  # Exit with error
```

## Dashboard Recovery UI

**Installed tab** shows:

```
CORE ITEMS
  ✓ ai-marketplace       (installed 2025-04-28)
  ✗ vault-mcp           (failed: connection timeout) [Retry]
  ✓ canvas-mcp          (installed 2025-04-28)

[Retry All Failed]
```

Clicking `[Retry]` on individual item or `[Retry All Failed]`:
- Show progress spinner
- Call `/api/marketplace/install/{item_id}` 
- Update status in real time
- Show success/failure message

## Error Categories

### Non-Recoverable (Fail Hard)
- SHA512 mismatch (security threat)
- ~/.claude/ not readable (permission/corruption)
- Invalid index JSON schema (malformed)

### Recoverable (Fail Soft)
- Network timeout (transient)
- Connection refused (service down)
- Disk space full (can retry later)
- Item already installed (skip)
- Dependency missing (recommend in UI)

### Best-Effort (Warn + Continue)
- Seeding registry fails (use empty registry)
- One core item install fails (try others)
- Telemetry send fails (silent)

## Testing Strategy

**Unit tests** for error scenarios:

```python
def test_bootstrap_recovers_from_network_timeout():
    """If one item times out, bootstrap continues."""
    status = BootstrapStatus()
    # Mock PackageInstaller to fail on one item, succeed on others
    # Assert: status.mark_complete() called
    # Assert: status.failed_items = {"vault-mcp": "timeout"}
    # Assert: status.installed_items = ["ai-marketplace", "canvas-mcp"]

def test_bootstrap_fails_hard_on_sha_mismatch():
    """If SHA doesn't match, bootstrap fails entirely."""
    # Mock sha512_verify to fail
    # Assert: status.mark_failed() called
    # Assert: bootstrap exits

def test_bootstrap_resumes_after_crash():
    """If bootstrap crashed at phase 3, resume from phase 4."""
    # Create existing BootstrapStatus at phase 2
    # Call OnFirstSetupEvent again
    # Assert: starts at phase 3, doesn't re-download index
```

---

**Version**: 1.0
**Last Updated**: 2025-04-28

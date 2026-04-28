# Backward Compatibility Strategy

## Scenario

User has manually installed marketplace items **before** bootstrap runs:

```
~/.cybersecsuite/agents/
└── analyst/              # Manually installed v1.0.0
```

Bootstrap is about to install the same item from index.json:

```json
{
  "id": "analyst",
  "version": "1.5.0",
  "source": "https://..."
}
```

**Question**: Should we upgrade, preserve, or merge?

## Recommended: Version-Aware Upgrade

**Default behavior**: If installed version < index version, upgrade automatically.

```python
def install_item(item: dict) -> InstallResult:
    """Install item, upgrading if newer version available."""
    item_id = item["id"]
    index_version = item["version"]
    
    # Check if already installed
    existing = MarketplaceRegistry.get(item_id)
    if existing:
        existing_version = existing.get("version")
        if version_tuple(existing_version) >= version_tuple(index_version):
            log.info(f"{item_id}: {existing_version} already installed, skipping")
            return InstallResult(status="skipped", reason="already_installed")
        else:
            log.info(f"{item_id}: upgrading {existing_version} → {index_version}")
            # Backup old version
            backup_path = make_backup(item_id, existing_version)
            try:
                download_and_install(item)
                log.info(f"Upgraded {item_id}; backup at {backup_path}")
                return InstallResult(status="upgraded", backup=backup_path)
            except Exception as e:
                restore_from_backup(item_id, backup_path)
                raise
    else:
        # New item, install normally
        download_and_install(item)
        return InstallResult(status="installed")
```

## Backup Strategy

When upgrading an existing item:

1. Copy current install to `~/.cybersecsuite/marketplace/.backups/{item_id}-{old_version}/`
2. Install new version
3. On failure: restore from backup atomically
4. User can manually restore old version from backup dir if needed

```
~/.cybersecsuite/marketplace/
├── .backups/
│   ├── analyst-1.0.0/        # Backup from upgrade
│   │   └── agent.json
│   └── vault-mcp-1.2.0/
│       └── manifest.json
├── agents/
│   └── analyst/               # Current: v1.5.0
└── mcps/
    └── vault-mcp/             # Current: v1.3.0
```

## Alternative: Preserve User Installs

If user has locally modified item (detected by file hash or marker):

```python
def install_item(item: dict) -> InstallResult:
    """Install item, preserving user modifications."""
    item_id = item["id"]
    
    existing = MarketplaceRegistry.get(item_id)
    if existing and existing.get("user_modified"):
        log.info(f"{item_id}: user-modified, preserving existing")
        return InstallResult(status="skipped", reason="user_modified")
    
    # Otherwise, upgrade normally
    ...
```

## Dashboard UI

**Marketplace/Installed tab**:

```
INSTALLED ITEMS
  • analyst (v1.0.0)
    └─ Newer available: v1.5.0 [Update] [Backup]
  • vault-mcp (v2.1.0)
    └─ Up to date
```

Clicking `[Update]`:
- Shows confirmation dialog
- Lists what will change
- Starts upgrade with progress bar
- Shows success or "backup restored" message

## Configuration

In `src/registries/marketplace.py`:

```python
UPGRADE_STRATEGY = "version-aware"  # or "preserve-user" or "always-upgrade"

BACKUP_ENABLED = True              # Keep backups of old versions
BACKUP_MAX_AGE = 30 * 24 * 3600    # Clean up backups older than 30 days
```

## Phase 0.5 Implementation

For bootstrap `OnFirstSetupEvent`:

```python
status = BootstrapStatus.load() or BootstrapStatus()

for item in core_items:
    try:
        result = install_item(item)
        if result.status == "installed":
            status.record_installed(item["id"])
        elif result.status == "upgraded":
            status.record_installed(item["id"])
            log.info(f"Upgraded {item['id']} (backup: {result.backup})")
        elif result.status == "skipped":
            log.debug(f"Skipped {item['id']}: {result.reason}")
    except Exception as e:
        log.warning(f"Failed to install {item['id']}: {e}")
        status.record_failed(item["id"], str(e))
```

---

**Version**: 1.0
**Last Updated**: 2025-04-28

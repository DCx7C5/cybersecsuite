"""Marketplace endpoints — install/uninstall/toggle/upgrade operations."""


import asyncio
import aiohttp
import asyncpg
import frontmatter
import shutil
from pathlib import Path
import re
from css.core.logger import getLogger
from fastapi import APIRouter, HTTPException, Query, status

from css.core.settings.config import MARKETPLACE_CONFIG, POSTGRES_DATABASE
from css.core.db.models.marketplace import MarketplaceItem, MarketplaceMeta
from css.core.enums import MarketplaceItemStatus, MarketplaceItemType
from css.core.marketplace.seeder import MarketplaceSeeder
from css.core.marketplace.registry import emit_marketplace_item_changed
from css.core.marketplace.installer import PackageInstaller
from css.core.marketplace.cache import marketplace_cache

log = getLogger(__name__)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.get("/", response_model=dict)
async def marketplace_root() -> dict:
    """Marketplace root endpoint for browser navigation."""
    return {
        "message": "Marketplace API",
        "links": {
            "status": "/marketplace/status",
            "items": "/marketplace/items?page=1&per_page=20",
            "tags": "/marketplace/tags?tags=security",
        },
    }


def _db_not_ready(error: Exception) -> bool:
    message = str(error)
    return (
        ("default_connection" in message and "cannot be None" in message)
        or "No TortoiseContext is currently active" in message
    )


def _marketplace_db_settings() -> tuple[str, int, str, str, str]:
    host = str(POSTGRES_DATABASE.get("host") or "127.0.0.1")
    port = int(str(POSTGRES_DATABASE.get("port") or "5432"))
    user = str(POSTGRES_DATABASE.get("user") or "cybersec")
    password = str(POSTGRES_DATABASE.get("password") or "change_me")
    database = str(POSTGRES_DATABASE.get("database") or "cybersec_forensics")
    if database == "cybersec":
        database = "cybersec_forensics"
    return host, port, user, password, database


async def _connect_marketplace_db() -> asyncpg.Connection:
    host, port, user, password, database = _marketplace_db_settings()
    return await asyncpg.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )


async def _list_items_sql(
    *,
    kind: MarketplaceItemType | None,
    provider: str | None,
    installed_only: bool,
    enabled_only: bool,
    page: int,
    per_page: int,
) -> dict:
    conditions: list[str] = []
    args: list[object] = []

    if kind:
        args.append(kind.value)
        conditions.append(f"kind = ${len(args)}")
    if installed_only:
        conditions.append("installed_at IS NOT NULL")
    if enabled_only:
        conditions.append("status <> 'disabled'")
    if provider:
        args.append(provider)
        conditions.append(f"meta->>'provider' = ${len(args)}")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    conn = await _connect_marketplace_db()
    try:
        total = await conn.fetchval(f"SELECT COUNT(*) FROM marketplace_item {where}", *args)

        offset = (page - 1) * per_page
        args_with_paging = [*args, per_page, offset]
        rows = await conn.fetch(
            f"""
            SELECT slug, name, description, kind, status, version, meta, installed_at
            FROM marketplace_item
            {where}
            ORDER BY slug
            LIMIT ${len(args) + 1} OFFSET ${len(args) + 2}
            """,
            *args_with_paging,
        )
    finally:
        await conn.close()

    items: list[dict] = []
    for row in rows:
        meta = row["meta"] if isinstance(row["meta"], dict) else {}
        kind_value = str(row["kind"])
        item = {
            "id": row["slug"],
            "name": row["name"],
            "description": row["description"] or "",
            "kind": kind_value,
            "status": str(row["status"]),
            "enabled": str(row["status"]) != "disabled",
            "installed": row["installed_at"] is not None,
            "version": row["version"] or "0.0.0",
            "tags": meta.get("tags", []) if isinstance(meta.get("tags"), list) else [],
        }
        if kind_value == "agent" and "model" in meta:
            item["model"] = meta["model"]
        if kind_value == "agent" and "max_turns" in meta:
            item["max_turns"] = meta["max_turns"]
        if kind_value == "mcp" and "tools_count" in meta:
            item["tools_count"] = meta["tools_count"]
        if kind_value == "skill" and "repository_url" in meta:
            item["repository_url"] = meta["repository_url"]
        items.append(item)

    return {
        "items": items,
        "total": int(total or 0),
        "page": page,
        "per_page": per_page,
    }


async def _status_sql() -> dict:
    conn = await _connect_marketplace_db()
    try:
        total_items = await conn.fetchval("SELECT COUNT(*) FROM marketplace_item")
        installed_items = await conn.fetchval("SELECT COUNT(*) FROM marketplace_item WHERE installed_at IS NOT NULL")
        enabled_items = await conn.fetchval("SELECT COUNT(*) FROM marketplace_item WHERE status <> 'disabled'")
        meta = await conn.fetchrow(
            "SELECT update_available, last_index_check, remote_index_hash, local_index_hash, version "
            "FROM marketplace_meta ORDER BY id LIMIT 1"
        )
    finally:
        await conn.close()

    return {
        "total_items": int(total_items or 0),
        "installed_items": int(installed_items or 0),
        "enabled_items": int(enabled_items or 0),
        "update_available": bool(meta["update_available"]) if meta else False,
        "last_index_check": meta["last_index_check"].isoformat() if meta and meta["last_index_check"] else None,
        "remote_index_hash": meta["remote_index_hash"] if meta else None,
        "local_index_hash": meta["local_index_hash"] if meta else None,
        "version": meta["version"] if meta else None,
    }

async def _get_item_sql(item_id: str) -> dict | None:
    conn = await _connect_marketplace_db()
    try:
        row = await conn.fetchrow(
            """
            SELECT slug, name, description, kind, status, version, meta, installed_at, source_url, install_path
            FROM marketplace_item
            WHERE slug = $1
            """,
            item_id,
        )
    finally:
        await conn.close()

    if row is None:
        return None

    meta = row["meta"] if isinstance(row["meta"], dict) else {}
    kind_value = str(row["kind"])
    item = {
        "id": row["slug"],
        "name": row["name"],
        "description": row["description"] or "",
        "kind": kind_value,
        "status": str(row["status"]),
        "enabled": str(row["status"]) != "disabled",
        "installed": row["installed_at"] is not None,
        "version": row["version"] or "0.0.0",
        "tags": meta.get("tags", []) if isinstance(meta.get("tags"), list) else [],
        "installed_at": row["installed_at"].isoformat() if row["installed_at"] else None,
        "source_url": row["source_url"],
        "install_path": row["install_path"],
        "meta": meta,
    }
    return item

async def _install_item_sql(item_id: str) -> dict:
    conn = await _connect_marketplace_db()
    try:
        row = await conn.fetchrow(
            """
            SELECT slug, kind, source_url, meta, installed_at, install_path
            FROM marketplace_item
            WHERE slug = $1
            """,
            item_id,
        )
        if row is None:
            return {
                "success": False,
                "item_id": item_id,
                "message": "Installation failed",
                "error": f"Package not found: {item_id}",
            }

        if row["installed_at"] is not None:
            return {
                "success": True,
                "item_id": item_id,
                "message": f"Successfully installed {item_id}",
                "installed_path": row["install_path"],
            }

        source_url = str(row["source_url"] or "").strip()
        if not source_url:
            return {
                "success": False,
                "item_id": item_id,
                "message": "Installation failed",
                "error": f"Missing source_url for package: {item_id}",
            }

        installer = PackageInstaller()
        payload = await installer._download_package(source_url)
        meta = row["meta"] if isinstance(row["meta"], dict) else {}
        expected_sha512 = str(meta.get("sha512") or "")
        if not installer._verify_sha512(payload, expected_sha512):
            return {
                "success": False,
                "item_id": item_id,
                "message": "Installation failed",
                "error": f"Checksum verification failed for package: {item_id}",
            }

        item_ref = type(
            "MarketplaceItemRef",
            (),
            {
                "kind": row["kind"],
                "slug": row["slug"],
                "source_url": source_url,
            },
        )()
        target_dir = installer._get_item_target_dir(item_ref)
        target_dir.mkdir(parents=True, exist_ok=True)
        installed_path = installer._write_payload(item=item_ref, payload=payload, target_dir=target_dir)

        await conn.execute(
            """
            UPDATE marketplace_item
            SET install_path = $2, installed_at = NOW(), status = 'installed', updated_at = NOW()
            WHERE slug = $1
            """,
            item_id,
            str(installed_path),
        )
    finally:
        await conn.close()

    await emit_marketplace_item_changed(item_slug=item_id, operation="install")
    marketplace_cache.invalidate(f"item:{item_id}")
    marketplace_cache.invalidate_prefix("items:")
    return {
        "success": True,
        "item_id": item_id,
        "message": f"Successfully installed {item_id}",
        "installed_path": str(installed_path),
    }

async def _uninstall_item_sql(item_id: str) -> dict:
    conn = await _connect_marketplace_db()
    try:
        row = await conn.fetchrow(
            """
            SELECT slug, kind, install_path
            FROM marketplace_item
            WHERE slug = $1
            """,
            item_id,
        )
        if row is None:
            return {
                "success": False,
                "item_id": item_id,
                "message": "Uninstallation failed",
                "error": f"Package not found: {item_id}",
            }

        install_path = str(row["install_path"] or "").strip()
        if install_path:
            path = Path(install_path).expanduser()
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()

        await conn.execute(
            """
            UPDATE marketplace_item
            SET install_path = NULL, installed_at = NULL, status = 'disabled', updated_at = NOW()
            WHERE slug = $1
            """,
            item_id,
        )
    finally:
        await conn.close()

    await emit_marketplace_item_changed(item_slug=item_id, operation="uninstall")
    marketplace_cache.invalidate(f"item:{item_id}")
    marketplace_cache.invalidate_prefix("items:")
    return {
        "success": True,
        "item_id": item_id,
        "message": f"Successfully uninstalled {item_id}",
    }

async def _toggle_item_sql(item_id: str, enabled: bool) -> dict:
    conn = await _connect_marketplace_db()
    try:
        row = await conn.fetchrow(
            "SELECT slug, installed_at FROM marketplace_item WHERE slug = $1",
            item_id,
        )
        if row is None:
            return {
                "success": False,
                "item_id": item_id,
                "enabled": enabled,
                "message": "Toggle failed",
                "error": f"Item not found: {item_id}",
            }

        next_status = "disabled"
        if enabled:
            next_status = "installed" if row["installed_at"] is not None else "enabled"

        await conn.execute(
            "UPDATE marketplace_item SET status = $2, updated_at = NOW() WHERE slug = $1",
            item_id,
            next_status,
        )
    finally:
        await conn.close()

    await emit_marketplace_item_changed(item_slug=item_id, operation="toggle")
    marketplace_cache.invalidate(f"item:{item_id}")
    marketplace_cache.invalidate_prefix("items:")
    return {
        "success": True,
        "item_id": item_id,
        "enabled": enabled,
        "message": f"Item {'enabled' if enabled else 'disabled'} successfully",
    }


def _clean_frontmatter_text(value: object, fallback: str = "") -> str:
    if not isinstance(value, str):
        return fallback
    text = value.strip()
    if text.startswith(">"):
        text = text[1:].strip()
    if text.startswith('"') and text.endswith('"') and len(text) >= 2:
        text = text[1:-1].strip()
    return text or fallback

def _normalize_markdown_preview(raw_markdown: str) -> str:
    try:
        parsed = frontmatter.loads(raw_markdown)
        return frontmatter.dumps(parsed)
    except Exception:
        return raw_markdown

def _resolve_preview_path(install_path: str) -> Path:
    install_root = Path(MARKETPLACE_CONFIG["install_root"]).expanduser().resolve()
    candidate = Path(install_path).expanduser().resolve()
    try:
        candidate.relative_to(install_root)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid install path for preview",
        ) from exc
    return candidate


def _resolve_preview_file(install_path: str) -> Path | None:
    candidate = _resolve_preview_path(install_path)
    if candidate.is_file():
        return candidate
    if not candidate.exists() or not candidate.is_dir():
        return None

    preferred_names = ("README.md", "README.MD", "SKILL.md", "AGENT.md")
    for name in preferred_names:
        direct = candidate / name
        if direct.exists() and direct.is_file():
            return direct

    markdown_files = sorted(path for path in candidate.rglob("*.md") if path.is_file())
    if markdown_files:
        return markdown_files[0]
    return None


def _generated_preview_markdown(*, item_id: str, name: str, description: str, kind: str) -> str:
    return (
        f"# {name}\n\n"
        f"- **ID**: `{item_id}`\n"
        f"- **Type**: `{kind}`\n\n"
        f"{description or 'No description available.'}\n"
    )


def _parse_loose_frontmatter(raw_body: str) -> dict[str, str]:
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", raw_body, flags=re.DOTALL)
    if not frontmatter_match:
        return {}
    block = frontmatter_match.group(1)
    metadata: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in {"name", "description"} and value:
            metadata[key] = value
    return metadata


async def _build_index_items() -> list[dict]:
    marketplace_base_url = MARKETPLACE_CONFIG["base_url"]
    async with MarketplaceSeeder() as seeder:
        index_data = await seeder.fetch_index()

    items: list[dict] = []
    type_key_map: list[tuple[str, str]] = [
        ("agents", "agent"),
        ("skills", "skill"),
        ("mcps", "mcp"),
        ("prompts", "prompt"),
        ("templates", "template"),
        ("workflows", "workflow"),
    ]
    for index_key, kind in type_key_map:
        entries = index_data.get(index_key, [])
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            item_id = str(entry.get("name", "")).strip()
            if not item_id:
                continue
            items.append(
                {
                    "id": item_id,
                    "name": item_id,
                    "description": _clean_frontmatter_text(str(entry.get("description", ""))),
                    "kind": kind,
                    "status": "available",
                    "enabled": False,
                    "installed": False,
                    "version": str(entry.get("version", "0.1.0")),
                    "tags": entry.get("tags", []) if isinstance(entry.get("tags"), list) else [],
                    "source_url": f"{marketplace_base_url}/{entry.get('file', '')}" if entry.get("file") else None,
                }
            )
    return items


async def _apply_frontmatter_to_item(item: dict, session: aiohttp.ClientSession) -> dict:
    source_url = item.get("source_url")
    if not isinstance(source_url, str) or not source_url:
        return item

    try:
        async with session.get(source_url) as response:
            response.raise_for_status()
            raw_body = await response.text()
        metadata: dict[str, object] = {}
        try:
            post = frontmatter.loads(raw_body)
            metadata = post.metadata if isinstance(post.metadata, dict) else {}
        except Exception:
            metadata = _parse_loose_frontmatter(raw_body)

        item["name"] = _clean_frontmatter_text(metadata.get("name"), fallback=item["id"])
        item["description"] = _clean_frontmatter_text(
            metadata.get("description"),
            fallback=item.get("description", ""),
        )

        tags = metadata.get("tags")
        if isinstance(tags, list):
            item["tags"] = [str(tag).strip() for tag in tags if str(tag).strip()]
    except Exception as error:
        log.debug("Frontmatter parse failed for %s: %s", source_url, error)

    return item


async def _enrich_items_with_frontmatter(items: list[dict]) -> list[dict]:
    if not items:
        return items

    timeout = aiohttp.ClientTimeout(total=20)
    connector = aiohttp.TCPConnector(limit=12, limit_per_host=6)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        return await asyncio.gather(*(_apply_frontmatter_to_item(item, session) for item in items))


async def _list_marketplace_items_fallback(
    *,
    kind: MarketplaceItemType | None,
    provider: str | None,
    installed_only: bool,
    enabled_only: bool,
    page: int,
    per_page: int,
) -> dict:
    items = await _build_index_items()
    if kind:
        items = [item for item in items if item["kind"] == kind.value]
    if provider:
        items = [item for item in items if (item.get("meta") or {}).get("provider") == provider]
    if installed_only:
        items = [item for item in items if item["installed"]]
    if enabled_only:
        items = [item for item in items if item["enabled"]]

    total = len(items)
    offset = (page - 1) * per_page
    paged_items = items[offset : offset + per_page]
    paged_items = await _enrich_items_with_frontmatter(paged_items)
    return {
        "items": paged_items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "source": "index_fallback",
    }


@router.post("/items/install", response_model=dict)
@router.post("/install", response_model=dict)
async def install_item(request: dict) -> dict:
    """Install a marketplace item.

    The installer will:
    1. Download the item from source URL (or marketplace CDN)
    2. Verify integrity (checksums, signatures)
    3. Extract to appropriate location
    4. Register with local registry
    5. Return installation path
    """
    from css.core.marketplace.installer import PackageInstaller

    try:
        item_id = str(request.get("item_id", "")).strip()
        if not item_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="item_id is required",
            )

        installer = PackageInstaller()
        result = await installer.install_package(
            item_id=item_id,
        )

        if result.success:
            return {
                "success": True,
                "item_id": item_id,
                "message": f"Successfully installed {item_id}",
                "installed_path": result.install_path,
            }
        else:
            return {
                "success": False,
                "item_id": item_id,
                "message": "Installation failed",
                "error": result.error or "Unknown error",
            }
    except Exception as e:
        log.warning("Install endpoint error (DB fallback): %s", e)
        if _db_not_ready(e):
            item_id = str(request.get("item_id", "")).strip()
            if not item_id:
                return {
                    "success": False,
                    "item_id": "",
                    "message": "Installation failed",
                    "error": "item_id is required",
                }
            return await _install_item_sql(item_id=item_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Installation failed: {str(e)}",
        )


@router.post("/items/uninstall", response_model=dict)
@router.post("/uninstall", response_model=dict)
async def uninstall_item(request: dict) -> dict:
    """Uninstall a marketplace item.

    The uninstaller will:
    1. Check for item existence
    2. Disable the item (if not already disabled)
    3. Remove installation files
    4. Optionally remove configuration
    5. Deregister from registry
    """
    from css.core.marketplace.installer import PackageInstaller

    try:
        item_id = str(request.get("item_id", "")).strip()
        if not item_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="item_id is required",
            )

        installer = PackageInstaller()
        result = await installer.uninstall_package(
            item_id=item_id,
        )

        if result.success:
            return {
                "success": True,
                "item_id": item_id,
                "message": f"Successfully uninstalled {item_id}",
            }
        else:
            return {
                "success": False,
                "item_id": item_id,
                "message": "Uninstallation failed",
                "error": result.error or "Unknown error",
            }
    except Exception as e:
        log.warning("Uninstall endpoint error (DB fallback): %s", e)
        if _db_not_ready(e):
            item_id = str(request.get("item_id", "")).strip()
            if not item_id:
                return {
                    "success": False,
                    "item_id": "",
                    "message": "Uninstallation failed",
                    "error": "item_id is required",
                }
            return await _uninstall_item_sql(item_id=item_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Uninstallation failed: {str(e)}",
        )


@router.post("/items/toggle", response_model=dict)
@router.post("/toggle", response_model=dict)
async def toggle_item(request: dict) -> dict:
    """Toggle enabled state of a marketplace item."""
    try:
        item_id = str(request.get("item_id", "")).strip()
        if not item_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="item_id is required",
            )
        enabled = bool(request.get("enabled"))

        item = await MarketplaceItem.get_or_none(slug=item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item not found: {item_id}",
            )

        if enabled:
            item.status = (
                MarketplaceItemStatus.installed
                if item.installed_at is not None
                else MarketplaceItemStatus.enabled
            )
        else:
            item.status = MarketplaceItemStatus.disabled

        await item.save()
        await emit_marketplace_item_changed(item_slug=item.slug, operation="toggle")

        return {
            "success": True,
            "item_id": item_id,
            "enabled": enabled,
            "message": f"Item {'enabled' if enabled else 'disabled'} successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        log.warning("Toggle endpoint error (DB fallback): %s", e)
        if _db_not_ready(e):
            item_id = str(request.get("item_id", "")).strip()
            if not item_id:
                return {
                    "success": False,
                    "item_id": "",
                    "enabled": bool(request.get("enabled")),
                    "message": "Toggle failed",
                    "error": "item_id is required",
                }
            return await _toggle_item_sql(item_id=item_id, enabled=bool(request.get("enabled")))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Toggle failed: {str(e)}",
        )


@router.post("/items/upgrade", response_model=dict)
@router.post("/upgrade", response_model=dict)
async def upgrade_item(request: dict) -> dict:
    """Upgrade a marketplace item.

    Currently not implemented.
    """
    item_id = str(request.get("item_id", "")).strip() or "<unknown>"
    log.warning(f"Upgrade requested for {item_id} but not yet implemented")
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Marketplace item upgrade is not yet implemented",
    )


@router.get("/items", response_model=dict)
async def list_marketplace_items(
    kind: MarketplaceItemType | None = Query(None, description="Filter by kind (agents, skills, mcp)"),
    provider: str | None = Query(None, description="Filter by provider"),
    installed_only: bool = Query(False, description="Show only installed items"),
    enabled_only: bool = Query(False, description="Show only enabled items"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
) -> dict:
    """List all marketplace items with optional filtering.

    Returns paginated list of marketplace items with metadata.
    """
    try:
        items = []

        # Build query
        query = MarketplaceItem.all()

        if kind:
            query = query.filter(kind=kind)

        if installed_only:
            query = query.filter(installed_at__not_isnull=True)
        if enabled_only:
            query = query.exclude(status=MarketplaceItemStatus.disabled)

        # Execute query + pagination
        offset = (page - 1) * per_page
        total = await query.count()
        results = await query.offset(offset).limit(per_page)

        # Format items
        for item in results:
            item_dict = {
                "id": item.slug,
                "name": item.name,
                "description": item.description,
                "kind": item.kind,
                "status": item.status,
                "enabled": item.status != MarketplaceItemStatus.disabled,
                "installed": item.installed_at is not None,
                "version": item.version,
                "tags": item.meta.get("tags", []) if item.meta else [],
            }
            # Add kind-specific fields from meta
            if item.meta:
                if item.kind == MarketplaceItemType.agent and "model" in item.meta:
                    item_dict["model"] = item.meta["model"]
                if item.kind == MarketplaceItemType.agent and "max_turns" in item.meta:
                    item_dict["max_turns"] = item.meta["max_turns"]
                if item.kind == MarketplaceItemType.mcp and "tools_count" in item.meta:
                    item_dict["tools_count"] = item.meta["tools_count"]
                if item.kind == MarketplaceItemType.skill and "repository_url" in item.meta:
                    item_dict["repository_url"] = item.meta["repository_url"]

            if provider and (item.meta or {}).get("provider") != provider:
                continue
            items.append(item_dict)

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    except Exception as e:
        log.warning("List items endpoint error (DB fallback): %s", e)
        if _db_not_ready(e):
            try:
                return await _list_items_sql(
                    kind=kind,
                    provider=provider,
                    installed_only=installed_only,
                    enabled_only=enabled_only,
                    page=page,
                    per_page=per_page,
                )
            except Exception as sql_error:
                log.warning("Marketplace SQL list fallback failed: %s", sql_error)
            return await _list_marketplace_items_fallback(
                kind=kind,
                provider=provider,
                installed_only=installed_only,
                enabled_only=enabled_only,
                page=page,
                per_page=per_page,
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Listing failed: {str(e)}",
        )


@router.get("/items/{item_id}", response_model=dict)
async def get_marketplace_item(item_id: str) -> dict:
    """Get details for a specific marketplace item.

    Returns full metadata, installation status, version info, etc.
    """
    try:
        # Convert kebab-case to title case for search
        title_case = " ".join(w.capitalize() for w in item_id.split("-"))

        # Try to find in MarketplaceItem
        item = await MarketplaceItem.get_or_none(name=title_case)

        if not item:
            item = await MarketplaceItem.get_or_none(slug=item_id)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item not found: {item_id}",
            )

        return {
            "item": {
                "id": item.slug,
                "name": item.name,
                "description": item.description,
                "kind": item.kind,
                "status": item.status,
                "enabled": item.status != MarketplaceItemStatus.disabled,
                "installed": item.installed_at is not None,
                "version": item.version,
                "tags": item.meta.get("tags", []) if item.meta else [],
                "installed_at": item.installed_at.isoformat() if item.installed_at else None,
                "source_url": item.source_url,
                "install_path": item.install_path,
                "meta": item.meta,
            },
            "found": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        log.warning("Get item endpoint error (DB fallback): %s", e)
        if _db_not_ready(e):
            try:
                item = await _get_item_sql(item_id=item_id)
                if item is not None:
                    return {"item": item, "found": True, "source": "sql_fallback"}
            except Exception as sql_error:
                log.warning("Marketplace SQL get fallback failed: %s", sql_error)
            fallback_items = await _build_index_items()
            item = next((entry for entry in fallback_items if entry["id"] == item_id), None)
            if item is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item not found: {item_id}",
                )
            item = (await _enrich_items_with_frontmatter([item]))[0]
            return {"item": item, "found": True, "source": "index_fallback"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval failed: {str(e)}",
        )

@router.get("/items/{item_id}/preview", response_model=dict)
async def get_marketplace_item_preview(item_id: str) -> dict:
    """Return installed markdown content for preview overlay."""
    try:
        item = await MarketplaceItem.get_or_none(slug=item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item not found: {item_id}",
            )
        if item.installed_at is None or not item.install_path:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Preview available only after installation",
            )
        preview_path = _resolve_preview_file(item.install_path)
        if preview_path is None:
            markdown_text = _generated_preview_markdown(
                item_id=item.slug,
                name=item.name,
                description=item.description,
                kind=str(item.kind.value if hasattr(item.kind, "value") else item.kind),
            )
            install_path = str(_resolve_preview_path(item.install_path))
        else:
            markdown_text = _normalize_markdown_preview(preview_path.read_text(encoding="utf-8"))
            install_path = str(preview_path)
        return {
            "item_id": item_id,
            "markdown": markdown_text,
            "install_path": install_path,
        }
    except HTTPException:
        raise
    except Exception as e:
        log.warning("Marketplace preview endpoint error (DB fallback): %s", e)
        if _db_not_ready(e):
            item = await _get_item_sql(item_id=item_id)
            if item is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item not found: {item_id}",
                )
            install_path = str(item.get("install_path") or "").strip()
            if not item.get("installed") or not install_path:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Preview available only after installation",
                )
            preview_path = _resolve_preview_file(install_path)
            if preview_path is None:
                markdown_text = _generated_preview_markdown(
                    item_id=item_id,
                    name=str(item.get("name") or item_id),
                    description=str(item.get("description") or ""),
                    kind=str(item.get("kind") or "unknown"),
                )
                resolved_install_path = str(_resolve_preview_path(install_path))
            else:
                markdown_text = _normalize_markdown_preview(preview_path.read_text(encoding="utf-8"))
                resolved_install_path = str(preview_path)
            return {
                "item_id": item_id,
                "markdown": markdown_text,
                "install_path": resolved_install_path,
                "source": "sql_fallback",
            }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview failed: {str(e)}",
        )


@router.get("/items/by-tags", response_model=dict)
@router.get("/tags", response_model=dict)
async def list_items_by_tags(
    tags: str = Query(..., description="Comma-separated tag slugs, e.g. 'python,security'"),
    kind: MarketplaceItemType | None = Query(None),
    match_all: bool = Query(False, description="True = item must have ALL tags; False = ANY tag"),
) -> dict:
    """Filter marketplace items by one or more tags.

    Query params:
    - **tags**: comma-separated tag slugs, e.g. ``python,security``
    - **kind**: optional item type filter
    - **match_all**: if True items must carry ALL supplied tags; default is ANY

    Returns:
        ``{"items": [...], "count": int}``
    """
    from css.core.marketplace.cache import marketplace_cache

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    cache_key = f"tags:{','.join(sorted(tag_list))}:{kind or 'any'}:{match_all}"
    cached = marketplace_cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        query = MarketplaceItem.all()
        if kind:
            query = query.filter(kind=kind)

        all_items = await query
        results = []
        for item in all_items:
            item_tags = set(item.meta.get("tags", []) if item.meta else [])
            tag_set = set(tag_list)
            if match_all:
                matched = tag_set.issubset(item_tags)
            else:
                matched = bool(tag_set & item_tags)

            if matched:
                results.append({
                    "id": item.slug,
                    "name": item.name,
                    "kind": item.kind,
                    "status": item.status,
                    "tags": list(item_tags),
                    "version": item.version,
                })

        response = {"items": results, "count": len(results)}
        marketplace_cache.set(cache_key, response)
        return response

    except Exception as e:
        log.warning("Tags filter error (DB fallback): %s", e)
        if _db_not_ready(e):
            fallback_items = await _build_index_items()
            tag_set = set(tag_list)
            results = []
            for item in fallback_items:
                if kind and item["kind"] != kind.value:
                    continue
                item_tags = set(item.get("tags", []))
                matched = tag_set.issubset(item_tags) if match_all else bool(tag_set & item_tags)
                if matched:
                    results.append(item)
            return {"items": results, "count": len(results), "source": "index_fallback"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tag filter failed: {str(e)}",
        )


@router.get("/status", response_model=dict)
async def marketplace_status() -> dict:
    """Get marketplace metadata and aggregate item status."""
    try:
        total_items = await MarketplaceItem.all().count()
        installed_items = await MarketplaceItem.filter(installed_at__not_isnull=True).count()
        enabled_items = await MarketplaceItem.exclude(status=MarketplaceItemStatus.disabled).count()
        meta = await MarketplaceMeta.get_or_none(id=1)

        return {
            "total_items": total_items,
            "installed_items": installed_items,
            "enabled_items": enabled_items,
            "update_available": bool(meta.update_available) if meta else False,
            "last_index_check": meta.last_index_check.isoformat() if meta and meta.last_index_check else None,
            "remote_index_hash": meta.remote_index_hash if meta else None,
            "local_index_hash": meta.local_index_hash if meta else None,
            "version": meta.version if meta else None,
        }
    except Exception as e:
        log.warning("Marketplace status endpoint error (DB fallback): %s", e)
        if _db_not_ready(e):
            try:
                return await _status_sql()
            except Exception as sql_error:
                log.warning("Marketplace SQL status fallback failed: %s", sql_error)
            fallback_items = await _build_index_items()
            return {
                "total_items": len(fallback_items),
                "installed_items": 0,
                "enabled_items": 0,
                "update_available": False,
                "last_index_check": None,
                "remote_index_hash": None,
                "local_index_hash": None,
                "version": None,
                "source": "index_fallback",
            }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check failed: {str(e)}",
        )


@router.post("/update-check", response_model=dict)
async def marketplace_update_check() -> dict:
    """Trigger immediate marketplace update check against remote index."""
    try:
        async with MarketplaceSeeder() as seeder:
            version = await seeder.check_for_updates()
        meta = await MarketplaceMeta.get_or_none(id=1)
        return {
            "update_available": bool(meta.update_available) if meta else False,
            "version": version or (meta.version if meta else None),
            "remote_index_hash": meta.remote_index_hash if meta else None,
            "local_index_hash": meta.local_index_hash if meta else None,
        }
    except Exception as e:
        log.warning("Marketplace update-check endpoint error (DB fallback): %s", e)
        if _db_not_ready(e):
            index_items = await _build_index_items()
            return {
                "update_available": False,
                "version": None,
                "remote_index_hash": None,
                "local_index_hash": None,
                "source": "index_fallback",
                "total_items": len(index_items),
            }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Update check failed: {str(e)}",
        )


@router.post("/reseed", response_model=dict)
async def marketplace_reseed(force: bool = Query(True, description="Force reseed even if items exist")) -> dict:
    """Reseed marketplace items from remote index."""
    try:
        async with MarketplaceSeeder() as seeder:
            created, skipped = await seeder.seed_if_empty(force=force)
        return {
            "success": True,
            "created": created,
            "skipped": skipped,
            "force": force,
        }
    except Exception as e:
        log.warning("Marketplace reseed endpoint error (DB fallback): %s", e)
        if _db_not_ready(e):
            fallback_items = await _build_index_items()
            return {
                "success": True,
                "created": len(fallback_items),
                "skipped": 0,
                "force": force,
                "source": "index_fallback",
            }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reseed failed: {str(e)}",
        )
